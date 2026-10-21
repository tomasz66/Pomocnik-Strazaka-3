import fitz, re, json, sys
PDF='/Users/tomekmusialik/Claude Code Tom/Pomocnik-Strazaka-3/Pomocnik Strażaka Załączniki/! CS MAGIRUS instrukcja obsługi M 32 L M 39 L i M 42 L 2014 v2 .pdf'
d=fitz.open(PDF)

TOP=72        # nagłówek strony (rozdział + tytuł) - wyżej nie bierzemy
BOTTOM=790    # stopka z numerem strony
COL2_X=290    # prawa kolumna (rysunki i podpisy)
LABEL_RE=re.compile(r'^[A-Z]$|^\d{1,2}$')
BULLETS=('→','-','–','•')

SUPERSCRIPT=1  # flaga PyMuPDF: indeks górny

# Znak stopnia w PDF-ie to małe "0" w indeksie górnym zaraz po liczbie (np. 75 + ⁰ = 75°)
def line_text(spans):
    out=''
    for i,sp in enumerate(spans):
        t=sp['text']
        if i and t.strip() in ('0','o','O') and sp['flags'] & SUPERSCRIPT and out.rstrip()[-1:].isdigit():
            t='°'
        out+=t
    return out

def clean(s):
    s=re.sub(r'\s+',' ',s).strip()
    return s.replace(' ,',',').replace(' .','.')

def page_header(pno):
    lines=[l.strip() for l in d[pno].get_text().split('\n') if l.strip()]
    return lines[3] if len(lines)>3 else '', lines[4] if len(lines)>4 else ''

def page_paras(pno):
    page=d[pno]
    ch,title=page_header(pno)
    blocks=[]
    for b in page.get_text('dict')['blocks']:
        if 'lines' not in b: continue
        x0,y0=b['bbox'][0],b['bbox'][1]
        if y0<TOP or y0>BOTTOM: continue
        lines=[]
        for l in b['lines']:
            t=line_text(l['spans'])
            if not t.strip(): continue
            bold=all(('Bold' in s['font']) for s in l['spans'] if s['text'].strip())
            size=max(s['size'] for s in l['spans'] if s['text'].strip())
            lines.append((t.strip(),bold,size,l['bbox'][0]))
        if lines:
            blocks.append((0 if x0<COL2_X else 1, y0, lines))
    blocks.sort(key=lambda b:(b[0],b[1]))
    paras=[]
    for col,y,lines in blocks:
        cur=None
        for t,bold,size,x in lines:
            if t in (ch,title) and size>=10:
                continue
            starts_new = cur is None or t.startswith(BULLETS) or (cur and cur['t'] in ('h',)) \
                or (cur and LABEL_RE.match(cur['x']) is None and LABEL_RE.match(t) is not None)
            if cur and cur.get('pending'):
                cur['x']=clean(cur['x']+' '+t); cur['pending']=False
                continue
            if bold and not t.startswith(BULLETS) and (cur is None or not cur['bold']):
                starts_new=True
            # Pogrubiony śródtytuł, a pod nim zwykły tekst - to dwa osobne akapity
            if cur and cur['bold'] and not bold and cur['t']!='cap':
                starts_new=True
            if starts_new:
                kind='h' if (bold and size>=10) else 'p'
                if t.startswith('['): kind='cap'
                cur={'t':kind,'x':t,'bold':bold,'pending': t in BULLETS or bool(LABEL_RE.match(t))}
                paras.append(cur)
            else:
                cur['x']=clean(cur['x']+' '+t)
        if cur and cur['t']=='p' and cur['bold']: cur['t']='b'
    # Zdanie przecięte między blokami: kontynuacja zaczyna się małą literą
    merged=[]
    for p in paras:
        x=clean(p['x'])
        if merged and x[:1].islower() and p['t']!='cap':
            merged[-1]['x']=clean(merged[-1]['x']+' '+x)
            continue
        merged.append(p)
    paras=merged
    out=[]
    for p in paras:
        x=clean(p['x'])
        if not x or x in BULLETS: continue
        if x.startswith('→'): out.append(['s',x.lstrip('→ ').strip()])
        elif x[:1] in '-–•' : out.append(['li',x[1:].strip()])
        else: out.append([p['t'] if not (p['bold'] and p['t']=='p') else 'b',x])
    return ch,title,out

if __name__=='__main__':
    for pno in map(int,sys.argv[1:]):
        ch,title,out=page_paras(pno-1)
        print('=====',pno,ch,'/',title)
        for k,x in out: print(f'[{k}]',x)
