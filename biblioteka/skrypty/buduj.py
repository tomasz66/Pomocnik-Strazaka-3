"""Buduje bibliotekę kierowcy SCD-42: biblioteka/scd42.json + obrazy stron, kontrolek i zdjęć ze szkolenia."""
import fitz, io, json, os, sys
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
from tekst import d as MANUAL, page_paras

SRC = '/Users/tomekmusialik/Claude Code Tom/Pomocnik-Strazaka-3/Pomocnik Strażaka Załączniki/'
OUT = '/Users/tomekmusialik/Claude Code Tom/Pomocnik-Strazaka-3/biblioteka/'
IMG = OUT + 'scd42/'

PAGE_DPI = 120        # w szarości nadal czytelne po powiększeniu
JPEG_Q = 55
PHOTO_MAX = 1200
KONTROLKI_DPI = 260   # skany mają drobne podpisy pod ikonami
FIG_MIN_W, FIG_MIN_H = 90, 60   # mniejsze obrazki to ikonki ostrzeżeń, nie rysunki
FIG_MIN_DRAWINGS = 30           # rysunek wektorowy (wykres, wymiary) bez zdjęcia
USTERKI_PAGES = set(range(193, 198))  # do nich linkują karty usterek

# Strony 1-10 to okładka i spis treści; 91-100 i 228-237 dotyczą innych modeli (M27/M32/M39)
FIRST_PAGE = 11
OTHER_MODELS = set(range(91, 101)) | set(range(228, 238))


def save_jpeg(img, path, q=JPEG_Q, max_w=None, gray=True):
    img = img.convert('L' if gray else 'RGB')
    if max_w and img.width > max_w:
        img = img.resize((max_w, int(img.height * max_w / img.width)), Image.LANCZOS)
    img.save(path, 'JPEG', quality=q, optimize=True, progressive=True)


# Obraz strony zapisujemy tylko, gdy ma rysunek - sam tekst jest już w czytniku
def has_figure(page):
    for im in page.get_images():
        for r in page.get_image_rects(im[0]):
            if r.width > FIG_MIN_W and r.height > FIG_MIN_H:
                return True
    return len(page.get_drawings()) > FIG_MIN_DRAWINGS


def pix_to_img(pix):
    return Image.open(io.BytesIO(pix.tobytes('png')))


# ── Instrukcja: podrozdziały wg nagłówka strony ──
import shutil
shutil.rmtree(IMG, ignore_errors=True)
os.makedirs(IMG + 'strony', exist_ok=True)
sections = []
for pno in range(FIRST_PAGE - 1, MANUAL.page_count):
    page_no = pno + 1
    if page_no in OTHER_MODELS:
        continue
    ch, title, paras = page_paras(pno)
    if not ch or not title:
        ch, title = sections[-1]['rozdzial'], sections[-1]['tytul']
    if not sections or (sections[-1]['rozdzial'], sections[-1]['tytul']) != (ch, title) or sections[-1]['strony'][-1]['nr'] != page_no - 1:
        sections.append({'id': 'r%d' % page_no, 'rozdzial': ch, 'tytul': title, 'strony': []})
    entry = {'nr': page_no, 'a': paras}
    if page_no in USTERKI_PAGES or has_figure(MANUAL[pno]):
        save_jpeg(pix_to_img(MANUAL[pno].get_pixmap(dpi=PAGE_DPI)), IMG + 'strony/s%03d.jpg' % page_no)
        entry['img'] = 1
    sections[-1]['strony'].append(entry)

# ── Kontrolki: skany stron (tylko do podglądu) ──
os.makedirs(IMG + 'kontrolki', exist_ok=True)
KONTROLKI_OPIS = [
    ('Symbole - kabina, podpory, stanowisko, drabina', 'Spis symboli: kabina kierowcy, układ elektryczny, podpory, stanowisko obsługi, zespół drabiny, przyciski funkcyjne, tryb awaryjny, łączność radiowa, ruchy drabiną, instalacja elektryczna, podwozie i napęd.'),
    ('Kontrolki drabiny i kosza + pulpit w kabinie', 'Uderzenia, obciążenie kosza, praca wolnostojąca. Pulpit w kabinie kierowcy A-R: lampy stroboskopowe, oświetlenie pola pracy, światła ostrzegawcze, przystawka odbioru mocy, licznik motogodzin, kontrolka Podpory, hamulec ręczny, poziomica.'),
    ('Wyświetlacz stanowiska sterowania', 'Wyświetlacz z wskaźnikami: korygowanie nierówności, wyrównywanie szczebli, oświetlenie, silnik, zmiana menu, wskaźniki obciążenia i wysięgu, wartości MAX i AKT.'),
    ('Kontrolki LED i przyciski funkcyjne', 'Gotowość do pracy i ciśnienie oleju, obciążenie drabiny wolnostojącej zabronione, przeciążenie - wsunąć drabinę, pomost, korygowanie nierówności, pokrycie szczebli, oświetlenie, silnik, menu.'),
    ('Kontrolki drabiny, składanie automatyczne, praca z pamięcią', 'Opisy kontrolek A-K: wiatr, tryb szybki/wolny, uderzenie, dźwignie w pozycji neutralnej, praca jako dźwig, obciążenie kosza. Automatyczne składanie do pozycji transportowej i praca z pamięcią.'),
    ('Elementy obsługi w koszu', 'Stanowisko sterowania w koszu, gniazda 400 V i 230 V, uchwyty do zabezpieczenia, poręcze, drzwi, intercom, pedał czuwaka, światło przednie.'),
    ('Tabela usterek', 'Zakłócenia przed rozpoczęciem pracy, w czasie pracy, po zakończeniu pracy i podczas jazdy - przyczyny i sposób usuwania.'),
    ('Wymiary i dane techniczne M 42 L', 'Wymiary drabiny M 42 L z koszem RC 300 na podwoziu Iveco, dane drabiny, kosza, podpór, hydrauliki i warunki użytkowania.'),
]
kdoc = fitz.open(SRC + 'Kontrolki_Magirus.pdf')
kontrolki = []
for i, page in enumerate(kdoc):
    save_jpeg(pix_to_img(page.get_pixmap(dpi=KONTROLKI_DPI)), IMG + 'kontrolki/k%d.jpg' % (i + 1), q=60)
    kontrolki.append({'img': 'k%d.jpg' % (i + 1), 'tytul': KONTROLKI_OPIS[i][0], 'opis': KONTROLKI_OPIS[i][1]})

# ── Szkolenie: notatki Tomka + zdjęcia z dopiskami ──
notes_doc = fitz.open(SRC + 'Magirus szkolenie.pdf')
notatki = [l.strip() for l in ''.join(p.get_text() for p in notes_doc).split('\n') if l.strip()]
notatki = [l for l in notatki if l != 'Magirus szkolenie']

os.makedirs(IMG + 'szkolenie', exist_ok=True)
ZDJECIA = {  # strona PDF -> opis (z czerwonych dopisków na zdjęciach)
    1: 'Kontrolki na desce rozdzielczej (zaznaczone na szkoleniu)',
    2: 'Pulpit podpór: kontrolka musi świecić przy obecności ratowników',
    3: 'Zawory podpór: 1 - zwolnienie lin blokady resorów',
    4: 'Pole pracy drabiny (wysokość i wysięg)',
    5: 'Poziomica pochylenia bocznego pojazdu',
    6: 'ZAWSZE wyłączamy automatyczne poziomowanie wieńca. Precyzyjne manewrowanie (2 cm mogą być edytowane przez drabinę do 20 cm). Linie z prądem: odległość min. 1,5 m od linii - minimum 2 długości izolatora - izolator ma 2 m - bezpieczna odległość 4 m',
    7: 'Przed przystąpieniem do pracy: ustawienie talerzy podpór na różnym podłożu (studzienka, krawężnik, podkłady)',
    8: 'Wykres ze szkolenia',
    9: 'Wyłączyć poziomowanie kosza i włączyć żółwia - musi być włączone',
    10: 'Włączanie trybu awaryjnego (przełącznik przy fotelu operatora)',
    11: 'Wyświetlacz: TEST PRAWIDŁOWY - GOTOWOŚĆ DO PRACY, WYŁĄCZONE PIONOWANIE, ZREDUKOWANE PRĘDKOŚCI, OPUŚCIĆ',
}
fdoc = fitz.open(SRC + 'Magirus_szkolenie_foto.pdf')
zdjecia = []
for nr, opis in ZDJECIA.items():
    xref = fdoc[nr - 1].get_images()[0][0]
    img = pix_to_img(fitz.Pixmap(fdoc, xref))
    save_jpeg(img, IMG + 'szkolenie/f%02d.jpg' % nr, q=62, max_w=PHOTO_MAX, gray=False)
    zdjecia.append({'img': 'f%02d.jpg' % nr, 'opis': opis})

usterki = json.load(open(os.path.join(os.path.dirname(__file__), 'usterki_recznie.json')))

data = {
    'zrodlo': 'Instrukcja obsługi Magirus M 27 L - M 42 L (Iveco Magirus, 01-2012) + notatki i zdjęcia ze szkolenia',
    'usterki': usterki,
    'rozdzialy': sections,
    'kontrolki': kontrolki,
    'szkolenie': {'notatki': notatki, 'zdjecia': zdjecia},
}
with open(OUT + 'scd42.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, separators=(',', ':'))

print('podrozdziałów:', len(sections), 'stron:', sum(len(s['strony']) for s in sections),
      'z obrazem:', sum(1 for s in sections for st in s['strony'] if st.get('img')))
print('usterek:', len(usterki), 'kontrolek:', len(kontrolki), 'notatek:', len(notatki), 'zdjęć:', len(zdjecia))
