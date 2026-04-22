"""Rysunek 2.2 — Pipeline uczenia maszynowego."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import graphviz
from common import save_graphviz


def build():
    g = graphviz.Digraph("pipeline_ml", format="png")
    g.attr(rankdir="LR", bgcolor="white", pad="0.4", nodesep="0.3", ranksep="0.7")
    g.attr("node", fontname="Helvetica", fontsize="11", shape="box",
           style="rounded,filled", fillcolor="#e8eef7", color="#1f3a68",
           penwidth="1.4", margin="0.25,0.18")
    g.attr("edge", color="#1f3a68", arrowsize="0.8", penwidth="1.2")

    stages = [
        ("A", "Dane wejściowe\n(CSV, bazy danych,\nstrumienie)"),
        ("B", "Preprocessing\n(czyszczenie,\nimputacja, encoding)"),
        ("C", "Podział danych\n(train / val / test)"),
        ("D", "Trenowanie\n(optymalizacja\nhiperparametrów)"),
        ("E", "Walidacja\n(metryki, k-fold)"),
        ("F", "Predykcja\n(wdrożenie,\ninferencja)"),
    ]
    for code, label in stages:
        g.node(code, label)
    for i in range(len(stages) - 1):
        g.edge(stages[i][0], stages[i + 1][0])

    g.edge("E", "D", label="  retrening  ", style="dashed",
           color="#a63446", fontcolor="#a63446", constraint="false")
    g.edge("F", "B", label="  nowe dane  ", style="dotted",
           color="#6b8e23", fontcolor="#6b8e23", constraint="false")

    g.attr(label="Rysunek 2.2. Pipeline uczenia maszynowego",
           labelloc="b", fontsize="13", fontname="Helvetica")
    return g


if __name__ == "__main__":
    save_graphviz(build(), chapter=2, idx="2", name="pipeline_ml",
                  comment="Typowy pipeline projektu ML: od pozyskania danych, przez preprocessing i trenowanie, aż po wdrożenie i pętle sprzężenia zwrotnego.")
