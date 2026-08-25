# TO-DO-OBRONA.md — co zostało do zrobienia przed obroną

> Stan na 2026-07-07. Krok 1 (próba demo + materiał awaryjny) — ✅ wykonany.
> Kod, eksperymenty, figury, paczka LaTeX, Q&A i środowisko demo — gotowe.
> Zostały wyłącznie kroki wymagające Ciebie (skład + próby).

---

## ✅ Zrobione (dla kontekstu)

- Wszystkie naprawy kodu (train/serve parity U1, progi na splicie kalibracyjnym,
  skalery po splicie) + atomowy retrain + re-run raportów — liczby kanoniczne
  w `ml-learing-center/reports/` (`FINAL_REPORT.md` agreguje).
- Paczka LaTeX z pełną treścią rozdz. 3/4-nowe/5/Zakończenie: `docs/thesis/latex/`
  (kompiluje się czysto — smoke test tectonic).
- Komplet figur rozdz. 3–5 (CV-AUC heatmapy, split 60/20/20, W3 LSTM, fairness 5.10).
- Walidator PDF: `ml-learing-center/validate_thesis.py` (16 checków).
- Q&A na obronę + ściąga liczb: `docs/thesis/obrona_QA.md` (liczby zweryfikowane 12/12).
- Środowisko demo: czysta baza + 3 klientów demo; scenariusz:
  `prezentacja_seminarium/demo_scenariusz.md`; materiał awaryjny: `demo_zapas/`.

---

## KROK 2 — Skład pracy w Overleafie (~2–4 h) ⬅️ NASTĘPNY

1. Wgraj do projektu Overleaf pliki z `docs/thesis/latex/`:
   - `rozdzial3.tex` → treść pustego rozdziału 3,
   - `rozdzial4_nowe_sekcje.tex` → wstaw po sekcji 4.5 (nowe 4.6/4.7/4.8),
   - `rozdzial5.tex` + `zakonczenie.tex` → treść rozdziału 5 i Zakończenia,
   - `bibliografia_nowe.tex` → dopisz pozycje [32]–[36] na końcu bibliografii.
2. Wykonaj **6 podmian** w istniejącym rozdziale 4 wg `docs/thesis/latex/rozdzial4_instrukcje.md`
   (Z1–Z6: każda ma „ZNAJDŹ → ZASTĄP" + tabela podmian figur).
3. Wgraj figury PNG wg mapy `docs/thesis/latex/FIGURY.md`
   (pliki lokalnie w `ml-learing-center/thesis_figures/output/` i `ml-learing-center/reports/`).
4. Przejdź `docs/thesis/latex/checklista_skladu.md` punkt po punkcie
   (TOC 3→5 modeli, zamienione podpisy rys. 4.3↔4.4, „trzy badane algorytmy"
   w 2.1.1, formatowanie 2.3.4, spisy tabel/rysunków).
5. Eksportuj PDF i zapisz jako **`Praca Magisterska-9.pdf` w katalogu głównym repo**.

## KROK 3 — Walidacja v9 (5 min na iterację, pętla do 16/16 🟢)

1. Uruchom:
   ```
   cd ml-learing-center && .venv/bin/python validate_thesis.py "../Praca Magisterska-9.pdf"
   ```
   (albo napisz do Claude'a „v9 w repo" — poprowadzi pętlę i wyjaśni czerwone punkty).
2. Raport `WalidacjaPDFv9.md` → poprawki w Overleafie → ponowny eksport → powtórka,
   aż **exit 0 / 16/16 🟢**.
3. Po czystej walidacji: commit `WalidacjaPDFv9.md` + PDF do repo.

## KROK 4 — Próba obrony (1 sesja, najlepiej z drugą osobą)

1. Wydrukuj ściągę liczb (`docs/thesis/obrona_QA.md`, część C).
2. Przejdź `docs/thesis/proba_obrony_checklist.md`: slajdy → losowane pytania
   z Q&A → demo wg scenariusza. Cel: ≤ 25 min łącznie.
3. Każdą niespójność wpisz do tabeli w checkliście (z przypisaniem: tekst/skład
   vs demo/Q&A) i popraw przed obroną.
4. Kryterium wyjścia: zero otwartych niespójności, odpowiedzi „obronne".

## Opcjonalnie (tylko przy zapasie czasu — nic nie blokuje)

- CREDIT-304 (UI polish: responsive/a11y/dark mode — tor MK).
- F3/F4 (bootstrap CI dla DPD/EOD; prototyp ThresholdOptimizer) — prompty
  w `Fable5-zmiany.md` (sekcja Task 2).
- Rozszerzenie audytu fairness na AGE/EDUCATION/MARRIAGE (appendix).

## Środowisko — przydatne komendy

```
docker compose up -d          # start demo (db + backend + ml-service)
docker compose down           # stop (BEZ -v! — -v kasuje dane demo)
cd frontend/WebApp && npm run dev          # frontend na :5173
ml-learing-center/.venv/bin/python ml-learing-center/seed_demo_clients.py  # re-seed
```

**Zamrożenie artefaktów:** do obrony żadnych retrainów (`main.py`) — każdy retrain
unieważnia liczby w pracy/ściądze/slajdach i wymaga pełnej kaskady re-runów.
