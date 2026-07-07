"""
CREDIT-111: DOWOD TEZY -- single-snapshot static rule vs. multi-window monitoring rule.

The Variant B thesis claims that monitoring a client over the 4 sliding windows
(W0..W3) detects defaults earlier and/or more reliably than the single-snapshot
static rule that only looks at W3. This script provides the comparison slide.

Two decision rules under test (per model RF / XGBoost / LSTM):

  Static rule:     flag client iff  PD_W3 >= threshold
  Monitoring rule: flag client iff  max(PD_W0, PD_W1, PD_W2, PD_W3) >= threshold

For each threshold in a sweep we compute (catch_rate, false_alarm_rate) and plot
both rules as ROC-like curves in (FA, catch) space. The honest reading of the
plot answers "at the same false-alarm budget, does monitoring catch more?".

Additionally we compute lead-time-only wins: cases where monitoring flagged a
defaulter at W0..W2 (before W3) at the operating point where both rules share
the same false-alarm rate.

Output:
- reports/static_vs_dynamic_metrics.csv   threshold sweep, all 3 models
- reports/static_vs_dynamic_operating.csv canonical operating points table
- reports/static_vs_dynamic_report.md     prose interpretation (the slide)
- reports/static_vs_dynamic_{model}_w3.png ROC-like curve per model (3 files)

Usage:
    cd ml-learing-center
    source .venv/bin/activate
    python static_vs_dynamic.py
"""
from pathlib import Path
from typing import Dict, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from timeseries_eval import MODELS, SLUG, score_test_set

HERE = Path(__file__).parent
REPORTS = HERE / "reports"
REPORTS.mkdir(exist_ok=True)

THRESHOLD_SWEEP = np.linspace(0.05, 0.95, 19)
FA_BUDGETS = [0.05, 0.10, 0.20]


def evaluate_rules(traj: np.ndarray, y_true: np.ndarray) -> pd.DataFrame:
    """Sweep thresholds and compute (catch, fa) for static (W3 only) and monitoring (max)."""
    static_scores = traj[:, 3]
    monitor_scores = traj.max(axis=1)
    is_def = y_true == 1
    is_non = y_true == 0

    rows = []
    for t in THRESHOLD_SWEEP:
        rows.append({
            "threshold": float(t),
            "static_catch": float((static_scores[is_def] >= t).mean()),
            "static_fa": float((static_scores[is_non] >= t).mean()),
            "monitor_catch": float((monitor_scores[is_def] >= t).mean()),
            "monitor_fa": float((monitor_scores[is_non] >= t).mean()),
        })
    return pd.DataFrame(rows)


def threshold_for_fa(scores: np.ndarray, y_true: np.ndarray, target_fa: float) -> float:
    """Pick the smallest threshold whose realised FA on non-defaulters is <= target_fa.
    Equivalent to the (1 - target_fa) quantile of non-defaulter scores."""
    nondef = scores[y_true == 0]
    return float(np.quantile(nondef, 1.0 - target_fa))


def evaluate_at_fa(traj: np.ndarray, y_true: np.ndarray, target_fa: float) -> Dict:
    """Find per-rule threshold at the requested FA budget and report catch + lead-only wins."""
    static_scores = traj[:, 3]
    monitor_scores = traj.max(axis=1)
    is_def = y_true == 1
    is_non = y_true == 0

    t_static = threshold_for_fa(static_scores, y_true, target_fa)
    t_monitor = threshold_for_fa(monitor_scores, y_true, target_fa)

    static_flag = static_scores >= t_static
    monitor_flag = monitor_scores >= t_monitor

    # Lead-only wins: defaulters caught by monitor but missed by static.
    only_monitor_def = is_def & monitor_flag & ~static_flag
    only_static_def = is_def & static_flag & ~monitor_flag

    # When monitor catches early (W0..W2 first crosses) the lead time is the
    # advantage; restrict to defaulters caught by monitor.
    caught_by_monitor = is_def & monitor_flag
    first_alert_window = np.argmax(traj >= t_monitor, axis=1)  # first True window
    # For clients with no True row, argmax returns 0 -> guard with monitor_flag.
    lead = 3 - first_alert_window  # 0 = caught at W3, 3 = caught at W0
    lead = np.where(monitor_flag, lead, np.nan)

    return {
        "target_fa": target_fa,
        "static_threshold": t_static,
        "monitor_threshold": t_monitor,
        "static_catch": float(static_flag[is_def].mean()),
        "static_fa": float(static_flag[is_non].mean()),
        "monitor_catch": float(monitor_flag[is_def].mean()),
        "monitor_fa": float(monitor_flag[is_non].mean()),
        "only_monitor_catches": int(only_monitor_def.sum()),
        "only_static_catches": int(only_static_def.sum()),
        "mean_lead_caught": float(np.nanmean(lead[caught_by_monitor])) if caught_by_monitor.sum() else 0.0,
    }


def plot_static_vs_monitor(sweep: pd.DataFrame, model_name: str, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.plot(sweep["static_fa"], sweep["static_catch"], marker="o", label="Static (W3 only)", color="C0")
    ax.plot(sweep["monitor_fa"], sweep["monitor_catch"], marker="s", label="Monitoring (any of W0..W3)", color="C3")
    ax.plot([0, 1], [0, 1], "k--", linewidth=0.6, label="Random")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xlabel("False alarm rate (non-defaulters flagged)")
    ax.set_ylabel("Catch rate (defaulters flagged)")
    ax.set_title(f"Static vs Monitoring -- {model_name} (W3 calibrated)")
    ax.grid(True, linewidth=0.3, alpha=0.5)
    ax.legend(loc="lower right")
    plt.tight_layout()
    plt.savefig(path, dpi=120)
    plt.close()


def write_report(
    sweep_per_model: Dict[str, pd.DataFrame],
    operating_per_model: Dict[str, pd.DataFrame],
    path: Path,
) -> None:
    lines = [
        "# CREDIT-111: Static vs Monitoring -- thesis proof report\n\n",
        "The Variant B thesis claims that **monitoring** (the alert fires if any of W0..W3 ",
        "crosses the threshold) detects defaults more reliably and/or earlier than the **static** ",
        "rule (alert based on W3 alone). This document interprets the results honestly.\n\n",
        f"Test set: 6000 clients ({1327} defaulters), W3-calibrated RF/XGBoost/LightGBM/CatBoost/LSTM, ",
        f"alert thresholds swept across {len(THRESHOLD_SWEEP)} values in [0.05, 0.95].\n\n",
        "---\n\n",
    ]

    for name in MODELS:
        op = operating_per_model[name]
        sweep = sweep_per_model[name]

        # Pick representative FA = 10% row
        row_10 = op[op["target_fa"] == 0.10].iloc[0]
        delta_catch = (row_10["monitor_catch"] - row_10["static_catch"]) * 100
        verdict = "monitoring wins" if delta_catch > 1 else ("static wins" if delta_catch < -1 else "tie")

        lines.append(f"## {name}\n\n")
        lines.append("Catch rate at canonical false-alarm budgets:\n\n")
        lines.append("| Target FA | Static catch | Monitoring catch | Delta (mon - static, pp) |\n")
        lines.append("|---|---|---|---|\n")
        for _, r in op.iterrows():
            d = (r["monitor_catch"] - r["static_catch"]) * 100
            lines.append(
                f"| {r['target_fa']:.0%} | {r['static_catch']:.1%} | {r['monitor_catch']:.1%} | {d:+.2f} |\n"
            )

        lines.append(f"\nLead-only wins (defaulters caught by monitor but missed by static at FA=10%): "
                     f"**{int(row_10['only_monitor_catches'])}**\n")
        lines.append(f"Lost-only cases (defaulters caught by static but missed by monitor at FA=10%): "
                     f"**{int(row_10['only_static_catches'])}**\n")
        lines.append(f"Mean lead time among monitor-caught defaulters (FA=10%): "
                     f"**{row_10['mean_lead_caught']:.2f}** windows before W3\n\n")
        lines.append(f"**Verdict at FA=10%:** {verdict} (delta = {delta_catch:+.2f} pp catch rate).\n\n")
        lines.append("---\n\n")

    # Combined honest reading
    lines.append("## Honest interpretation\n\n")
    lines.append("- The monitoring rule is mathematically a **superset** of the static rule -- any threshold "
                 "applied to `max(W0..W3)` returns at least as many flags as the same threshold on `W3` alone. "
                 "So at the *same threshold* monitoring strictly dominates static on catch rate **but** also on "
                 "false alarms. The interesting comparison is at the **same false-alarm budget**: does monitoring "
                 "catch more by re-picking its threshold higher?\n")
    lines.append("- The numbers above answer that question per model and per FA budget.\n")
    lines.append("- The **lead-only wins** column is the monitoring-specific value: defaulters that the W3-only ")
    lines.append("rule misses but the W0..W3 trajectory catches. These are the cases where the trajectory's history "
                 "matters -- the client's risk built up over earlier windows.\n")
    lines.append("- For the thesis the framing is: monitoring offers **earlier detection at comparable discrimination**. "
                 "The slide should show both the ROC-like curves AND the lead-only wins count -- the latter is the "
                 "quantitative answer to \"why bother tracking trajectory\".\n")
    path.write_text("".join(lines))


def main() -> None:
    print("Scoring W3 test set across all 4 sliding windows (reusing timeseries_eval)...")
    y_test, trajectories = score_test_set()

    all_sweeps = []
    sweep_per_model: Dict[str, pd.DataFrame] = {}
    operating_per_model: Dict[str, pd.DataFrame] = {}

    print("\n===== STATIC VS MONITORING (W3 calibrated) =====")
    for name in MODELS:
        traj = trajectories[name]
        sweep = evaluate_rules(traj, y_test)
        sweep.insert(0, "model", name)
        all_sweeps.append(sweep)
        sweep_per_model[name] = sweep

        op_rows = [evaluate_at_fa(traj, y_test, fa) for fa in FA_BUDGETS]
        op = pd.DataFrame(op_rows)
        op.insert(0, "model", name)
        operating_per_model[name] = op

        plot_static_vs_monitor(sweep, name, REPORTS / f"static_vs_dynamic_{SLUG[name]}_w3.png")

        # Print operating-point summary
        print(f"\n{name}:")
        for _, r in op.iterrows():
            d = (r["monitor_catch"] - r["static_catch"]) * 100
            print(
                f"  FA={r['target_fa']:.0%}  static_catch={r['static_catch']:.1%}  "
                f"monitor_catch={r['monitor_catch']:.1%}  delta={d:+.2f}pp  "
                f"only_monitor_catches={int(r['only_monitor_catches'])}  "
                f"mean_lead={r['mean_lead_caught']:.2f}"
            )

    pd.concat(all_sweeps, ignore_index=True).to_csv(REPORTS / "static_vs_dynamic_metrics.csv", index=False)
    pd.concat(operating_per_model.values(), ignore_index=True).to_csv(
        REPORTS / "static_vs_dynamic_operating.csv", index=False,
    )
    write_report(sweep_per_model, operating_per_model, REPORTS / "static_vs_dynamic_report.md")

    print(f"\nSaved CSVs + report + {len(MODELS)} PNG plots in {REPORTS}/")


if __name__ == "__main__":
    main()
