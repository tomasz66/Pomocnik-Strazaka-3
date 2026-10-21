# Biblioteka SCD-42 - jak przebudować

Źródła (PDF-y) leżą lokalnie w `Pomocnik Strażaka Załączniki/` i NIE trafiają na GitHub.

```
pip3 install pymupdf pillow
python3 biblioteka/skrypty/buduj.py
```

- `tekst.py` - wyciąga tekst instrukcji jako akapity (nagłówki, kroki →, listy)
- `usterki_recznie.json` - tabela usterek przepisana ręcznie ze stron 193-196
- `buduj.py` - składa `biblioteka/scd42.json` + obrazy stron, kontrolek i zdjęć ze szkolenia
