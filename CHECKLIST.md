# CHECKLIST.md — Postęp prac

> Lista zadań zsynchronizowana z `TASKS.md`. Aktualizuj po zmergeowaniu każdego PR-a.
>
> **Legenda statusów:**
>
> - 🟢 **Wykonane** — task zmergeowany do `main`.
> - 🔴 **Do zrobienia** — task dostępny (wszystkie `blocked_by` są 🟢), nie został jeszcze rozpoczęty.
> - 🔒 **Zablokowane** — task czeka na zależność (`blocked_by` zawiera coś, co nie jest 🟢).
>
> **Ostatnia aktualizacja:** 2026-06-03 (po merge CREDIT-204 — odczyt zapisanej trajektorii klienta; endpoint `GET /clients/{ref}/history`)

---

## 🎯 Aktualne zadanie

- **Gabriel Figur (GF):** 🔴 **CREDIT-105** — Kalibracja izotoniczna (3-way split, Brier po < przed) · branch `sprint2/calibration` *(potem 🔴 110, 111)*
- **Mikołaj Kusiński (MK):** 🔴 **CREDIT-301** — widok Timeline (Recharts LineChart trajektorii PD + karty alertów, na mocku z kontraktu) · branch `sprint3/timeline-view` *(Sprint 3 P0; główny slajd obrony)*

> **Reguła aktualizacji tej sekcji:** gdy task zostanie zmergeowany do `main`, ustaw tutaj kolejny najwyżej priorytetowy dostępny (🔴) task z toru właściwej osoby. Jeśli osoba nie ma już dostępnych tasków w bieżącym sprincie, wpisz „⏸️ czeka na odblokowanie / koniec sprintu".

---

## 📊 Statystyki

- **Łącznie zadań:** 27
- **🟢 Wykonane:** 11 (CREDIT-101, CREDIT-102, CREDIT-103, CREDIT-201, CREDIT-401, CREDIT-402, CREDIT-210, CREDIT-104, CREDIT-202, CREDIT-203, CREDIT-204)
- **🔴 Dostępne:** 8 (CREDIT-105, CREDIT-107, CREDIT-108, CREDIT-109, CREDIT-110, CREDIT-112, CREDIT-205, CREDIT-301)
- **🔒 Zablokowane:** 8

---

## 🛤️ Ścieżka krytyczna (oś tezy)

`101 → 102 → 104 → 110 → 111 → 114`. Każde opóźnienie tutaj opóźnia dowód tezy. Wszystko inne biegnie równolegle.

---

## Sprint 1 — Fundament danych i trwałości (2 cze – 15 cze)

### Tor GF (ML)

- 🟢 **CREDIT-101** · [DATA] · P0 · `sprint1/sliding-window-panel`
  - Sliding-window 3-mies. → 4 okna (W0–W3) z wiersza UCI; `extract_windows()` + test pytest.
  - blocked_by: — · blocks: 102, 103, 110, 111

- 🟢 **CREDIT-102** · [ML] · P0 · `sprint1/retrain-3mo`
  - Trening RF/XGB/LSTM na oknie W3; artefakty z sufiksem `_w3` (stare nietknięte); fix mismatchu `utilization_rate`/`severe_late` w `main.py` vs `app.py`.
  - blocked_by: 101 · blocks: 103, 104, 105, 106, 107, 108, 109, 110, 112, 113

- 🟢 **CREDIT-103** · [EVAL] · P0 · `sprint1/revalidate-metrics`
  - AUC/Gini/KS/ROC/PR/calibration; ≥9 wykresów w `ml-learing-center/reports/`.
  - blocked_by: 102 · blocks: 114

### Tor MK (infra)

- 🟢 **CREDIT-201** · [INFRA] · P1 · SWAP-OK · `sprint1/test-infra`
  - xUnit (.NET) + pytest (Python) + Vitest (React) + CI workflow blokujący czerwone PR-y.
  - blocked_by: — · blocks: 205

- 🟢 **CREDIT-401** · [DB] · P0 · `sprint1/db-schema`
  - Schemat Postgres + EF Core (Client/Snapshot/Prediction/Trend) + NuGet packages (EFCore, .Design, .Tools, Npgsql.EFCore.PostgreSQL).
  - blocked_by: — · blocks: 402, 203, 204

- 🟢 **CREDIT-402** · [INFRA] · P1 · `sprint1/docker-postgres`
  - docker-compose: db + backend + ml-service (frontend POZA compose); auto-migracje przy starcie.
  - blocked_by: 401 · blocks: —

---

## Sprint 2 — Silnik monitoringu, kontrakty, zapis (16 cze – 29 cze)

- 🟢 **CREDIT-210** · [CONTRACT] · P0 · GF+MK · `sprint2/contract-monitoring`
  - Payload trajektorii + zapisu migawki; reguła alertu slope (W3−W0).
  - blocked_by: — · blocks: 104, 202, 203, 301

- 🟢 **CREDIT-104** · [ML] · P0 · GF · `sprint2/flask-timeseries`
  - Flask endpoint `/predict/timeseries`: 22 cechy → 4 okna → PD per okno per model + trendy.
  - blocked_by: 102, 210 · blocks: 110, 202

- 🔴 **CREDIT-105** · [ML] · P0 · GF · `sprint2/calibration`
  - Kalibracja izotoniczna (3-way split train/calib/test); Brier po < przed.
  - blocked_by: 102 · blocks: 106, 113

- 🟢 **CREDIT-202** · [BE] · P0 · MK · `sprint2/dotnet-timeseries`
  - `.NET POST /api/v1/monitoring/predict-timeseries`; proxy nad Flask + walidacja + labelki okien + mapowanie błędów (400/502/503). Test integracyjny (WebApplicationFactory + stub HttpMessageHandler).
  - blocked_by: 210, 104 · blocks: —

- 🟢 **CREDIT-203** · [BE] · P0 · MK · `sprint2/persistence-write`
  - Repozytoria EF Core (Snapshot/Prediction/Trend) + endpoint `POST /api/v1/monitoring/clients/{ref}/snapshots`: scoring (reuse) → zapis migawki + predykcji W3 + upsert trendów; 409 przy duplikacie `(ref, snapshotDate)`. Test integracyjny (WebApplicationFactory + EF InMemory + stub Flask, 4 testy).
  - blocked_by: 401, 210 · blocks: 204, 205

---

## Sprint 3 — Dowód tezy + start frontendu (30 cze – 13 lip)

- 🔴 **CREDIT-110** · [EVAL] · P0 · GF · `sprint3/timeseries-metrics`
  - Early-warning lead time + rozkład slope (default vs non-default) + AUC trajektorii.
  - blocked_by: 101, 102, 104 · blocks: 111

- 🔒 **CREDIT-111** · [EVAL] · P0 · GF · `sprint3/static-vs-dynamic`
  - **DOWÓD TEZY** — statyka (PD z W3) vs monitoring (trajektoria); catch rate vs fałszywe alarmy.
  - blocked_by: 110 · blocks: 114

- 🔒 **CREDIT-106** · [ML] · P1 · GF · SWAP-OK · `sprint3/cost-thresholds`
  - Progi kosztowe (FN > FP); `alert_thresholds.json` w (0.1, 0.9).
  - blocked_by: 105 · blocks: —

- 🟢 **CREDIT-204** · [BE] · P0 · MK · `sprint3/client-history-get`
  - `GET /api/v1/monitoring/clients/{ref}/history` — składa zapisane migawki w chronologiczną trajektorię PD (asc po dacie) + W3 predykcje per punkt + bieżące trendy z tabeli Trend; opcjonalne `from`/`to`/`limit`; 404 CLIENT_NOT_FOUND, 400 przy złym limit/zakresie dat. Test integracyjny (WebApplicationFactory + EF InMemory + stub Flask, 5 testów).
  - blocked_by: 203 · blocks: 302

- 🔴 **CREDIT-301** · [FE] · P0 · MK · `sprint3/timeline-view`
  - Recharts LineChart trajektorii PD (X=okno, Y=PD, 3 linie) + karty alertów (na mocku).
  - blocked_by: 210 · blocks: 302, 303

---

## Sprint 4 — Integracja + interpretowalność + tuning (14 lip – 27 lip)

- 🔒 **CREDIT-302** · [FE] · P1 · MK · `sprint4/client-history-ui`
  - Lista klientów + widok historii na realnych danych z bazy.
  - blocked_by: 204, 301 · blocks: 304

- 🔴 **CREDIT-205** · [BE] · P1 · MK · SWAP-OK · `sprint4/persistence-tests`
  - Testy integracyjne persystencji (Testcontainers / SQLite in-memory), ≥6 testów.
  - blocked_by: 203, 201 · blocks: —

- 🔴 **CREDIT-107** · [ML] · P2 · GF · SWAP-OK · `sprint4/shap`
  - SHAP top-5 cech per predykcja (RF/XGB/LR); `shap.topFeatures` w response.
  - blocked_by: 102 · blocks: 211

- 🔴 **CREDIT-108** · [ML] · P2 · GF · `sprint4/optuna-cv`
  - 5-fold CV + tuning Optuna (XGBoost/RF) na oknach 3-mies.
  - blocked_by: 102 · blocks: —

---

## Sprint 5 — UX migawek, alerty, modele, fairness (28 lip – 10 sie)

- 🔒 **CREDIT-303** · [FE] · P1 · MK · `sprint5/snapshot-entry`
  - SnapshotForm + datepicker; fix zahardkodowanych miesięcy w `InputForm.tsx`; „kopiuj z poprzedniej migawki".
  - blocked_by: 210, 301 · blocks: 304

- 🔒 **CREDIT-211** · [BE/FE] · P2 · MK · SWAP-OK · `sprint5/shap-ui`
  - SHAP pass-through w .NET DTO + komponent wizualizacji (bar/waterfall).
  - blocked_by: 107, 210 · blocks: —

- 🔴 **CREDIT-109** · [ML] · P2 · GF · `sprint5/lgbm-catboost`
  - LightGBM + CatBoost na oknach 3-mies.; response z 6 modelami.
  - blocked_by: 102 · blocks: 113

- 🔴 **CREDIT-112** · [EVAL] · P1 · GF · SWAP-OK · `sprint5/fairness`
  - Audyt fairness (fairlearn) — DPD / EOD względem SEX; ostrzeżenie gdy |różnica| > 0.1.
  - blocked_by: 102 · blocks: —

---

## Sprint 6 — Polish, ensemble, raport, docs (11 sie – 24 sie)

- 🔒 **CREDIT-113** · [ML] · P2 · GF · `sprint6/stacking`
  - Stacked ensemble (LR meta-learner na 5–6 modelach bazowych).
  - blocked_by: 102, 105, 109 · blocks: 114

- 🔒 **CREDIT-114** · [EVAL] · P0 · GF · `sprint6/final-report`
  - Raport końcowy + komplet wykresów do slajdów obrony.
  - blocked_by: 103, 111, 113 · blocks: —

- 🔒 **CREDIT-304** · [FE] · P2 · MK · `sprint6/ui-polish`
  - Responsive (1024/1440/1920), a11y (Lighthouse ≥ 90), dark mode, tooltipy modeli.
  - blocked_by: 302, 303 · blocks: —

- 🔒 **CREDIT-501** · [DOCS] · P0 · GF+MK · `sprint6/docs`
  - README + Model Card + Architecture + aktualizacja `CLAUDE.md` (nowe endpointy, baza, okno 3-mies.).
  - blocked_by: ~all · blocks: —

---

## 📝 Workflow aktualizacji checklisty

**Po zmergeowaniu PR-a `CREDIT-XXX` do `main`:**

1. W sekcji właściwego sprintu zmień status zadania z 🔴 (lub 🔒) na 🟢.
2. Dla każdego zadania, które było 🔒 i miało `CREDIT-XXX` w `blocked_by`:
   - Sprawdź, czy WSZYSTKIE jego `blocked_by` są teraz 🟢.
   - Jeśli tak — zmień status z 🔒 na 🔴.
3. Zaktualizuj sekcję „📊 Statystyki" (inkrementuj 🟢, dekrementuj 🔴/🔒).
4. Zaktualizuj sekcję „🎯 Aktualne zadanie" — wpisz kolejne dostępne (🔴) zadanie dla właściwej osoby z jej toru (priorytet P0 > P1 > P2, w obrębie sprintu).
5. Zaktualizuj datę „Ostatnia aktualizacja" na górze pliku.
6. Commituj zmianę `CHECKLIST.md` razem z mergem (lub jako osobny PR/commit `chore: update CHECKLIST after CREDIT-XXX`).
