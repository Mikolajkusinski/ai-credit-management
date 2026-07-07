# CHECKLIST.md — Postęp prac

> Lista zadań zsynchronizowana z `TASKS.md`. Aktualizuj po zmergeowaniu każdego PR-a.
>
> **Legenda statusów:**
>
> - 🟢 **Wykonane** — task zmergeowany do `main`.
> - 🔴 **Do zrobienia** — task dostępny (wszystkie `blocked_by` są 🟢), nie został jeszcze rozpoczęty.
> - 🔒 **Zablokowane** — task czeka na zależność (`blocked_by` zawiera coś, co nie jest 🟢).
>
> **Ostatnia aktualizacja:** 2026-07-07 (po merge CREDIT-114 final report + CREDIT-501 docs; wcześniej tego dnia: descope CREDIT-113, naprawy train/serve skew U1 i wycieków metodologicznych z atomowym retrainem — `reports/{threshold,scaler}_leakage_fix.md`, transakcja atomowa w zapisie migawki + test rollbacku, job CI dla ml-learing-center)

---

## 🎯 Aktualne zadanie

- **Gabriel Figur (GF):** ⏸️ wszystkie zadania toru GF wykonane (ścieżka krytyczna tezy domknięta: 101→102→104→110→111→114 ✅); dalej: teksty pracy (rozdz. 3/5) + eksperymenty dowodowe na obronę (plan: `Fable_Task4.md` / plik planu)
- **Mikołaj Kusiński (MK):** 🔴 **CREDIT-304** — UI polish (responsive 1024/1440/1920, a11y Lighthouse ≥ 90, dark mode, tooltipy modeli) · branch `sprint6/ui-polish` *(Sprint 6 P2; ostatni otwarty task projektu)*

> **Reguła aktualizacji tej sekcji:** gdy task zostanie zmergeowany do `main`, ustaw tutaj kolejny najwyżej priorytetowy dostępny (🔴) task z toru właściwej osoby. Jeśli osoba nie ma już dostępnych tasków w bieżącym sprincie, wpisz „⏸️ czeka na odblokowanie / koniec sprintu".

---

## 📊 Statystyki

- **Łącznie zadań:** 30 (CREDIT-115 + CREDIT-116 dodane 2026-06-05 jako follow-up do CREDIT-109)
- **🟢 Wykonane:** 28 (CREDIT-101, CREDIT-102, CREDIT-103, CREDIT-201, CREDIT-401, CREDIT-402, CREDIT-210, CREDIT-104, CREDIT-202, CREDIT-203, CREDIT-204, CREDIT-301, CREDIT-302, CREDIT-205, CREDIT-105, CREDIT-110, CREDIT-111, CREDIT-106, CREDIT-109, CREDIT-107, CREDIT-108, CREDIT-115, CREDIT-116, CREDIT-303, CREDIT-211, CREDIT-112, **CREDIT-114**, **CREDIT-501**)
- **🔴 Dostępne:** 1 (CREDIT-304)
- **🔒 Zablokowane:** 0
- **⚪ Descoped:** 1 (CREDIT-113 — decyzja 2026-07-07, backlog po obronie)

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
  - **DOWÓD TEZY** — statyka (PD z W3) vs monitoring (trajektoria); catch rate vs fałszywe alarmy. Mixed results @ FA=10% *(liczby po leakage-fix 2026-07-07)*: monitoring traci 5-11pp catch vs static dla 4 modeli statycznych, ALE **LSTM jako jedyny wygrywa monitoringiem (+2.6pp)**; mean lead ~2 okna i 39-74 unikalnych catchy/model. Framing: "monitoring offers earlier detection at comparable discrimination". 5 ROC overlay PNG + 2 CSV + Markdown report + `threshold_leakage_fix.md`.
  - blocked_by: 110 · blocks: 114

- 🟢 **CREDIT-106** · [ML] · P1 · GF · SWAP-OK · `sprint3/cost-thresholds`
  - Progi kosztowe (FN > FP); `alert_thresholds.json` w (0.1, 0.9). Per-model optymalne *(po leakage-fix 2026-07-07: optymalizacja na splicie kalibracyjnym, nie testowym)*: RF=0.145 / XGB=0.165 / LGBM=0.160 / CatBoost=0.160 / LSTM=0.155 (FN=5×FP). Flask response z `costThresholds` + `windowAlerts` (additive, non-breaking).
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

- 🟢 **CREDIT-303** · [FE] · P1 · MK · `sprint5/snapshot-entry`
  - SnapshotForm (reuse `InputForm` + natywny `<input type="date">`) w zakładce Monitoring: przycisk „+ Add snapshot" w `ClientHistory` odsłania datowany formularz 22 cech → `POST /clients/{ref}/snapshots` (nowy `createSnapshot` w `monitoringApi.ts` + typy `CreateSnapshotRequest/Response`) → reload trajektorii; mapowanie błędów 400/409/502/503 (409 = „snapshot już istnieje dla tej daty"). Fix 3× zahardkodowanych miesięcy w `InputForm.tsx` → `deriveMonthLabels(referenceDate)` (rollover-safe, miesiące względem wybranej daty migawki). „Kopiuj z poprzedniej migawki" jako pamięć sesji w `ClientHistory` (history endpoint zwraca tylko PD, nie surowe cechy). `InputForm` wstecznie kompatybilny (nowe propsy opcjonalne — zakładka Prediction bez zmian). Testy Vitest 16 → 27 (InputForm +5, SnapshotForm +5, ClientHistory +1).
  - blocked_by: 210, 301 · blocks: 304

- 🟢 **CREDIT-211** · [BE/FE] · P2 · MK · SWAP-OK · `sprint5/shap-ui`
  - SHAP pass-through w .NET DTO + komponent wizualizacji. Gap j.w. CREDIT-115: Flask `/predict/timeseries` zwracał `shap` (4 modele tree-based × top-5 cech, contract §3.5) ale backend DTO go silently dropował przy deserializacji. Backend: `ShapExplanation`/`ShapModel`/`ShapFeature` w `TimeseriesResponse.cs`, `Shap` w `SnapshotResponse.cs`, `Shap = scored.Shap` w `MonitoringService.ScoreAndPersistAsync` (additive, bez migracji DB — SHAP scoring-time only, nieperzystowany). Frontend: typy SHAP w `monitoring.ts` (+`shap?` na `TimeseriesResponse`/`CreateSnapshotResponse`), `MOCK_TIMESERIES_RESPONSE` z blokiem `shap`, nowy `ShapExplanation.tsx` (diverging horizontal bars dla 4 modeli, czerwone + = podnosi PD, zielone − = obniża; długość ∝ |value|/max). Wpięte w `SnapshotForm` — po dodaniu migawki SHAP renderuje się pod formularzem („why this score?"). Testy: backend +2 asserty (`MonitoringTimeseriesTests` + `SnapshotPersistenceTests`, 24/24), frontend +`ShapExplanation.test.tsx` (27→34 vitest). LSTM pominięty (TreeExplainer N/A — zgodnie z CREDIT-107).
  - blocked_by: 107, 210 · blocks: —

- 🟢 **CREDIT-109** · [ML] · P2 · GF · `sprint5/lgbm-catboost`
  - LightGBM + CatBoost na oknach 3-mies.; 5 modeli w response Flask. CatBoost najlepszy (AUC 0.7793, Brier 0.1357 *po leakage-fix 2026-07-07*; pierwotnie 0.7802/0.1354); cost thresholds rozszerzone do 5 modeli; `compute_trends` iteracyjne po `predictions.keys()`. PR #23, merged 2026-06-05.
  - blocked_by: 102 · blocks: 113

- 🟢 **CREDIT-112** · [EVAL] · P1 · GF · SWAP-OK · `sprint5/fairness`
  - Audyt fairness (fairlearn) — DPD (demographic parity diff) i EOD (equalized odds diff) względem SEX dla 5 modeli W3, przy progach binaryzacji z `alert_thresholds.json` (cost-opt, FN=5×FP). Wszystkie modele |DPD| oraz |EOD| ≤ 0.1; DPD dodatnie (mężczyźni nieco częściej flagowani, zgodnie z wyższym base rate defaultów w grupie SEX=1). Max DPD CatBoost (0.039), min LSTM (0.007). Pliki: `ml-learing-center/fairness_audit.py`, `reports/fairness_report.md`, `reports/fairness_metrics_w3.csv`, `reports/fairness_selection_rate_w3.png`, `reports/fairness_tpr_fpr_w3.png`; dependency `fairlearn>=0.10` w `requirements.txt`.
  - blocked_by: 102 · blocks: —

- 🟢 **CREDIT-115** · [BE] · P2 · GF · `feat/backend-5model-dtos`
  - Backend DTO follow-up do CREDIT-109: rozszerzenie `WindowPredictions` + `Trends` (.NET) o `lightgbm` + `catboost` — pełen 5-model passthrough z Flaska. Integration gap odkryty 2026-06-05 podczas demo prep (curl pokazał 3 keys zamiast 5). 5 predictions + 5 trends per snapshot persistowane; bez migracji DB. PR #32 merged.
  - blocked_by: 109, 202 · blocks: 116

- 🟢 **CREDIT-116** · [FE] · P2 · GF · `feat/frontend-5model-monitoring`
  - Frontend follow-up do CREDIT-115: rozszerzenie `ModelKey` + `WindowPredictions` + `Trends` (TS) o `lightgbm` + `catboost`; Timeline chart 5 linii z distinct colors (amber + violet); TrendAlerts 5 kart w responsive grid (`repeat(auto-fit, minmax(220px, 1fr))`); `MOCK_TIMESERIES_RESPONSE` rozszerzony. UI Monitoring tab pokazuje teraz 5/5 modeli (było 3/5 mimo backend 5/5). 16/16 vitest passing. PR #33 merged.
  - blocked_by: 115, 301 · blocks: —

---

## Sprint 6 — Polish, ensemble, raport, docs (11 sie – 24 sie)

- 🟢 **CREDIT-114** · [EVAL] · P0 · GF · `sprint6/final-report`
  - Raport końcowy: `ml-learing-center/final_report.py` → `reports/FINAL_REPORT.md` (sekcje 1:1 pod rozdz. 5: tabela 5 modeli, statyka vs monitoring z uczciwym werdyktem, fairness, weryfikacja H1/H2/H3, ograniczenia, mapa artefaktów→sekcje). Każda liczba czytana z plików `reports/`, zero ręcznych wartości. Wykonane 2026-07-07 po leakage-fix.
  - blocked_by: 103, 111 · blocks: — *(113 usunięte z blocked_by po descope 2026-07-07)*

- 🔴 **CREDIT-304** · [FE] · P2 · MK · `sprint6/ui-polish`
  - Responsive (1024/1440/1920), a11y (Lighthouse ≥ 90), dark mode, tooltipy modeli.
  - blocked_by: 302, 303 · blocks: —

- 🟢 **CREDIT-501** · [DOCS] · P0 · GF+MK · `sprint6/docs`
  - README + Model Card + Architecture + aktualizacja `CLAUDE.md` (nowe endpointy, baza, okno 3-mies.). Wykonane 2026-07-07: nowy `README.md` (uruchomienie end-to-end + kluczowe wyniki), `docs/MODEL_CARD.md` (dane/trening/metryki/fairness/ograniczenia — liczby z reports/), `docs/ARCHITECTURE.md` (przepływ + decyzje projektowe), `CLAUDE.md` przepisany na stan 5-modelowy z Postgres i monitoringiem.
  - blocked_by: ~all · blocks: —

---

## ⚪ Descoped / Backlog po obronie

- ⚪ **CREDIT-113** · [ML] · P2 · GF · `sprint6/stacking`
  - Stacked ensemble (LR meta-learner na 5 modelach bazowych).
  - **Świadoma decyzja zakresu 2026-07-07:** stacking nie wnosi do dowodu tezy (H1/H2/H3 nie wymagają ensemble), a poprawna realizacja wymaga protokołu out-of-fold + rekalibracji meta-modelu (bez OOF = wyciek). Przeniesione do kierunków dalszych badań w pracy; w razie powrotu — protokół w `Fable_Task4.md` (prompt P6).
  - blocked_by: 102, 105, 109 · blocks: — *(usunięte z blocked_by CREDIT-114)*

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
