# Design: Ścieżka do obrony — dwa równoległe tory (dokument + obrona/demo)

**Data:** 2026-07-07 · **Status:** zatwierdzony w brainstormingu
**Kontekst decyzji:** cel = „wszystko po kolei do obrony"; źródło pracy = LaTeX
poza repo (prawdopodobnie Overleaf — brak `.tex` w repo i ~/Documents);
demo na obronie = pełne, na żywo.

## Problem i cel

Kod i eksperymenty są domknięte (28/30 zadań CREDIT, testy zielone,
`FINAL_REPORT.md`, naprawy metodologiczne z 2026-07-07), ale **dokument pracy
(PDF v8) wciąż ma puste rozdziały 3 i 5 oraz Zakończenie**, mimo że pełne
drafty treści leżą w `docs/thesis/*.md` z liczbami zweryfikowanymi
z artefaktów. Celem etapu jest doprowadzenie do stanu „gotowy do obrony":
kompletna praca (v9) przechodząca automatyczną walidację, przygotowane
materiały obrony (Q&A, ściąga liczb), działające i przećwiczone demo
z planem awaryjnym.

Wybrane podejście: **B — dwa równoległe tory** (odrzucone: A sekwencyjne —
niezależne prace czekałyby na pętlę składu; C obrona-najpierw — odkładanie
integracji o 6 tygodni grozi rozjazdem wersji przy świeżych dziś liczbach).

## Tor 1 — dokument pracy → v9

**Deliverable: katalog `docs/thesis/latex/`** gotowy do wrzucenia do projektu
Overleaf:

1. **Pliki sekcji `.tex`** konwertowane z draftów markdown:
   - `rozdzial3.tex` — kompletny rozdział (z `Rozdzial3.md`),
   - `rozdzial4_nowe_sekcje.tex` — sekcje 4.6/4.7/4.8 (z części B
     `Rozdzial4_poprawki.md`) + `rozdzial4_instrukcje.md` — lista
     „znajdź → zastąp" dla istniejących fragmentów rozdz. 4 (część A),
   - `rozdzial5.tex` + `zakonczenie.tex` (z `Rozdzial5.md`).
   - Konwencje: tabele `booktabs`, figury `\includegraphics` ze ścieżkami
     paczki figur, cytowania `\cite{...}` (nowe klucze zdefiniowane w pkt 3).
2. **Paczka figur** (`thesis_figures/output/`, PNG 300 DPI + SVG), uzupełniona o:
   - regenerowany rys. 4.1 (podział 60/20/20 — obecny pokazuje 56/14/30),
   - heatmapy 4.5 (RF) i 4.7 (XGB) przeliczone na **CV-AUC na zbiorze
     treningowym** (nowy skrypt sweep, siatka 5×5, 5-fold; jedyny kosztowny
     obliczeniowo element — uruchamiany w tle na początku toru),
   - krzywe uczenia LSTM W3 (retrain z zapisem history — deterministyczny,
     seed 42),
   - RF top-20 feature importance, globalny SHAP beeswarm+bar dla XGBoost,
   - mapę „numer rysunku w pracy → plik → co się zmieniło vs v8"
     (w tym: zamienione podpisy 4.3/4.4).
3. **`bibliografia_nowe.tex`** — pozycje: Hardt/Price/Srebro 2016 (equalized
   odds), Bird et al. 2020 (fairlearn), Zadrozny & Elkan 2002 (kalibracja
   izotoniczna), Akiba et al. 2019 (Optuna), opcjonalnie Grinsztajn et al.
   2022 (drzewa vs sieci na danych tabelarycznych); format zgodny z [1]–[31],
   z listą miejsc cytowań.
4. **`checklista_skladu.md`** — globalne poprawki redakcyjne wykonywane
   ręcznie w Overleafie (rozłączne z `rozdzial4_instrukcje.md`, który dotyczy
   wyłącznie podmian w treści rozdz. 4): TOC 5.2/5.3 (3→5 modeli), strony
   rozdz. 3, podpisy rys. 4.3/4.4, formatowanie sekcji 2.3.4, usunięcie
   zdań-obietnic bez pokrycia (bootstrap ma już pokrycie — B3).

**Pętla walidacji v9:** użytkownik składa → wrzuca `Praca Magisterska-9.pdf`
do repo → skrypt `validate_thesis.py` (ekstrakcja tekstu + ~15 sprawdzeń
z listy R3 `Fable5_Task1.md`: liczby vs `reports/*.csv`, frazy-relikty
(„trzy klasyfikatory", „70/30", „(6, 3)", stare progi), spójność TOC,
niepuste rozdziały) → `WalidacjaPDFv9.md` → iteracja do zera czerwonych.

**Kryterium ukończenia:** walidacja czysta; rozdz. 3/5/Zakończenie niepuste;
figury w pracy zgodne z mapą.

**Założenie do potwierdzenia:** projekt LaTeX poza repo; jeśli użytkownik
udostępni źródła w repo, skład przejmuje agent i pętla się skraca.

## Tor 2 — obrona i demo (równoległy, niezależny od Toru 1)

1. **Q&A** — `docs/thesis/obrona_QA.md`:
   - część fairness (prompt F9 z `Fable5_Task2.md`), zaktualizowana o wyniki
     sesji 2026-07-07: kontr-eksperyment bez SEX (|ΔAUC| ≤ 0.001, DPD XGB
     0.036→0.011) domyka pytanie o SEX w cechach; pytanie o progi-na-teście
     ma odpowiedź „naprawione" (`threshold_leakage_fix.md`),
   - część ogólna (Q1–Q5 z `Fable5_Task1.md`, przeliczone): LSTM +2.6pp
     @FA=10% jako nowa amunicja H2; diagnoza B1 (dryf tylko LSTM +0.004,
     drzewa czyste) na pytanie o symulowany monitoring; bootstrap CI
     (nierozróżnialność RF/XGB/LGBM) na pytanie o ranking modeli,
   - **ściąga liczb** (1 strona do druku): AUC/Brier/progi/DPD/EOD/delty
     static-vs-dynamic, z datą i hashem commita artefaktów.
2. **Higiena danych + demo:** `docker compose down -v` (kasuje `pg_data`
   ze snapshotami sprzed fixu U1) → `up` → health + smoke test API →
   `seed_demo_clients.py` → weryfikacja w UI (5 linii Timeline, alerty,
   SHAP na naprawionych artefaktach) → **próba generalna** wg scenariusza
   ze slajdów z pomiarem czasu.
3. **Plan awaryjny:** nagranie przebiegu demo lub seria zrzutów do slajdów
   zapasowych; podmiana ewentualnych zrzutów sprzed fixu U1
   w `prezentacja_seminarium/`.

**Kryterium ukończenia:** Q&A + ściąga w repo; demo przechodzi próbę
end-to-end na czystej bazie; materiał awaryjny istnieje.

## Etap wspólny (po obu torach)

- **Próba obrony**: przejście slajdów z kartami Q&A + demo w jednej sesji;
  wychwycone niespójności wracają do właściwego toru.
- **Polish — jawnie poza ścieżką krytyczną, tylko przy zapasie czasu:**
  CREDIT-304 (UI: responsive/a11y/dark mode; tor MK), opcjonalne F3/F4
  (bootstrap CI dla DPD/EOD, prototyp ThresholdOptimizer).

## Kolejność i zależności

```
Tor 1: [sweep heatmap w tle] figury → .tex + biblio + checklista → (skład: użytkownik) → walidacja v9 ⟲
Tor 2: Q&A + ściąga → higiena DB + re-seed → próba demo → nagranie awaryjne
Wspólny: próba obrony (wymaga: v9 ✓ ∧ demo ✓) → poprawki → [polish]
```

Tory niezależne; Tor 2 wypełnia oczekiwanie na skład/kompilacje w Torze 1.

## Ryzyka i mitygacje

| Ryzyko | Mitygacja |
|---|---|
| Pętla składu v9 się wydłuża | checklista per punkt + automatyczny walidator → tania iteracja |
| Rozjazd liczb praca↔slajdy↔ściąga | jedno źródło (`FINAL_REPORT.md` + CSV); ściąga z hashem commita |
| Demo pada na sali | nagranie/zrzuty zapasowe przygotowane po udanej próbie |
| Pokusa retrainu przed obroną | zamrożenie artefaktów: żadnych retrainów bez pełnej kaskady walidacji |
| Sweep heatmap trwa godzinami | start w tle na początku; heatmapy nie blokują reszty paczki |

## Testowanie / weryfikacja end-to-end

1. `validate_thesis.py` na v9 — zero czerwonych punktów.
2. Kompilacja plików `.tex` w minimalnym szablonie (smoke test składni) przed
   przekazaniem użytkownikowi.
3. Demo: pełny przebieg scenariusza na czystej bazie bez błędów; czas ≤ slotu
   prezentacji.
4. Spot-check 10 liczb: praca (v9) ↔ ściąga ↔ slajdy ↔ `reports/*.csv`.
