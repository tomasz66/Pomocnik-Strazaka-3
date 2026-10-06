import json,re,html,os
HERE=os.path.dirname(os.path.abspath(__file__))
s=open(os.path.join(HERE,'..','index.html'),encoding='utf-8').read()
a=s.find('id="app-data"'); a=s.find('>',a)+1; b=s.find('</script>',a)
d=json.loads(s[a:b]); G={g['id']:g for g in d['groups']}
STRIP=re.compile(r'\s*\((czujnik|czujka|czujnik, miernik|pilot|spodnie pilarza)\)')
def q(x):
    x=(x or '').strip(); m=re.fullmatch(r'(\d+) szt\.?',x)
    return m.group(1) if m else x
def nb(t): return re.sub(r'(?<=[\s])([aiouwzAIOUWZ]) ',r'\1 ',t)
# Strony: (wóz, podtytuł, nagłówki kolumn [(tytuł, ile kolumn)], skrytki w kolumnach)
PAGES=[
 ('v1','strona 1/2 · kabina i strona kierowcy',[('Kabina',1),('Strona kierowcy',2)],[['kab'],['k1'],['k2','k3']]),
 ('v1','strona 2/2 · strona dowódcy, tył, przód, dach',[('Strona dowódcy',2),('Tył · przód · dach',1)],[['d1'],['d2','d3'],['tyl','przod','dach']]),
 ('v2','strona 1/2 · kabina i strona kierowcy',[('Kabina',1),('Strona kierowcy',1)],[['kab'],['k1','k2','k3']]),
 ('v2','strona 2/2 · strona dowódcy, tył, przód, dach',[('Strona dowódcy',2),('Przód · tył · dach',1)],[['d1','d2'],['d3'],['przod','tyl','dach']]),
 ('v3','zawartość skrytek',[('Kabina · nadwozie',1),('Strona kierowcy',1),('Strona dowódcy',1)],[['kab','nad'],['k1','k2','k3','k4'],['d1','d2','d3','d4']]),
]
CSS='''@page{size:A4;margin:0}*{box-sizing:border-box}body{font-family:"Helvetica Neue",Arial,sans-serif;margin:0;color:#000}
section{width:210mm;height:297mm;padding:6mm;overflow:hidden;page-break-after:always;display:flex;flex-direction:column}
section:last-child{page-break-after:auto}
h1{font-size:14pt;margin:0 0 2mm;background:#000;color:#fff;padding:1.3mm 2.5mm}h1 small{font-size:8pt;font-weight:400}
.heads,.cols{display:grid;column-gap:2.5mm}.cols{align-items:start;flex:1}
.ct{font-size:1.05em;font-weight:700;text-transform:uppercase;letter-spacing:.3pt;border-bottom:1.5pt solid #000;margin-bottom:1.4mm;padding-bottom:.4mm}
.col{display:flex;flex-direction:column;gap:1.8mm}
.comp{border:1pt solid #000}
h2{margin:0;font-size:1.35em;background:#000;color:#fff;padding:.5mm 1.5mm;display:flex;justify-content:space-between;align-items:baseline}
h2 span{font-size:.65em;font-weight:400}
table{width:100%;border-collapse:collapse}td{padding:.1em 1.2mm;border-bottom:.4pt dotted #999;vertical-align:top;line-height:1.14}
td.q{text-align:right;white-space:nowrap;font-weight:700;width:1%}tr.g td{font-weight:700;background:#e6e6e6}tr.sub td:first-child{padding-left:3mm}'''
def comp_html(v,c):
    its=[it for it in d['items'] if it['v']==v and it['comp']==c['id']]
    if not its: return ''
    o=[f'<div class="comp"><h2>{c.get("label") or c["name"]}<span>{len(its)} poz.</span></h2><table>']
    seen=set()
    for it in sorted(its,key=lambda i:(i.get('group') or '', i['name'].lower())):
        g=it.get('group')
        if g and g not in seen:
            seen.add(g); o.append(f'<tr class="g"><td colspan=2>{html.escape(G[g]["name"])}</td></tr>')
        n=html.escape(nb(STRIP.sub('',it['name'])))
        o.append(f'<tr{" class=sub" if g else ""}><td>{n}</td><td class="q">{html.escape(q(it.get("qty")))}</td></tr>')
    o.append('</table></div>')
    return ''.join(o)
out=[]
for v,sub,heads,cols in PAGES:
    V=d['vehicles'][v]; C={c['id']:c for c in V['compartments']}; n=len(cols)
    out.append(f'<section><h1>{V["name"]} <small>{html.escape(V.get("sub",""))} · {sub}</small></h1>')
    out.append(f'<div class="heads" style="grid-template-columns:repeat({n},1fr)">'+''.join(f'<div class="ct" style="grid-column:span {sp}">{t}</div>' for t,sp in heads)+'</div>')
    out.append(f'<div class="cols" style="grid-template-columns:repeat({n},1fr)">')
    for col in cols:
        out.append('<div class="col">'+''.join(comp_html(v,C[cid]) for cid in col if cid in C)+'</div>')
    out.append('</div></section>')
open(os.path.join(HERE,'zawartosc-skrytek.html'),'w',encoding='utf-8').write(f'<!doctype html><html lang=pl><head><meta charset=utf-8><title>Ściąga - zawartość skrytek</title><style>{CSS}</style></head><body>'+''.join(out)+'</body></html>')
