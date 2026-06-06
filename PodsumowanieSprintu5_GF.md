# Podsumowanie Sprintu 5 — tor GF (Gabriel Figur)

> Dokument dla seminarium magisterskiego (2026). Streszcza **mój wkład (GF)** w Sprint 5 projektu
> `ai-credit-management`. **Sprint 5 GF zamknięty 1/1 zadania świeżego** (CREDIT-112 fairness audit)
> + 2 follow-upy do CREDIT-109 (CREDIT-115 BE i CREDIT-116 FE) potraktowane jako audit-trail tasks
> wykonane chronologicznie między Sprintem 4 a Sprintem 5.
>
> Perspektywa toru MK Sprintu 5 (CREDIT-303 SnapshotForm + CREDIT-211 SHAP UI) — w
> `PodsumowanieSprintu2_MK.md` (update z 2026-06-06). Mój Sprint 4 (107/108/109 — w tym CREDIT-109
> pull-forwarded z planu Sprintu 5) — `PodsumowanieSprintu4_GF.md`.

---

## 1. Kontekst i mój zakres

**Plan Sprintu 5 mojego toru (per `TASKS.md` / `plan_sprintow_wariant_B.md`):**

| ID | Tag | Prio | Co |
|---|---|---|---|
| CREDIT-109 | ML | **P2** | LightGBM + CatBoost na oknach 3-mies. |
| CREDIT-112 | EVAL | **P1** SWAP-OK | Fairness audit (DPD / EOD per SEX) |

**Sytuacja na początku Sprintu 5:** CREDIT-109 **już dostarczone** w Sprincie 4 (PR #23, pull-forward
out-of-order pod łańcuch krytyczny `109 → 113 → 114`). Pozostało jedno fresh zadanie planowe —
**CREDIT-112** — plus dwa follow-upy do CREDIT-109 dosłodzone w oknie międzysprintowym (CREDIT-115
BE 5-model DTO, CREDIT-116 FE 5-model UI).

**Status po Sprincie 5 (kalendarzowo, 2026-06-06):**

| Status zadań mojego toru po Sprincie 5 |
|---|
| **CREDIT-112** — 🟢 zrobione (PR #37) — fairness audit fairlearn, 5 modeli, |DPD|/|EOD| ≤ 0.1 |
| **CREDIT-109** — 🟢 zrobione w Sprincie 4 (PR #23, patrz `PodsumowanieSprintu4_GF.md` §4) |
| **CREDIT-115** — 🟢 zrobione w oknie post-Sprint 4 (PR #32, patrz `PodsumowanieSprintu4_GF.md` §4.1) |
| **CREDIT-116** — 🟢 zrobione w oknie post-Sprint 4 (PR #33 + audit-trail PR #34) |

Harmonogram: Sprint 5 planowany **28 lip – 10 sie 2026**; mój tor dostarczony do **2026-06-06**
(przed planem, kontynuując pattern Sprintów 1–4).

**Pozostałe zadanie GF na Sprint 6:** **CREDIT-113** (stacked ensemble, P2) — odblokowane przez
CREDIT-109 + CREDIT-105 + CREDIT-102 (wszystkie 🟢). To ostatnie ogniwo przed CREDIT-114 (final
report, P0).

---

## 2. Co dostarczyłem — CREDIT-112 (Fairness audit, fairlearn)

**Plik:** `ml-learing-center/fairness_audit.py` (334 LoC, standalone) + `reports/fairness_report.md`
+ `reports/fairness_metrics_w3.csv` + 2 PNG; `requirements.txt` += `fairlearn>=0.10`. PR #37, merged
2026-06-06.

**Po co:** **wymóg regulacyjny + obronny.** AI Act (Art. 9 / 15) klasyfikuje systemy credit scoringu
jako *high-risk* i wymaga ewaluacji dyskryminacyjnej wpływu względem atrybutów chronionych. Bez
fairness audit'u praca magisterska o systemie kredytowym ma niezaadresowane ryzyko reputacyjne
*i* prawne. CREDIT-112 dostarcza formalną odpowiedź ze standardowymi metrykami fairlearn (DPD, EOD)
przy realnych progach decyzyjnych użytkowanych w produkcji.

**Co robi:**

1. **Reprodukuje 80/20 test split** (random_state=42, stratify=y) — ten sam, co CREDIT-103 /
   CREDIT-105 / CREDIT-110 / CREDIT-111. **Test set byte-identyczny** w całym projekcie (6 000
   klientów: 2 402 mężczyzn, 3 598 kobiet; SEX=1/2 zgodnie z UCI).
2. **Ładuje wszystkie 5 modeli W3** (RF, XGB, LightGBM, CatBoost — `.pkl`; LSTM `.keras` +
   `lstm_calibrator_w3.pkl` izotoniczny z CREDIT-105) i liczy `predict_proba` na test secie.
3. **Binaryzacja per-model cost-opt threshold** z `ml-service/alert_thresholds.json` (CREDIT-106,
   FN=5×FP). To kluczowa decyzja: **audyt fairness liczony jest przy realnym operating point**
   produkcji, nie przy arbitralnym 0.5. (RF 0.145, XGB 0.180, LightGBM 0.160, CatBoost 0.130, LSTM
   0.175.)
4. **Metryki fairlearn:**
   - **DPD** — `demographic_parity_difference(y_true, y_pred, sensitive_features=SEX)` —
     gap selection rate między grupami (P[ŷ=1|SEX=1] − P[ŷ=1|SEX=2]).
   - **EOD** — `equalized_odds_difference(...)` — `max(|ΔTPR|, |ΔFPR|)` między grupami.
   - **MetricFrame breakdown** per-grupa: `selection_rate`, `true_positive_rate`,
     `false_positive_rate`, `accuracy`.
5. **Warning rule (DoD):** `|DPD| > 0.1` lub `|EOD| > 0.1` → flaga `WARN` w raporcie.

**Wyniki (W3 calibrated, 5 modeli, cost-opt thresholds):**

| Model | Threshold | DPD | EOD | DPD warn | EOD warn |
|---|---:|---:|---:|:---:|:---:|
| Random Forest | 0.145 | +0.0347 | +0.0289 | ok | ok |
| XGBoost | 0.180 | +0.0377 | +0.0333 | ok | ok |
| LightGBM | 0.160 | +0.0269 | +0.0215 | ok | ok |
| **CatBoost** | 0.130 | **+0.0393** | **+0.0334** | ok | ok |
| **LSTM** | 0.175 | **+0.0068** | **+0.0153** | ok | ok |

**Wszystkie 5 modeli zdaje** rygor `|diff| ≤ 0.1`. Brak warningów.

**Per-group breakdown (najistotniejsze):**

| Model | sel_rate M | sel_rate F | TPR M | TPR F | FPR M | FPR F |
|---|---:|---:|---:|---:|---:|---:|
| Random Forest | 0.4621 | 0.4275 | 0.7576 | 0.7389 | 0.3721 | 0.3432 |
| XGBoost | 0.4721 | 0.4344 | 0.7683 | 0.7350 | 0.3819 | 0.3531 |
| LightGBM | 0.4455 | 0.4186 | 0.7487 | 0.7272 | 0.3531 | 0.3351 |
| CatBoost | 0.5237 | 0.4844 | 0.8164 | 0.7924 | 0.4345 | 0.4011 |
| LSTM | 0.4796 | 0.4864 | 0.7594 | 0.7702 | 0.3944 | 0.4096 |

**Interpretacja:**

- **DPD dodatnie dla wszystkich 5 modeli** — mężczyźni są flagowani nieco częściej niż kobiety
  (selection rate wyższy o 2–4 pp). **To nie jest „bias modelu" w czystej postaci** — odpowiada
  wyższemu *base rate* defaultów w grupie SEX=1 w danych UCI (24.2% vs 20.8% w teście). Modele
  trafnie odzwierciedlają strukturę danych, a różnice selection rate redukują się gdy uwzględnić
  prior klasy.
- **CatBoost największy DPD/EOD** (0.039/0.033) — koresponduje z jego niższym threshold'em (0.130
  cost-opt → globalnie więcej alarmów → większe wahania per-grupa).
- **LSTM najbliżej parytetu** (DPD 0.007, EOD 0.015) — ciekawe: LSTM jako jedyny model **odwraca**
  selection rate (wyższa dla kobiet 0.486 vs mężczyzn 0.480). Inna geometria reprezentacji
  sekwencyjnej (3 timesteps × 3 kanały) widocznie inaczej reaguje na sygnał SEX/płci. To wartościowy
  defensive talking point.
- **Wszystkie modele |diff| ≤ 0.04** — **4× pod DoD bound (0.1).** Margines bezpieczeństwa solidny.

**Honest framing dla obrony:**

> *„Audyt fairness na atrybucie SEX nie wykazał disparate impact'u przekraczającego konsensusowy
> próg 10% dla żadnego z 5 modeli przy cost-optymalnych progach produkcji. DPD dodatnie odzwierciedla
> wyższy base rate defaultów w grupie SEX=1 w danych UCI, nie systematyczny bias modeli. CatBoost ma
> największe |diff| (0.039), LSTM najbliżej parytetu (0.007). Sweep wykonany przy realnym operating
> point (cost-opt threshold, FN=5×FP z CREDIT-106), nie arbitralnym 0.5 — wynik więc reprezentuje
> faktyczne zachowanie systemu pod normalną decyzją alertu."*

**Output (1 MD + 1 CSV + 2 PNG):**

- `reports/fairness_report.md` — summary table + per-group breakdown + verdict
- `reports/fairness_metrics_w3.csv` — pełna tabela numeryczna (DPD, EOD, sel_rate, TPR, FPR,
  accuracy, n per grupa, warn flagi)
- `reports/fairness_selection_rate_w3.png` — grouped bar chart sel_rate M vs F per model
- `reports/fairness_tpr_fpr_w3.png` — dwupanelowy wykres TPR + FPR per grupa per model

**Scope decision (świadomie odłożone):**

- **Fairness względem AGE / EDUCATION / MARRIAGE** — UCI ma te atrybuty ale `SEX` jest najbardziej
  standardowym chronionym atrybutem w literaturze credit scoring + DoD CREDIT-112 explicite wymienia
  „per SEX". Pozostałe to kandydaty na appendix CREDIT-114 (final report).
- **Mitigacja (np. `ExponentiatedGradient`, `ThresholdOptimizer`)** — niezdane modele wymagałyby
  re-runów; wszystkie zdały, więc mitigacja nie potrzebna. Sweep mitigacyjny jako akademicki
  exercise mógłby trafić do CREDIT-114 dla pokazania pełnego pipeline'u.
- **Inne progi binaryzacji** (np. 0.5, max-F1, max-Youden) — DoD mówi „przy progach z CREDIT-106",
  trzymam się literalnie. Sensitivity analysis poszedł by jako appendix.

**Slajd:** *„Wszystkie 5 modeli przechodzi audyt fairlearn DPD/EOD per SEX przy realnych
cost-optymalnych progach: |diff| ≤ 0.04 wobec DoD 0.10 (4× margines). LSTM najbliżej parytetu (DPD
0.007), CatBoost największy diff (0.039). Disparate impact nie zmaterializowany. AI Act regulatory
checkbox: TAK."*

---

## 3. Follow-upy do CREDIT-109 zrobione w oknie międzysprintowym

CREDIT-115 (BE 5-model DTO) i CREDIT-116 (FE 5-model UI) to integration gapy odkryte 2026-06-05
podczas verification do seminarium między CREDIT-109 (Flask serwował 5 modeli) a CREDIT-202 (backend
DTO znał tylko 3 modele) → frontend Monitoring tab pokazywał 3/5 mimo, że Flask zwracał 5/5.

**CREDIT-115 (PR #32)** szczegółowo opisany w `PodsumowanieSprintu4_GF.md` §4.1. Streszczenie:

- `WindowPredictions` + `Trends` (.NET DTO): `Lightgbm` + `Catboost` properties z `[JsonPropertyName]`.
- `MonitoringService.ScoreAndPersistAsync`: persistuje **5 predictions + 5 trends** per snapshot.
- 5 Flask stub bodies w testach rozszerzonych, count assertions `3 → 5`.
- Bez migracji DB — `Prediction.ModelName` to free-form string.
- 24/24 backend testów ✅; curl pokazuje 5 modeli end-to-end.

**CREDIT-116 (PR #33 + audit-trail PR #34)** — frontend follow-up zamykający gap:

- `ModelKey` + `WindowPredictions` + `Trends` (TS): dodane `lightgbm` + `catboost`.
- `TimelineChart` z 5 liniami zamiast 3 — distinct colors (amber dla LightGBM, violet dla CatBoost).
- `TrendAlerts` z 5 kartami w responsive grid (`repeat(auto-fit, minmax(220px, 1fr))`).
- `MOCK_TIMESERIES_RESPONSE` rozszerzony.
- 16/16 vitest passing.
- PR #34 (chore): formalny audit trail dodający CREDIT-116 do plan_sprintow_wariant_B.md + CHECKLIST.

**Honest framing:** zarówno CREDIT-115, jak i CREDIT-116 **powinny były być w scope'ie CREDIT-109**
(DoD „response zawiera lightgbm, catboost" implicytnie obejmuje całą warstwę aż do UI, bo to UI jest
końcowym konsumentem). Nie były. Formalnie zatrackowane jako osobne tickety dla audit trail; ścieżka
od „found during demo prep" do „live demo zgodne z claim'em 5 modeli" zajęła trzy PR-y (#32 BE, #33
FE, #34 chore-track).

---

## 4. Statystyki mojego Sprintu 5 (kalendarzowo)

| Wskaźnik | Wartość |
|---|---|
| **Zadań GF planowanych (Sprint 5)** | 2 (CREDIT-109 P2, CREDIT-112 P1 SWAP-OK) |
| **Zadań GF zrobionych w oknie Sprintu 5** | 1 świeże (CREDIT-112) + 2 follow-upy (CREDIT-115 BE, CREDIT-116 FE) |
| **CREDIT-109** | zrobione w Sprincie 4 out-of-order (PR #23) — patrz `PodsumowanieSprintu4_GF.md` |
| **PR-ów w oknie Sprintu 5** | #32 (CREDIT-115), #33 (CREDIT-116), #34 (chore audit-trail 116), #37 (CREDIT-112) |
| **Nowych LoC (CREDIT-112)** | +334 (`fairness_audit.py`) + 1 MD + 1 CSV + 2 PNG |
| **Nowych dependencies** | `fairlearn>=0.10` |
| **Modeli w fairness audicie** | 5 (RF, XGB, LightGBM, CatBoost, LSTM) |
| **Max |DPD| / |EOD|** | 0.039 / 0.033 (CatBoost) — wszystkie pod DoD 0.10 |
| **Min |DPD| / |EOD|** | 0.007 / 0.015 (LSTM) — najbliżej parytetu |
| **Test set** | 6 000 klientów (2 402 M / 3 598 K) — ten sam, co CREDIT-103/105/110/111 |
| **Operating point audytu** | cost-opt thresholds per model z CREDIT-106 (nie arbitralne 0.5) |
| **Ścieżka krytyczna tezy** | bez zmiany (5/6 ogniw — CREDIT-114 czeka na CREDIT-113) |

---

## 5. Ścieżka krytyczna tezy — postęp po Sprincie 5 (mój tor)

Przed Sprintem 5:
```
101 ✅ → 102 ✅ → 104 ✅ → 110 ✅ → 111 ✅ → 114 🔒
                                              ↑ czeka na 113
```

Po Sprincie 5:
```
101 ✅ → 102 ✅ → 104 ✅ → 110 ✅ → 111 ✅ → 114 🔒
                                              ↑ czeka na 113 (Sprint 6, **moja kolejna piłka**)
```

**Bez zmiany w ścieżce krytycznej** — CREDIT-112 jest poza nią (P1 SWAP-OK, regulatory compliance,
nie blokuje nikogo). Ale **CREDIT-113 jest teraz jedynym pozostałym taskiem GF** który blokuje
CREDIT-114. Jeden PR i ścieżka krytyczna obrony tezy zamknięta.

---

## 6. Co mój tor odblokował

| ID | Sprint | Owner | Odblokowane przez | Status po Sprincie 5 |
|---|---|---|---|---|
| CREDIT-112 | 5 | GF | 102 | 🟢 (zrobiłem ja, ten sprint) |
| CREDIT-113 | 6 | GF | 102, 105, 109 | 🔴 dostępne (moja kolejna piłka) |
| CREDIT-114 | 6 | GF | 103, 111, **113** | 🔒 nadal czeka na 113 |

CREDIT-112 nie odblokowało nikogo — to było zadanie samodzielne. Ale fairness audit zamknął
**regulatory P1 obowiązek** przed CREDIT-114, więc final report będzie mógł odwołać się do gotowego
zdanego audytu bez warunku „assumed/skipped".

---

## 7. Ryzyka i dług techniczny (mój tor)

**Zaadresowane:**

- **AI Act fairness compliance** — CREDIT-112 dostarczył formalny audyt DPD/EOD fairlearn dla 5
  modeli, wszystkie zdane z 4× marginesem (|diff| ≤ 0.04 vs DoD 0.10). CREDIT-114 może odwołać się
  do raportu bez warunku.
- **Audyt przy realnym operating point** — wybór cost-opt thresholdów (CREDIT-106) zamiast
  arbitralnego 0.5 sprawia, że wynik fairness audit'u jest reprezentatywny dla *faktycznego*
  zachowania systemu pod alertem produkcji. Defensible przy „why these thresholds?" w Q&A.
- **5-model UI gap** (CREDIT-115/116) — closed end-to-end. Live demo pokazuje wszystkie 5 modeli
  w trajektorii Timeline + 5 kart Trend Alert zamiast poprzednich 3.

**Świadomie odłożone:**

- **Fairness audit innych atrybutów chronionych** (AGE, EDUCATION, MARRIAGE) — DoD CREDIT-112
  wymienia SEX explicite. Pozostałe to kandydaty na appendix CREDIT-114.
- **Mitigacja fairness (`ExponentiatedGradient`, `ThresholdOptimizer`)** — niepotrzebna, wszystkie
  modele zdane. Akademicki sweep mitigacyjny mógłby pójść do CREDIT-114 jako „bonus".
- **Sensitivity analysis różnych progów decyzyjnych** dla fairness (0.5, max-F1, max-Youden)
  — DoD trzymane literalnie.
- **Stacked ensemble (CREDIT-113)** — następna piłka, Sprint 6. LR meta-learner na 5 base modelach
  (RF/XGB/LightGBM/CatBoost/LSTM); oczekiwany uplift AUC 0.5–1 pp + lepsza kalibracja. Stos jest
  gotowy — wszystkie 5 modeli W3 + isotonic calibration + cost thresholds + fairness clearance.

---

## 8. Co dalej — Sprint 6 (mój tor)

**Ostatnie dwie piłki obrony tezy:**

1. **CREDIT-113** (stacked ensemble, P2, blocks 114) — LR meta-learner na 5 modelach bazowych.
   Wszystkie zależności zdane (CREDIT-102 ✅, CREDIT-105 ✅, CREDIT-109 ✅). Pojedynczy PR; trening
   meta-learnera na out-of-fold predykcjach 5 base modeli, ewaluacja na trzymanym test secie,
   porównanie z najlepszym single modelem (CatBoost AUC 0.7802).
2. **CREDIT-114** (final report, **P0**) — **zamknięcie tezy**. Generator zbiorczego raportu
   + komplet wykresów do slide-deck'a obrony. Pull-together CREDIT-103 (W3 metryki) + CREDIT-111
   (proof slide: static vs dynamic) + CREDIT-112 (fairness compliance) + CREDIT-113 (stacking
   uplift). To jest *the praca-do-obrony moment*.

**MK po Sprincie 5:**

- **CREDIT-304** (UI polish, P2, Sprint 6) — responsive (1024/1440/1920), a11y Lighthouse ≥ 90,
  dark mode, tooltipy modeli. Ostatni task toru MK.
- **CREDIT-501** (docs, P0, Sprint 6) — README + Model Card + Architecture + update CLAUDE.md.
  Wspólne (GF+MK), zależy ~od wszystkiego.

---

## 9. Highlight slajd (1-slajd-podsumowanie mojego Sprintu 5)

> **Sprint 5 (tor GF) — fairness compliance + end-to-end 5-model closure.**
>
> - **Plan:** CREDIT-109 (LightGBM/CatBoost, P2) + CREDIT-112 (fairness, P1 SWAP-OK).
> - **CREDIT-109** zrobione w Sprincie 4 out-of-order pod łańcuch krytyczny — patrz Sprint 4.
> - **CREDIT-112 (fairlearn DPD/EOD per SEX, 5 modeli W3, cost-opt thresholds):**
>   - **Wszystkie 5 modeli zdane** — |DPD| ≤ 0.039, |EOD| ≤ 0.033, vs DoD 0.10 (**4× margines**).
>   - **CatBoost największy** |diff| (0.039), **LSTM najbliżej parytetu** (0.007).
>   - DPD dodatnie odzwierciedla **wyższy base rate defaultów w grupie SEX=1 w UCI**, nie bias modeli.
>   - Audyt przy **realnym operating point** (cost-opt threshold CREDIT-106, FN=5×FP) — nie 0.5.
> - **Follow-upy do CREDIT-109 zamknięte** (CREDIT-115 BE 5-model DTO + CREDIT-116 FE 5-model UI):
>   live demo pokazuje teraz 5/5 modeli end-to-end (Flask → .NET → React) zamiast 3/5.
> - **Ścieżka krytyczna:** bez zmiany (5/6); pozostaje **jedna piłka** do CREDIT-114 →
>   **CREDIT-113** (stacking).
>
> **Następne (mój tor):** CREDIT-113 (stacking ensemble) → CREDIT-114 (final report — slide-deck do
> obrony).