# Checklista składu v9 (globalne poprawki redakcyjne — ręcznie w Overleafie)

> Rozłączna z `rozdzial4_instrukcje.md` (tam: podmiany treści rozdz. 4).
> Po składzie: eksport `Praca Magisterska-9.pdf` do root repo → pętla
> `ml-learing-center/.venv/bin/python ml-learing-center/validate_thesis.py
> "../Praca Magisterska-9.pdf"` aż do exit 0.

## Struktura / spis treści

- [ ] Wstawić `rozdzial3.tex` jako treść rozdziału 3 (sekcje 3.1–3.6; obecnie
      same śródtytuły). Uwaga: draft ma dodatkową podsekcję 3.3.4 (panel
      sliding-window) i 3.3.5 (podział) — TOC zaktualizuje się automatycznie.
- [ ] Wstawić `rozdzial4_nowe_sekcje.tex` po sekcji 4.5 (nowe 4.6/4.7/4.8).
- [ ] Wstawić `rozdzial5.tex` jako treść rozdziału 5 + `zakonczenie.tex`.
- [ ] TOC 5.2: dodać podsekcje 5.2.4 (LightGBM) i 5.2.5 (CatBoost) — lub, przy
      strukturze z draftu, 5.2 bez podsekcji per model (opis łączny) — wybrać
      jedno i konsekwentnie.
- [ ] TOC/nagłówek 5.3: „Wzajemne porównanie modeli LSTM, Random Forest
      i XGBoost" → „Wzajemne porównanie pięciu modeli".
- [ ] Odświeżyć numery stron TOC dla rozdz. 3 (obecnie wszystkie „23").

## Relikty w istniejącym tekście (poza rozdz. 4)

- [ ] Sekcja 2.1.1: „trzy badane algorytmy" → „pięć badanych algorytmów".
- [ ] Sekcja 2.3.4 (LightGBM): wyrównać formatowanie do reszty (obecnie inne
      wyjustowanie); nagłówek „2.4." pojawia się na stronie PRZED 2.3.5 —
      naprawić kolejność.
- [ ] Wstęp-roadmapa: sprawdzić, że zapowiedzi („kalibracja prawdopodobieństw
      oraz wyznaczenie progów alertu", „audyt fairness") mają teraz pokrycie —
      zostają bez zmian.

## Figury

- [ ] Podmienić rys. 4.1/4.3/4.5/4.6/4.7/4.8 wg tabeli w `rozdzial4_instrukcje.md`.
- [ ] **Zamienione podpisy 4.3 ↔ 4.4 w v8**: po podmianie 4.3 na krzywe uczenia
      sprawdzić, że rys. 4.4 (panele hiperparametrów LSTM) ma właściwy podpis
      „Wpływ hiperparametrów LSTM na AUC walidacji".
- [ ] Rys. 4.2 (SMOTE): zostaje jako analiza alternatyw — podpis bez zmian.
- [ ] Rys. 4.9 (schemat 5-fold CV): zostaje (schemat); tekst 4.4.1 po podmianie
      Z5 odwołuje się do niego jako ilustracji procedury Optuny.
- [ ] Wstawić figury rozdz. 5 wg `FIGURY.md` (ROC/PR/kalibracja, static-vs-dynamic,
      pd-per-window, fairness 5.10, bootstrap).
- [ ] Wszystkie PNG w 300 DPI z `thesis_figures/output/` lub `reports/`
      (mapa: `FIGURY.md`).

## Bibliografia

- [ ] Dopisać pozycje z `bibliografia_nowe.tex` jako [32]–[36] (kontynuacja
      numeracji); w tekście draftów cytowania już są (`\cite{...}`).
- [ ] Zaktualizować „Spis tabel" (nowe tabele: mapowanie kolumn, okna W0..W3,
      metryki 5 modeli, bootstrap, static-vs-dynamic, fairness) i „Spis
      rysunków".

## Sanity końcowe (przed eksportem)

- [ ] Zdania-obietnice mają pokrycie: bootstrap (tak — 5.3), kalibracja (4.6),
      progi (4.7), fairness (5.5b).
- [ ] Żadna liczba nie pochodzi „z głowy": źródło = tabele draftów (zgodne
      z `reports/*.csv` na commit 2026-07-07).
- [ ] Eksport → `Praca Magisterska-9.pdf` → walidator → iteracja do 16/16 🟢.
