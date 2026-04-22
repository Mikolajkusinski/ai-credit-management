"""Rysunek 3.4 — Diagram preprocessingu danych."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import graphviz
from common import save_graphviz


def build():
    g = graphviz.Digraph("preprocessing", format="png")
    g.attr(rankdir="LR", bgcolor="white", pad="0.4", nodesep="0.25", ranksep="0.6")
    g.attr("node", fontname="Helvetica", fontsize="11", shape="box",
           style="rounded,filled", fillcolor="#e8eef7", color="#1f3a68",
           penwidth="1.3", margin="0.22,0.15")
    g.attr("edge", color="#1f3a68", arrowsize="0.8", penwidth="1.2")

    steps = [
        ("A", "Dane surowe\n(UCI credit\ndefault CSV)"),
        ("B", "Czyszczenie\n(usunięcie ID,\nkolumn redundantnych)"),
        ("C", "Imputacja NaN\ni nieskończoności\n(fillna(0), replace(inf))"),
        ("D", "Feature engineering\n(utilization_rate,\nBILL_trend, late_count…)"),
        ("E", "Encoding cech\nkategorycznych\n(one-hot dla\nEDUCATION, MARRIAGE, SEX)"),
        ("F", "Normalizacja\n(StandardScaler\nosobno per cecha)"),
        ("G", "Podział zbioru\n(stratified\n70 / 30)"),
    ]
    for code, label in steps:
        g.node(code, label)
    for i in range(len(steps) - 1):
        g.edge(steps[i][0], steps[i + 1][0])

    # wyróżnienie feature eng.
    g.node("D", fillcolor="#fde9b1", color="#c9772e")

    g.attr(label="Rysunek 3.4. Etapy preprocessingu danych w projekcie",
           labelloc="b", fontsize="12", fontname="Helvetica")
    return g


if __name__ == "__main__":
    save_graphviz(build(), chapter=3, idx="4", name="preprocessing",
                  comment="Siedmioetapowy pipeline preprocessingu danych zastosowany w pracy: od surowego CSV, przez feature engineering (wyróżnione), aż po stratyfikowany podział 70/30.")
