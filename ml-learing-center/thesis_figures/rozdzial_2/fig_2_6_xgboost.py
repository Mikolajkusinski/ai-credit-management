"""Rysunek 2.6 — Diagram działania XGBoost (gradient boosting)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import graphviz
from common import save_graphviz


def build():
    g = graphviz.Digraph("xgboost", format="png")
    g.attr(rankdir="LR", bgcolor="white", pad="0.4", nodesep="0.3", ranksep="0.65")
    g.attr("node", fontname="Helvetica", fontsize="11", shape="box",
           style="rounded,filled", margin="0.22,0.14", penwidth="1.3")
    g.attr("edge", color="#1f3a68", arrowsize="0.8", penwidth="1.2")

    g.node("X", "Dane wejściowe X",
           fillcolor="#e8eef7", color="#1f3a68")

    for i in range(1, 5):
        label = (f"Drzewo t_{i}\n(uczy się przewidywać\nresidua modelu t_{i-1})"
                 if i > 1 else f"Drzewo t_1\n(startowy model słaby)")
        g.node(f"T{i}", label, fillcolor="#d4e3f2", color="#3e7cb1")

    g.node("SUM", "Suma predykcji\n(ważona skumulowana)",
           fillcolor="#f2e9d4", color="#c9772e")
    g.node("OUT", "Predykcja końcowa\n(sigmoid → P(Default))",
           fillcolor="#f5d7db", color="#a63446")

    g.edge("X", "T1")
    for i in range(1, 4):
        g.edge(f"T{i}", f"T{i+1}", label="  residua  ",
               fontsize="9", fontcolor="#555", color="#a63446", style="dashed")

    for i in range(1, 5):
        g.edge(f"T{i}", "SUM", arrowhead="none", color="#999", style="dotted")
    g.edge("SUM", "OUT")

    g.attr(label="Rysunek 2.6. XGBoost — sekwencyjne dodawanie drzew korygujących błędy poprzedników",
           labelloc="b", fontsize="12", fontname="Helvetica")
    return g


if __name__ == "__main__":
    save_graphviz(build(), chapter=2, idx="6", name="xgboost",
                  comment="Schemat gradient boostingu w XGBoost: każde kolejne drzewo uczy się residuów poprzedniego, a ważona suma wszystkich drzew tworzy predykcję końcową.")
