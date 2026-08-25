"""
B3 (Fable5-zmiany.md Task1 / plan 2026-07-07): bootstrap variance of test AUC.

Delivers the "40 bootstrapped repetitions of the test set" promised by thesis
section 4.5. Reuses the exact prediction pipeline of the fairness audit
(load_test_split), resamples the 6000-row test set with replacement 40 times
(seed=42) and reports mean / std / 95% percentile CI of AUC per model, plus
which pairwise model differences are separable at this sample size.

Outputs:
    reports/bootstrap_auc_w3.csv      (40 rows x 5 models)
    reports/bootstrap_auc_w3.png      (boxplot)
    reports/bootstrap_auc_report.md
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

from fairness_audit import MODELS, load_test_split

HERE = Path(__file__).parent
REPORTS = HERE / "reports"
N_BOOT = 40
SEED = 42


def main() -> None:
    print("Scoring the test split once (reusing fairness_audit.load_test_split)...")
    preds, _sex = load_test_split()
    y = preds[MODELS[0]]["y_true"]
    n = len(y)

    rng = np.random.default_rng(SEED)
    rows = []
    for b in range(N_BOOT):
        idx = rng.integers(0, n, size=n)
        # Guard against a degenerate resample with a single class (n=6000 -> ~impossible).
        if len(np.unique(y[idx])) < 2:
            idx = rng.integers(0, n, size=n)
        rows.append({
            "bootstrap": b,
            **{m: roc_auc_score(y[idx], preds[m]["y_prob"][idx]) for m in MODELS},
        })
    boot = pd.DataFrame(rows)
    boot.to_csv(REPORTS / "bootstrap_auc_w3.csv", index=False)

    # Point estimates on the full test set for reference.
    point = {m: roc_auc_score(y, preds[m]["y_prob"]) for m in MODELS}

    lines = [
        "# B3: Bootstrap wariancji AUC (40 powtórzeń zbioru testowego)",
        "",
        f"Repróbkowanie ze zwracaniem, n={n}, {N_BOOT} powtórzeń, seed={SEED}. "
        "Realizacja obietnicy z sekcji 4.5 pracy.",
        "",
        "| Model | AUC (pełny test) | Bootstrap mean | Std | 95% CI |",
        "|---|---:|---:|---:|---|",
    ]
    for m in MODELS:
        v = boot[m].to_numpy()
        lo, hi = np.percentile(v, [2.5, 97.5])
        lines.append(
            f"| {m} | {point[m]:.4f} | {v.mean():.4f} | {v.std(ddof=1):.4f} "
            f"| [{lo:.4f}, {hi:.4f}] |"
        )

    # Pairwise separability via bootstrap of the AUC DIFFERENCE (paired resamples).
    lines += [
        "",
        "## Rozróżnialność par modeli (bootstrap sparowany różnicy AUC)",
        "",
        "| Para | Δ AUC (mean) | 95% CI różnicy | CI zawiera 0? |",
        "|---|---:|---|---|",
    ]
    for i, a in enumerate(MODELS):
        for b_name in MODELS[i + 1:]:
            diff = boot[a].to_numpy() - boot[b_name].to_numpy()
            lo, hi = np.percentile(diff, [2.5, 97.5])
            sep = "nie — **rozróżnialne**" if (lo > 0 or hi < 0) else "tak — nierozróżnialne"
            lines.append(f"| {a} vs {b_name} | {diff.mean():+.4f} | [{lo:+.4f}, {hi:+.4f}] | {sep} |")

    lines += [
        "",
        "**Wniosek do pracy:** różnice między modelami drzewiastymi raportować jako "
        "porównywalne, chyba że CI różnicy nie zawiera zera (patrz tabela); przewaga "
        "nad LSTM jest oczekiwanie stabilna. Uwaga metodologiczna: bootstrap "
        "repróbkuje wyłącznie zbiór testowy przy ustalonych modelach — nie obejmuje "
        "wariancji treningu.",
        "",
    ]
    (REPORTS / "bootstrap_auc_report.md").write_text("\n".join(lines), encoding="utf-8")

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.boxplot([boot[m] for m in MODELS], tick_labels=MODELS, showfliers=False)
    ax.set_ylabel("AUC (bootstrap, test)")
    ax.set_title(f"Bootstrap AUC — {N_BOOT} powtórzeń zbioru testowego (n={n})")
    ax.grid(axis="y", linestyle=":", linewidth=0.5)
    plt.tight_layout()
    plt.savefig(REPORTS / "bootstrap_auc_w3.png", dpi=120)
    plt.close()

    print("Saved: bootstrap_auc_w3.csv, bootstrap_auc_report.md, bootstrap_auc_w3.png")


if __name__ == "__main__":
    main()
