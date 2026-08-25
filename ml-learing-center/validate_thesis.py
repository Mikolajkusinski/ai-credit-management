"""Walidator PDF pracy magisterskiej (lista R3 z Fable5-zmiany.md).

Użycie:
    .venv/bin/python validate_thesis.py "../Praca Magisterska-9.pdf"

Ekstrahuje tekst PDF-a, uruchamia ~15 checków (struktura, wymagana zawartość,
zakazane relikty starej metodologii, liczby zgodne z kanonicznymi CSV)
i zapisuje raport WalidacjaPDFv9.md obok PDF-a. Exit 1, gdy jakikolwiek
check jest czerwony — pętla składu iteruje do exit 0.
"""
from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass
class Check:
    id: str
    ok: bool
    description: str
    detail: str = ""


def _num_variants(v: float, nd: int = 4) -> list[str]:
    """Warianty zapisu liczby: kropka/przecinek, 4 i 3 miejsca (PDF-y używają przecinka)."""
    s4 = f"{v:.{nd}f}"
    s3 = f"{v:.3f}"
    return [s4, s4.replace(".", ","), s3, s3.replace(".", ",")]


def _section_len(text: str, start_pat: str, end_pat: str) -> int:
    m1 = re.search(start_pat, text)
    m2 = re.search(end_pat, text[m1.end():]) if m1 else None
    if not m1 or not m2:
        return 0
    return len(text[m1.end():m1.end() + m2.start()].strip())


def run_checks(text: str, reports_dir: Path) -> list[Check]:
    metrics = pd.read_csv(reports_dir / "metrics_w3.csv").set_index("model")
    with open(reports_dir.parent.parent / "ml-service" / "alert_thresholds.json") as f:
        thr = json.load(f)
    checks: list[Check] = []

    def add(cid, ok, desc, detail=""):
        checks.append(Check(cid, bool(ok), desc, detail))

    def contains_any(variants):
        return any(v in text for v in variants)

    # — struktura (niepuste rozdziały) —
    add("ch3_nonempty", _section_len(text, r"Rozdział 3\.", r"Rozdział 4\.") > 5000,
        "Rozdział 3 ma treść (>5000 znaków)")
    add("ch5_nonempty", _section_len(text, r"Rozdział 5\.", r"Zakończenie") > 8000,
        "Rozdział 5 ma treść (>8000 znaków)")
    add("zakonczenie_nonempty", _section_len(text, r"Zakończenie", r"Bibliografia") > 1000,
        "Zakończenie ma treść (>1000 znaków)")
    # — wymagana zawartość —
    add("hipotezy", all(h in text for h in ["H1", "H2", "H3"]),
        "Hipotezy H1/H2/H3 obecne")
    add("split_602020", "60/20/20" in text, "Podział 60/20/20 opisany")
    add("five_models", text.count("LightGBM") >= 3 and text.count("CatBoost") >= 3,
        "LightGBM i CatBoost wielokrotnie w treści (5 modeli)")
    add("calibration", "izotoniczn" in text, "Kalibracja izotoniczna opisana")
    add("auc_catboost", contains_any(_num_variants(metrics.loc["CatBoost", "AUC"])),
        f"AUC CatBoost ({metrics.loc['CatBoost', 'AUC']:.4f}) w treści")
    add("auc_rf", contains_any(_num_variants(metrics.loc["Random Forest", "AUC"])),
        f"AUC RF ({metrics.loc['Random Forest', 'AUC']:.4f}) w treści")
    add("thresholds", contains_any(_num_variants(thr["randomForest"], 3))
        and contains_any(_num_variants(thr["xgboost"], 3)),
        "Progi kosztowe (RF, XGB) w treści")
    add("fairness_terms", "DPD" in text and "EOD" in text, "Metryki DPD/EOD w treści")
    # — relikty zakazane —
    add("no_three_classifiers", "trzy różne klasyfikatory" not in text,
        "Brak reliktu 'trzy różne klasyfikatory'")
    add("no_old_split", "9 000" not in text and "56% trenowanie" not in text,
        "Brak starego podziału 70/30 (test 9 000 / proporcje 56-14-30)")
    add("no_lstm_63", "ma wymiar (6, 3)" not in text,
        "Brak bezwarunkowego LSTM (6,3) — dopuszczalny tylko jako baseline")
    add("no_old_toc_53", "modeli LSTM, Random Forest i XGBoost" not in text,
        "TOC 5.3 nie wymienia 3 modeli")
    add("no_old_thr", "XGB=0.180" not in text and "LSTM=0.185" not in text,
        "Brak starych progów (0.180/0.185)")
    return checks


def main(pdf_path: str) -> int:
    from pypdf import PdfReader
    pdf = Path(pdf_path)
    text = "\n".join(p.extract_text() or "" for p in PdfReader(pdf).pages)
    checks = run_checks(text, Path(__file__).parent / "reports")
    red = [c for c in checks if not c.ok]
    lines = [f"# Walidacja {pdf.name} — {len(checks) - len(red)}/{len(checks)} OK", ""]
    for c in checks:
        lines.append(f"- {'🟢' if c.ok else '🔴'} `{c.id}` — {c.description}"
                     + (f" — {c.detail}" if c.detail else ""))
    out = pdf.parent / "WalidacjaPDFv9.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"{len(checks) - len(red)}/{len(checks)} OK -> {out}")
    return 1 if red else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
