"""Rysunek 5.9 — Diagram końcowych wniosków i kierunków dalszych badań (placeholder)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import graphviz
from common import save_graphviz


# TODO: podmień treści na rzeczywiste wnioski i kierunki badawcze z pracy
CONCLUSIONS = [
    "[Wniosek 1 — np. XGBoost daje najlepszy\nkompromis dokładność / interpretowalność]",
    "[Wniosek 2 — np. LSTM wnosi wartość\ndodaną dzięki modelowaniu sekwencji]",
    "[Wniosek 3 — feature engineering ma\nistotny wpływ na jakość predykcji]",
]

FUTURE_WORK = [
    "[Kierunek 1 — rozszerzenie o dane\nbehawioralne / transakcyjne]",
    "[Kierunek 2 — modele transformerowe\ndla sekwencji dłuższych niż 6 miesięcy]",
    "[Kierunek 3 — wyjaśnialność modeli\ndla regulatorów (GDPR, AI Act)]",
    "[Kierunek 4 — uczenie ciągłe\n(online learning) i drift detection]",
]


def build():
    g = graphviz.Digraph("wnioski_kierunki", format="png")
    g.attr(rankdir="LR", bgcolor="white", pad="0.4", nodesep="0.25", ranksep="0.8")
    g.attr("node", fontname="Helvetica", fontsize="10", shape="box",
           style="rounded,filled", margin="0.22,0.16", penwidth="1.4")
    g.attr("edge", color="#333", arrowsize="0.8")

    g.node("PRACA", "Praca\nmagisterska",
           fillcolor="#1f3a68", fontcolor="white", fontsize="14",
           color="#1f3a68", penwidth="2", shape="ellipse")

    g.node("WN_H", "Kluczowe wnioski", fillcolor="#6b8e23", fontcolor="white",
           fontsize="13", color="#6b8e23", penwidth="2")
    g.node("KI_H", "Kierunki dalszych badań", fillcolor="#a63446", fontcolor="white",
           fontsize="13", color="#a63446", penwidth="2")

    g.edge("PRACA", "WN_H")
    g.edge("PRACA", "KI_H")

    for i, w in enumerate(CONCLUSIONS):
        node_id = f"W{i}"
        g.node(node_id, w, fillcolor="#e0ecd1", color="#6b8e23", fontsize="9")
        g.edge("WN_H", node_id)

    for i, k in enumerate(FUTURE_WORK):
        node_id = f"K{i}"
        g.node(node_id, k, fillcolor="#f5d7db", color="#a63446", fontsize="9")
        g.edge("KI_H", node_id)

    g.attr(label="Rysunek 5.9. Wnioski z pracy magisterskiej oraz kierunki dalszych badań",
           labelloc="b", fontsize="12", fontname="Helvetica")
    return g


if __name__ == "__main__":
    save_graphviz(build(), chapter=5, idx="9", name="wnioski_kierunki",
                  comment="[PLACEHOLDER] Mind-map wniosków i kierunków dalszych badań. Podmień treści w listach CONCLUSIONS i FUTURE_WORK na własne.")
