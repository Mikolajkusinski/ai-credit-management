"""Rysunek 2.1 — Taksonomia uczenia maszynowego."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import graphviz
from common import save_graphviz


def build():
    g = graphviz.Digraph("taksonomia_ml", format="png")
    g.attr(rankdir="TB", bgcolor="white", pad="0.4", nodesep="0.35", ranksep="0.7")
    g.attr("node", fontname="Helvetica", fontsize="11", shape="box",
           style="rounded,filled", margin="0.22,0.12")
    g.attr("edge", color="#333", arrowhead="none", penwidth="1.1")

    g.node("ML", "Uczenie maszynowe",
           fillcolor="#1f3a68", fontcolor="white", fontsize="13", penwidth="2")

    g.node("SUP", "Uczenie nadzorowane",
           fillcolor="#3e7cb1", fontcolor="white")
    g.node("UNS", "Uczenie nienadzorowane",
           fillcolor="#6b8e23", fontcolor="white")
    g.node("RL", "Uczenie wzmacniane",
           fillcolor="#a63446", fontcolor="white")

    g.edge("ML", "SUP"); g.edge("ML", "UNS"); g.edge("ML", "RL")

    g.node("CLS", "Klasyfikacja\n(credit scoring,\nwykrywanie fraudów)",
           fillcolor="#d4e3f2", fontsize="10")
    g.node("REG", "Regresja\n(prognoza LGD,\nszacowanie strat)",
           fillcolor="#d4e3f2", fontsize="10")
    g.edge("SUP", "CLS"); g.edge("SUP", "REG")

    g.node("CLUST", "Grupowanie\n(segmentacja klientów)",
           fillcolor="#e0ecd1", fontsize="10")
    g.node("DIM", "Redukcja wymiarów\n(PCA, t-SNE)",
           fillcolor="#e0ecd1", fontsize="10")
    g.node("ANOM", "Wykrywanie anomalii\n(AML)",
           fillcolor="#e0ecd1", fontsize="10")
    g.edge("UNS", "CLUST"); g.edge("UNS", "DIM"); g.edge("UNS", "ANOM")

    g.node("POL", "Optymalizacja polityki\n(robo-doradcy,\ndynamiczne limity)",
           fillcolor="#f1d1d6", fontsize="10")
    g.edge("RL", "POL")

    g.attr(label="Rysunek 2.1. Taksonomia uczenia maszynowego z przykładami zastosowań w finansach",
           labelloc="b", fontsize="12", fontname="Helvetica")
    return g


if __name__ == "__main__":
    save_graphviz(build(), chapter=2, idx="1", name="taksonomia_ml",
                  comment="Hierarchiczne drzewo trzech głównych paradygmatów uczenia maszynowego z typowymi zastosowaniami w sektorze finansowym.")
