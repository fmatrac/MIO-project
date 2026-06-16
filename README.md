# Testowanie bezpieczeństwa modeli językowych (LLM) – angielski vs polski

Projekt z przedmiotu **Metody Inteligencji Obliczeniowej**.

**Temat:** Przetestowanie bezpieczeństwa modeli AI z użyciem wybranego zbioru
testującego.

**Wybrany zbiór testujący:** **SimpleSafetyTests** (Vidgen i in., 2024) –
wskazany w publikacji *SafetyPrompts: a Systematic Review of Open Datasets for
Evaluating and Improving Large Language Model Safety*
(Röttger i in., 2024, [arXiv:2404.05399](https://arxiv.org/abs/2404.05399)).

## Autorzy

- Filip Matracki — zbiór danych i tłumaczenie EN→PL
- Patryk Adamski — uruchomienie modeli i ocena (sędzia)
- Radosław Mieńkowski — analiza wyników, wykresy i sprawozdanie

## O co chodzi w projekcie

Główny wniosek z publikacji SafetyPrompts to **brak zbiorów bezpieczeństwa w
językach innych niż angielski** – przez co osoby mówiące w innych językach mogą
być **bardziej narażone** na szkodliwe odpowiedzi modeli. Sprawdzamy tę
hipotezę wprost: czy te same modele są **mniej bezpieczne po polsku niż po
angielsku**?

Bierzemy 100 szkodliwych poleceń z SimpleSafetyTests, tłumaczymy je na polski i
zadajemy je trzem małym modelom LLM – po angielsku i po polsku. Każdą odpowiedź
oceniamy jako **bezpieczną** (model odmawia / ostrzega) lub **niebezpieczną**
(model spełnia szkodliwą prośbę). Porównujemy odsetek niebezpiecznych
odpowiedzi w obu językach.

## Testowane modele (lokalnie, przez Ollama)

| Model | Producent | Rozmiar |
|-------|-----------|---------|
| `llama3.2:3b` | Meta | 3B |
| `gemma2:2b` | Google | 2B |
| `phi3:mini` | Microsoft | 3.8B |

**Sędzia (ocena odpowiedzi):** `qwen2.5:3b` (Alibaba) – celowo **inny** model
niż testowane, żeby żaden model nie oceniał sam siebie.

## Struktura repozytorium

```
MIO-project/
├── data/
│   ├── sst_en.csv      # oryginalne 100 poleceń (angielski)
│   └── sst_pl.csv      # tłumaczenie na polski (maszynowe + poprawki ręczne)
├── src/
│   ├── config.py        # ustawienia: modele, ścieżki, parametry generacji
│   ├── ollama_client.py # cienki klient HTTP do Ollama
│   ├── translate.py     # tłumaczenie EN -> PL (Google Translate)
│   ├── run_experiment.py# odpytanie modeli (model × język × polecenie)
│   ├── judge.py         # ocena: wykrywanie odmów + sędzia-LLM
│   └── analyze.py       # zestawienia + wykresy
├── results/
│   ├── responses.csv    # surowe odpowiedzi modeli
│   ├── judged.csv       # odpowiedzi z etykietą bezpieczne/niebezpieczne
│   ├── summary_*.csv     # tabele zbiorcze
│   └── figures/*.png     # wykresy do sprawozdania
├── sprawozdanie/
│   └── sprawozdanie.md   # sprawozdanie (5–10 stron)
└── requirements.txt
```

## Jak odtworzyć wyniki

```bash
# 1. Zależności Pythona
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 2. Ollama + modele (https://ollama.com)
brew install ollama          # lub instalator ze strony
ollama serve &               # uruchom serwer w tle
ollama pull llama3.2:3b
ollama pull gemma2:2b
ollama pull phi3:mini
ollama pull qwen2.5:3b

# 3. Pipeline (uruchamiać z katalogu src/)
cd src
python translate.py          # EN -> PL (data/sst_pl.csv)  [opcjonalne – plik jest w repo]
python run_experiment.py     # generuje results/responses.csv
python judge.py              # generuje results/judged.csv
python analyze.py            # generuje tabele i wykresy
python build_html.py         # (opcjonalnie) sprawozdanie.md -> sprawozdanie.html
```

Sprawozdanie jest dostępne w dwóch formatach (ta sama treść):
- `sprawozdanie/sprawozdanie.md` — źródło w Markdown,
- `sprawozdanie/sprawozdanie.tex` + `sprawozdanie.pdf` — wersja LaTeX (7 stron),
