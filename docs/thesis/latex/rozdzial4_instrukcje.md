# Rozdział 4 — instrukcje podmian w ISTNIEJĄCEJ treści (Overleaf)

> Wyłącznie zmiany w istniejących sekcjach 4.1–4.5. Nowe sekcje 4.6/4.7/4.8 —
> gotowe w `rozdzial4_nowe_sekcje.tex` (wstawić po 4.5). Pełne teksty zamienne
> poniżej pochodzą z `docs/thesis/Rozdzial4_poprawki.md` (część A).

## Z1 — intro rozdziału 4 (s. ~23 v8)

**ZNAJDŹ:** „W ramach pracy zaimplementowano trzy różne klasyfikatory
reprezentujące odmienne rodziny algorytmiczne: Random Forest (…) oraz LSTM
(rekurencyjną sieć neuronową). Dwa pierwsze operują (…)"
**ZASTĄP:** akapitem „W ramach pracy zaimplementowano pięć klasyfikatorów…"
(pełny tekst: Rozdzial4_poprawki.md §A.1). Kluczowe: pięć modeli; dynamika =
przede wszystkim schemat oceny W0..W3, nie architektura LSTM.

## Z2 — sekcja 4.1.1 (podział zbioru)

**ZNAJDŹ:** cały opis 70/30 od „Pełny zbiór UCI (…) liczy 30 000 rekordów.
W pierwszym kroku wydzielono z niego zbiór testowy o udziale 30%…" do snippetu
`train_test_split(X_scaled, y, test_size=0.3, …)` włącznie.
**ZASTĄP:** tekstem „Finalny protokół walidacji opiera się na trójdzielnym,
stratyfikowanym podziale 60/20/20…" (pełny tekst: §A.2). Rysunek 4.1 → nowy
plik `fig_4_1_podzial_danych.png` (60/20/20).

## Z3 — sekcja 4.1.2 (niezbalansowanie)

**PO** istniejącym opisie class_weight/scale_pos_weight (zostaje!) **DOPISZ**
akapit „Ważenie klas poprawia ranking obserwacji, lecz celowo zniekształca
skalę prawdopodobieństw…" (pełny tekst: §A.3 — tandem ważenie+kalibracja,
odsyłacz do nowej sekcji 4.6).

## Z4 — sekcja 4.2.1 (LSTM)

**ZNAJDŹ:** „Wejście sieci ma wymiar (6, 3): sześć kroków czasowych…" (+ snippet
z `Input(shape=(6, 3))` jako jedyną architekturą).
**ZASTĄP:** tekstem „Sieć zaimplementowano w dwóch wariantach wejścia. Wariant
bazowy, 6-miesięczny, przyjmuje tensor (6, 3)… Wariant finalny (…) (3, 3)…"
(pełny tekst: §A.4). Dalej w 4.3.2 i sąsiednich: frazy „w sześciomiesięcznym
oknie", „w ilu z sześciu miesięcy", „między kwietniem a wrześniem" → „w oknie
obserwacji" / „w oknie 3-miesięcznym" (cechy parametryzowane oknem).

## Z5 — sekcja 4.4.1 (strojenie)

**ZNAJDŹ:** akapit „walidację krzyżową 5-fold zaprezentowano schematycznie,
natomiast do właściwej oceny modeli przyjęto pojedynczy, stratyfikowany podział
70/30…" (do końca uzasadnienia kosztowego).
**ZASTĄP:** tekstem „Hiperparametry przyjęte w implementacji wybrano
heurystycznie…, a następnie zweryfikowano systematycznie: strojenie Optuna
\cite{akiba2019} (TPESampler, 30 prób na model) z pięciokrotną stratyfikowaną
walidacją krzyżową…" (pełny tekst: §A.5). Rysunki 4.5/4.7 → nowe pliki
`fig_4_5_heatmapa_rf_cv.png` / `fig_4_7_heatmapa_xgb_cv.png` (CV-AUC na
treningu; podpisy: „CV-AUC (5-fold, zbiór treningowy)", NIE „AUC testu").

## Z6 — sekcja 4.5 (bootstrap)

**ZNAJDŹ:** „raportowana w rozdziale 5 wariancja AUC, obliczona na podstawie 40
bootstrapowanych powtórzeń zbioru testowego. Jeśli model jest stabilny…"
**ZASTĄP:** tekstem „Stabilność oceny na pojedynczym podziale zweryfikowano
bootstrapem: 40 repróbkowań zbioru testowego ze zwracaniem…" (pełny tekst:
§A.6 — obietnica ma teraz pokrycie w wynikach rozdz. 5.3).

## Podmiany figur (pliki z `ml-learing-center/thesis_figures/output/rozdzial_4/`)

| Rys. | Nowy plik | Uwaga |
|---|---|---|
| 4.1 | `fig_4_1_podzial_danych.png` | 60/20/20 (było 56/14/30) |
| 4.3 | `fig_4_3_krzywe_uczenia_lstm.png` | **w v8 podpisy 4.3↔4.4 były zamienione** — patrz checklista |
| 4.5 | `fig_4_5_heatmapa_rf_cv.png` | CV-AUC; ramka na (500, 10) zgodna z tekstem (stara ramka: depth=8) |
| 4.6 | `fig_4_6_feature_importance_rf.png` | z artefaktu W3 |
| 4.7 | `fig_4_7_heatmapa_xgb_cv.png` | CV-AUC; ramka (lr=0.02, depth=4) |
| 4.8 | `fig_4_8_shap_xgb.png` | globalny SHAP z artefaktu W3 |
