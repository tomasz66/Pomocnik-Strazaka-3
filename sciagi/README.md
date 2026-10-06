# Ściągi do druku (A4)

Papierowe wersje tego, co w aplikacji jest w ekranie **Karty pojazdów**.

| Plik | Co to jest |
|---|---|
| `Sciaga-zawartosc-skrytek-GBA-GCBA-SCD.pdf` | Gdzie co jest i ile - 5 stron: GBA 2, GCBA 2, SCD-42 1 (druk dwustronny) |
| `Sciaga-dane-techniczne-GBA-GCBA-SCD.pdf` | Dane techniczne - 2 strony: GBA + GCBA, SCD-42 + Garaż, przyczepki, zestawienie JRG |
| `gen-skrytki.py` | Buduje `zawartosc-skrytek.html` z danych w `../index.html` (zawsze aktualne) |
| `dane-techniczne.html` | Źródło ściągi z danymi technicznymi - pisane ręcznie, przy zmianach sprzętu trzeba poprawić ręcznie |
| `pdf-fit.js` | HTML -> PDF, sam dobiera największą czcionkę, przy której każda strona mieści się na A4 |
| `pdf.js` | HTML -> PDF bez dopasowania czcionki (do `dane-techniczne.html`) |

## Jak odświeżyć po zmianach sprzętu

Wymaga Pythona 3 oraz Node z pakietem `playwright` (`npm install playwright && npx playwright install chromium`).

```
python3 gen-skrytki.py
node pdf-fit.js "$PWD/zawartosc-skrytek.html" Sciaga-zawartosc-skrytek-GBA-GCBA-SCD.pdf
node pdf.js "$PWD/dane-techniczne.html" Sciaga-dane-techniczne-GBA-GCBA-SCD.pdf
```

Układ stron skrytek (które skrytki w której kolumnie) jest w `PAGES` w `gen-skrytki.py`.
Zasada: każda skrytka w całości w jednej kolumnie, kolejność jak na wozie
(kabina, strona kierowcy, strona dowódcy, tył/przód/dach).
