   # Use Fable 5 Before It's Gone

A curated shortlist of tasks in **this** repo where Claude **Fable 5** genuinely
earns its cost — plus foolproof, ready-to-paste prompts for each.

Fable 5 is Anthropic's most capable model: built for the hardest reasoning,
long-horizon autonomous work, and end-to-end analytical deliverables (reports,
methodology, docs). It is also the most token-hungry model on the Pro plan and
runs multi-minute turns. So this is not a "switch everything to Fable 5" list —
it's the handful of tasks where depth changes the outcome.

---

## How to use this file

1. Switch model with `/model` → **Fable 5** before running one of these.
2. Paste the **whole** prompt in one message. Fable 5 rewards a complete,
   well-specified brief and runs autonomously — do **not** drip-feed it steps.
3. For the hard reasoning tasks, mention "work at high effort" (it has headroom
   the cheaper models don't).
4. Expect long turns (several minutes on the big ones). That's normal, not a hang.
5. Switch back to **Opus 4.8** for everyday edits once the heavy run is done.

### Reserve Fable 5 for these — don't waste it on
Routine edits, `CHECKLIST.md` / sprint-summary updates, commit messages, lint
fixes, single-file bugfixes, renaming, boilerplate tests. Opus 4.8 (or Sonnet 4.6)
gives you the same result for a fraction of your weekly cap.

> ⚠️ **One caveat:** Fable 5's safety classifier refuses security-/cyber-focused
> analysis. For a credit-risk ML repo this won't bite you — just don't ask it to,
> e.g., "find ways to exploit the API."

---

## Task 1 — Adversarial thesis-defense review (methodology vs. implementation)

**What it's about.** Have Fable 5 play a hostile examiner: attack the
methodology in your thesis against what the code *actually* does, and surface
every claim that the implementation doesn't back up. This complements
`DokumentRoznice.md` (thesis-vs-project diff you already started) but goes
deeper — it looks for *defensible* weaknesses, not just textual differences.
This is Fable 5's sweet spot: willing to push back, strong at repo reasoning.

**Prompt:**

```text
You are my master's-thesis examiner and you are skeptical. Your job is to find
every weakness a committee could attack at the defense.

Context:
- This repo is a credit-card default risk prediction system: a 5-model ensemble
  (Random Forest, XGBoost, LSTM, LightGBM, CatBoost) served by a Flask ML
  service, orchestrated by a .NET 8 backend, with a React frontend.
- The thesis is "Praca Magisterska-8.pdf" (latest version).
- Supporting docs: WalidacjaPDFv7.md (validation), DokumentRoznice.md
  (thesis-vs-code diff), and the PodsumowanieSprintu*.md sprint summaries.

Work at high effort. Do this:
1. Read the thesis PDF and the docs above.
2. Cross-check the thesis's core claims (about the models, the sliding-window
   approach, the fairness audit, and the evaluation methodology) against the
   actual code in ml-learing-center/ and ml-service/.
3. Produce a table of findings. For each: the thesis claim, what the code shows,
   the gap, severity (high/med/low), and how I should respond if challenged.
4. List the 5 hardest questions the committee is likely to ask, with a strong
   suggested answer for each.

Report every concern including ones you're unsure about — I will filter. Do not
soften findings to be polite.
```

---

## Task 2 — Fairness results: interpretation + mitigation recommendation

**What it's about.** You have DPD/EOD (demographic parity difference / equalized
odds difference) w.r.t. SEX across the 5 W3 models (Sprint 5, `fairness_audit.py`
via fairlearn). Numbers alone don't defend a thesis — the *interpretation* does.
Fable 5 is strong at exactly this kind of open, high-stakes reasoning: which
model is most defensible for a credit decision, and which mitigation to argue for.

**Prompt:**

```text
Work at high effort. You are helping me write and defend the fairness section of
a master's thesis on credit-default prediction.

Read ml-learing-center/fairness_audit.py and any fairness outputs it writes
(check ml-learing-center/reports/ and thesis_figures/). The audit computes
Demographic Parity Difference (DPD) and Equalized Odds Difference (EOD) with
respect to SEX, using fairlearn, for 5 models: Random Forest, XGBoost, LSTM,
LightGBM, CatBoost (the "_w3" sliding-window variants).

Then:
1. Summarize what the DPD/EOD numbers actually say about each model — in plain,
   defensible language, not just restating the numbers.
2. Rank the 5 models by how defensible each is for a real credit-lending
   decision, weighing fairness against predictive performance. Justify the ranking.
3. Recommend ONE mitigation strategy (e.g. reweighting, threshold optimization
   via fairlearn's ThresholdOptimizer, or post-processing) and explain WHY it
   fits this dataset and this legal/ethical context, plus its trade-offs.
4. Give me 3–4 paragraphs of thesis-ready prose (English) interpreting the
   results and justifying the recommendation.

Be precise about the difference between demographic parity and equalized odds and
why the choice between them matters for lending.
```

---

## Task 3 — Pre-defense correctness bug hunt (risk-critical code)

**What it's about.** Before the defense, get a deep read of the code paths that
would be embarrassing if wrong: feature engineering, the LSTM `(1, 6, 3)` tensor
prep, and the pre-saved scaler application. Fable 5 has higher bug-finding recall
than lighter models — but it obeys "only report serious issues" too literally, so
the prompt explicitly tells it to report everything and let you filter.

**Prompt:**

```text
Work at high effort. Do a rigorous correctness review of the risk-critical ML
code in this repo. I need this solid before my thesis defense.

Focus files:
- ml-service/features.py and ml-service/app.py — the engineer_features() logic
  (payment stats, bill trends, utilization rate, late counts) and the
  prepare_lstm_input() that shapes 6-month sequences into a (1, 6, 3) tensor.
- ml-service/sliding_window.py — the 3-month window logic.
- The scaler handling: lstm_scalers_w3.pkl / scaler_w3.pkl are pre-saved and
  applied at inference, NOT re-fit. Verify that's actually what the code does.

Check specifically for:
- Feature-order or column-alignment mismatches between training
  (ml-learing-center/) and inference (ml-service/).
- Off-by-one or wrong-axis errors in the 6-month sequence / (1, 6, 3) reshape.
- Train/inference skew in scaling (any accidental re-fit, wrong scaler, or
  leakage).
- NaN / division-by-zero in derived features (e.g. utilization rate).

Report EVERY finding you're not certain is fine, with: file:line, the concern,
a confidence level, a severity, and a concrete fix. Do not pre-filter for
importance — I'll do that. This is not a security review; focus on correctness.
```

---

## Task 4 — Wariant B sliding-window: end-to-end design + build

**What it's about.** Your Sprint 1 focus (`plan_sprintow_wariant_B.md`): the
3-month sliding-window + DB feature, spanning the Flask ML service, the .NET
orchestrator, and the React frontend. Multi-file, three languages, long-horizon —
this is precisely what Fable 5's autonomous agentic mode is built for, **if** you
hand it the full spec upfront.

**Prompt:**

```text
Work at high effort and autonomously. I want you to design and then implement the
"Wariant B" sliding-window feature described in plan_sprintow_wariant_B.md.

Read first: plan_sprintow_wariant_B.md, CLAUDE.md, and the existing sliding-window
code (ml-service/sliding_window.py, ml-learing-center/sliding_window.py) and the
monitoring/snapshot flow (backend/WebApi/Services/MonitoringService.cs,
SnapshotRepository.cs, and frontend SnapshotForm.tsx / TimelineChart.tsx).

Goal: a 3-month sliding-window prediction path backed by the database, working
end to end across the stack:
- Flask ML service (ml-service/): window construction + the _w3 models.
- .NET backend (backend/WebApi/): DTOs, controller, service, persistence.
- React frontend (frontend/WebApp/src/): the UI to drive and display it.

Do this in order:
1. Give me a short design: data flow, the DB schema/changes needed, the new/edited
   endpoints, and where each layer changes. Stop and let me confirm.
2. After I confirm, implement it, keeping the existing 22-field camelCase (.NET)
   ↔ snake_case (Flask) mapping convention intact.
3. Update or add tests (pytest in ml-service/tests, xUnit in backend/WebApi.Tests,
   vitest in frontend) and tell me exactly how to run them.

Follow the existing patterns in each layer. Don't over-engineer or add features
beyond the Wariant B spec.
```

---

## Task 5 — Thesis results / discussion section (deep writing)

**What it's about.** Fable 5 is explicitly tuned for end-to-end analytical
writing. Hand it your actual evaluation outputs and have it write the
results-and-discussion prose — interpreting, comparing, and defending — rather
than just formatting. This is the highest word-for-word payoff for a thesis.

**Prompt:**

```text
Work at high effort. Help me write the Results & Discussion section of my
master's thesis on credit-default prediction.

Read the evaluation code and its outputs:
- ml-learing-center/evaluation.py, timeseries_eval.py, static_vs_dynamic.py,
  optimize_thresholds.py, optuna_tuning.py.
- Their outputs in ml-learing-center/reports/ and ml-learing-center/thesis_figures/.
- WalidacjaPDFv7.md for the validation framing I've already established.

Then write thesis-grade English prose that:
1. Reports the performance of all 5 models (RF, XGBoost, LSTM, LightGBM, CatBoost)
   on the relevant metrics, and interprets — not just lists — the differences.
2. Argues the static-vs-dynamic (sliding-window) comparison: does the evidence
   actually justify the dynamic approach? Be honest if it's marginal.
3. Discusses threshold optimization and hyperparameter tuning (Optuna) and what
   they changed.
4. States limitations and threats to validity like a careful researcher would.

Match the tone of WalidacjaPDFv7.md. Lead each subsection with the finding, then
the evidence. Flag anywhere the data doesn't fully support a claim I might want
to make.
```

---

## Task 6 — Cross-stack consistency audit (the 22-field / 5-model contract)

**What it's about.** The request contract (22 fields) and the 5-model prediction
response cross three languages: React types → .NET DTOs → Flask JSON. Drift
between these layers is a classic source of silent bugs. Fable 5 can hold all
three layers in context at once and check them against each other — a task that
frustrates lighter models.

**Prompt:**

```text
Work at high effort. Audit the end-to-end data contract of this system for any
mismatch across the three layers. Trace it, don't skim.

The contract flows:
- Frontend: frontend/WebApp/src/types/prediction.ts, types/monitoring.ts,
  components/InputForm.tsx, api/predictApi.ts, api/monitoringApi.ts.
- Backend: backend/WebApi/Models/PredictRequest.cs, FlaskPredictRequest.cs,
  PredictResponse.cs, and the monitoring DTOs; Controllers/PredictController.cs,
  MonitoringController.cs; Services/PythonModelClient.cs, PredictionService.cs.
- ML service: ml-service/app.py (request parsing and the JSON response with all
  5 models).

Verify:
1. All 22 input fields line up field-for-field through React → .NET (camelCase)
   → Flask (snake_case), with correct types and the documented validation ranges
   (age 18–100, limit 10K–1M, education 1–4, etc.).
2. The 5-model prediction response (RF, XGBoost, LSTM, LightGBM, CatBoost) is
   passed through faithfully at every layer — no model silently dropped, renamed,
   or mislabeled.
3. The monitoring/timeseries and SHAP pass-through DTOs are consistent end to end.

Output a table of every mismatch or risk with file:line on each side and a fix.
If everything lines up, say so explicitly per section — don't assume.
```

---

## Task 7 — Static vs. dynamic: is the sliding-window claim actually justified?

**What it's about.** A core thesis claim is presumably that the dynamic
(sliding-window) approach beats the static one. This is the single claim most
likely to be attacked. Have Fable 5 stress-test it against the real experimental
code and outputs — as a statistician, not a cheerleader.

**Prompt:**

```text
Work at high effort. Act as a rigorous, skeptical statistician reviewing one
central claim of my thesis: that the dynamic sliding-window approach outperforms
the static baseline for credit-default prediction.

Read ml-learing-center/static_vs_dynamic.py, timeseries_eval.py,
sliding_window.py, sliding_window_test.py, and any results they produce in
reports/ and thesis_figures/.

Assess honestly:
1. What does the experiment actually measure, and is the comparison fair (same
   data splits, same metrics, no leakage from the windowing)?
2. Is the performance difference real and meaningful, or within noise? Comment on
   effect size and whether any significance testing is warranted/present.
3. What's the strongest counter-argument a reviewer could make against the
   dynamic approach, and how would I rebut it?
4. Give me a bottom-line verdict: is the claim defensible as written, needs
   softening, or needs more evidence? If softening, propose the exact wording.

Be blunt. I'd rather find the hole now than at the defense.
```

---

## Quick reference

| # | Task | Best effort | Rough budget |
|---|------|-------------|--------------|
| 1 | Adversarial defense review | high | medium–large |
| 2 | Fairness interpretation | high | medium |
| 3 | Correctness bug hunt | high | medium |
| 4 | Wariant B end-to-end build | high/xhigh | large |
| 5 | Results/discussion writing | high | medium |
| 6 | Cross-stack contract audit | high | medium |
| 7 | Static-vs-dynamic stress test | high | small–medium |

**Budget order if you can only run a few:** 1 and 2 first (highest thesis payoff),
then 3 (cheap insurance before the defense), then 4 when you're ready for the big
build.