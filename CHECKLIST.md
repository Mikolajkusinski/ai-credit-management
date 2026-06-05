# CHECKLIST.md — Postęp prac

> Lista zadań zsynchronizowana z `TASKS.md`. Aktualizuj po zmergeowaniu każdego PR-a.
>
> **Legenda statusów:**
>
> - 🟢 **Wykonane** — task zmergeowany do `main`.
> - 🔴 **Do zrobienia** — task dostępny (wszystkie `blocked_by` są 🟢), nie został jeszcze rozpoczęty.
> - 🔒 **Zablokowane** — task czeka na zależność (`blocked_by` zawiera coś, co nie jest 🟢).
>
> **Ostatnia aktualizacja:** 2026-06-05 (po merge CREDIT-108 Optuna+CV — RF +0.0010, XGB +0.0030 test AUC vs default; Sprint 4 GF backlog fully closed: 107 ✅ + 108 ✅ + 109 ✅)

---

## 🎯 Aktualne zadanie

- **Gabriel Figur (GF):** 🔴 **CREDIT-113** — Stacked ensemble (LR meta-learner na 5 modelach bazowych) · branch `sprint6/stacking` *(ostatnie ogniwo przed CREDIT-114 final report)*
- **Mikołaj Kusiński (MK):** 🔴 **CREDIT-303** — SnapshotForm + datepicker; fix zahardkodowanych miesięcy w `InputForm.tsx`; „kopiuj z poprzedniej migawki" · branch `sprint5/snapshot-entry` *(Sprint 5 P1; odblokowane przez CREDIT-210 + CREDIT-301)*

> **Reguła aktualizacji tej sekcji:** gdy task zostanie zmergeowany do `main`, ustaw tutaj kolejny najwyżej priorytetowy dostępny (🔴) task z toru właściwej osoby. Jeśli osoba nie ma już dostępnych tasków w bieżącym sprincie, wpisz „⏸️ czeka na odblokowanie / koniec sprintu".

---

## 📊 Statystyki

- **Łącznie zadań:** 29 (CREDIT-115 dodany 2026-06-05 jako follow-up do CREDIT-109)
- **🟢 Wykonane:** 21 (CREDIT-101, CREDIT-102, CREDIT-103, CREDIT-201, CREDIT-401, CREDIT-402, CREDIT-210, CREDIT-104, CREDIT-202, CREDIT-203, CREDIT-204, CREDIT-301, CREDIT-302, CREDIT-205, CREDIT-105, CREDIT-110, CREDIT-111, CREDIT-106, CREDIT-109, CREDIT-107, CREDIT-108)
- **🔴 Dostępne:** 5 (CREDIT-112, CREDIT-113, CREDIT-115, CREDIT-211, CREDIT-303)
- **🔒 Zablokowane:** 3

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

- 🟢 **CREDIT-105** · [ML] · P0 · GF · `sprint2/calibration`
  - Kalibracja izotoniczna (3-way split train/calib/test); Brier po < przed. CalibratedClassifierCV(FrozenEstimator, isotonic) dla RF/XGB; sklearn IsotonicRegression na raw output LSTM. Brier −19/−24/−23%; AUC zachowane.
  - blocked_by: 102 · blocks: 106, 113

- 🟢 **CREDIT-202** · [BE] · P0 · MK · `sprint2/dotnet-timeseries`
  - `.NET POST /api/v1/monitoring/predict-timeseries`; proxy nad Flask + walidacja + labelki okien + mapowanie błędów (400/502/503). Test integracyjny (WebApplicationFactory + stub HttpMessageHandler).
  - blocked_by: 210, 104 · blocks: —

- 🟢 **CREDIT-203** · [BE] · P0 · MK · `sprint2/persistence-write`
  - Repozytoria EF Core (Snapshot/Prediction/Trend) + endpoint `POST /api/v1/monitoring/clients/{ref}/snapshots`: scoring (reuse) → zapis migawki + predykcji W3 + upsert trendów; 409 przy duplikacie `(ref, snapshotDate)`. Test integracyjny (WebApplicationFactory + EF InMemory + stub Flask, 4 testy).
  - blocked_by: 401, 210 · blocks: 204, 205

---

## Sprint 3 — Dowód tezy + start frontendu (30 cze – 13 lip)

- 🟢 **CREDIT-110** · [EVAL] · P0 · GF · `sprint3/timeseries-metrics`
  - Early-warning lead time + rozkład slope (default vs non-default) + AUC trajektorii. Catch rate ~50% (próg 0.5), mean lead time ~2.05 okien, slope_auc ~0.59 vs w3_auc ~0.77. 6 PNG + CSV + Markdown report w `reports/`.
  - blocked_by: 101, 102, 104 · blocks: 111

- 🟢 **CREDIT-111** · [EVAL] · P0 · GF · `sprint3/static-vs-dynamic`
  - **DOWÓD TEZY** — statyka (PD z W3) vs monitoring (trajektoria); catch rate vs fałszywe alarmy. Mixed results @ FA=10%: monitoring tracił 2-6pp catch vs static (max-aggregator noise > single calibrated snapshot), ALE mean lead ~2 okna i 43-184 unikalnych catchy/model. Framing: "monitoring offers earlier detection at comparable discrimination". 3 ROC overlay PNG + 2 CSV + Markdown report.
  - blocked_by: 110 · blocks: 114

- 🟢 **CREDIT-106** · [ML] · P1 · GF · SWAP-OK · `sprint3/cost-thresholds`
  - Progi kosztowe (FN > FP); `alert_thresholds.json` w (0.1, 0.9). Per-model optymalne: RF=0.145 / XGB=0.180 / LSTM=0.185 (FN=5×FP). Flask response z `costThresholds` + `windowAlerts` (additive, non-breaking).
  - blocked_by: 105 · blocks: —

- 🟢 **CREDIT-204** · [BE] · P0 · MK · `sprint3/client-history-get`
  - `GET /api/v1/monitoring/clients/{ref}/history` — składa zapisane migawki w chronologiczną trajektorię PD (asc po dacie) + W3 predykcje per punkt + bieżące trendy z tabeli Trend; opcjonalne `from`/`to`/`limit`; 404 CLIENT_NOT_FOUND, 400 przy złym limit/zakresie dat. Test integracyjny (WebApplicationFactory + EF InMemory + stub Flask, 5 testów).
  - blocked_by: 203 · blocks: 302

- 🟢 **CREDIT-301** · [FE] · P0 · MK · `sprint3/timeline-view`
  - Widok Timeline z zakładką (Prediction / Monitoring): Recharts LineChart trajektorii PD (X=label okna, Y=PD 0–1, 3 linie RF/XGB/LSTM) + karty alertów semaforowych (slope W3−W0). Renderuje mock z kontraktu 210; gotowy klient `monitoringApi.ts` (`predictTimeseries` + `MOCK_TIMESERIES_RESPONSE`) pod CREDIT-302/303. Testy Vitest (6: buildChartData 4 punkty/model + smoke; karty alertów: nazwy, labelki, slope).
  - blocked_by: 210 · blocks: 302, 303

---

## Sprint 4 — Integracja + interpretowalność + tuning (14 lip – 27 lip)

- 🟢 **CREDIT-302** · [FE] · P1 · MK · `sprint4/client-history-ui`
  - Lista klientów + widok historii na realnych danych z bazy. Nowy backend `GET /api/v1/monitoring/clients` (roster ze statami: snapshotCount, latestSnapshotDate, roll-up alert; kontrakt 4.5) + repo projection `GetClientStatsAsync`. Frontend: `monitoringApi.listClients/getClientHistory`, `ClientList.tsx` (realna lista, badge alertu, klik → historia), `ClientHistory.tsx` (GET history → reuse `TimelineChart`+`TrendAlerts`, mapper `historyToTrajectory`), zakładka Monitoring jako master-detail (ClientList ⇄ ClientHistory). `TimelineChart` z opcjonalnymi `title`/`subtitle` (defaulty bez zmian → testy 301 zielone). Testy: backend +2 (ClientListTests: lista po migawkach + pusta), frontend +9 (ClientList 4, ClientHistory 5).
  - blocked_by: 204, 301 · blocks: 304

- 🟢 **CREDIT-205** · [BE] · P1 · MK · SWAP-OK · `sprint4/persistence-tests`
  - Wierne testy integracyjne persystencji na realnym PostgreSQL 16 przez Testcontainers (uruchamia prawdziwą migrację Npgsql, nie EF InMemory). Nowy `WebApi.Tests/PersistenceTests.cs` (8 testów) + współdzielony `PostgresFixture` (jeden kontener `postgres:16-alpine` na klasę, `TRUNCATE … RESTART IDENTITY CASCADE` między testami). Reuse harnessu z 203/204 (WebApplicationFactory + stub Flask), podmiana providera InMemory → `UseNpgsql`. Pokrycie tego, czego InMemory nie sprawdza: round-trip zapis→odczyt (Client/Snapshot/3×Prediction W3/3×Trend), historia rosnąco po dacie, **kaskadowe usuwanie FK** (usunięcie klienta czyści snapshoty/predykcje/trendy), unikalny `ExternalRef`, upsert trendów (nadpisanie nie duplikacja + bump `ComputedAt`), 409 na duplikat `(ref, date)`, round-trip `timestamptz`↔`DateOnly` (Kind=Utc), serwerowe defaulty `NOW()`. Tylko testy — kod produkcyjny nietknięty (atomowa transakcja pozostaje świadomie odłożona). Backend: 16 → 24 testów, CI zielone.
  - blocked_by: 203, 201 · blocks: —

- 🟢 **CREDIT-107** · [ML] · P2 · GF · SWAP-OK · `sprint4/shap`
  - SHAP top-5 cech per predykcja (RF/XGB/LightGBM/CatBoost; LSTM pominięty — TreeExplainer N/A); `shap.topFeatures` w response. 102 ms compute (20× pod DoD < 2s). PR #26.
  - blocked_by: 102 · blocks: 211

- 🟢 **CREDIT-108** · [ML] · P2 · GF · `sprint4/optuna-cv`
  - 5-fold CV + Optuna tuning (XGBoost/RF), 30 trials, TPESampler. Test AUC: RF +0.0010 / XGB +0.0030 vs default. Best XGB: lr=0.0075, depth=3, n_est=1000. Scope: academic — tuned bases NIE promoted do produkcji. PR #27.
  - blocked_by: 102 · blocks: —

---

## Sprint 5 — UX migawek, alerty, modele, fairness (28 lip – 10 sie)

- 🔴 **CREDIT-303** · [FE] · P1 · MK · `sprint5/snapshot-entry`
  - SnapshotForm + datepicker; fix zahardkodowanych miesięcy w `InputForm.tsx`; „kopiuj z poprzedniej migawki".
  - blocked_by: 210, 301 · blocks: 304

- 🔴 **CREDIT-211** · [BE/FE] · P2 · MK · SWAP-OK · `sprint5/shap-ui`
  - SHAP pass-through w .NET DTO + komponent wizualizacji (bar/waterfall). Odblokowane przez CREDIT-107 merge.
  - blocked_by: 107, 210 · blocks: —

- 🟢 **CREDIT-109** · [ML] · P2 · GF · `sprint5/lgbm-catboost`
  - LightGBM + CatBoost na oknach 3-mies.; 5 modeli w response Flask. CatBoost najlepszy (AUC 0.7802, Brier 0.1354); cost thresholds rozszerzone do 5 modeli; `compute_trends` iteracyjne po `predictions.keys()`. PR #23, merged 2026-06-05.
  - blocked_by: 102 · blocks: 113

- 🔴 **CREDIT-112** · [EVAL] · P1 · GF · SWAP-OK · `sprint5/fairness`
  - Audyt fairness (fairlearn) — DPD / EOD względem SEX; ostrzeżenie gdy |różnica| > 0.1.
  - blocked_by: 102 · blocks: —

- 🔴 **CREDIT-115** · [BE] · P2 · GF · `feat/backend-5model-dtos`
  - Backend DTO follow-up do CREDIT-109: rozszerzenie `WindowPredictions` + `Trends` (.NET) o `lightgbm` + `catboost` — pełen 5-model passthrough z Flaska. Integration gap odkryty 2026-06-05 podczas demo prep (curl pokazał 3 keys zamiast 5). 5 predictions + 5 trends per snapshot persistowane; bez migracji DB. PR #32.
  - blocked_by: 109, 202 · blocks: —

---

## Sprint 6 — Polish, ensemble, raport, docs (11 sie – 24 sie)

- 🔴 **CREDIT-113** · [ML] · P2 · GF · `sprint6/stacking`
  - Stacked ensemble (LR meta-learner na 5 modelach bazowych). **Ostatnie ogniwo przed CREDIT-114 final report.**
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
