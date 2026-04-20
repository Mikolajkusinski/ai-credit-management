"""Rysunek 2.4 — Architektura modelu LSTM użytego w pracy."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import graphviz
from common import save_graphviz


def build():
    g = graphviz.Digraph("architektura_lstm", format="png")
    g.attr(rankdir="TB", bgcolor="white", pad="0.4", nodesep="0.25", ranksep="0.55")
    g.attr("node", fontname="Helvetica", fontsize="11", shape="box",
           style="rounded,filled", margin="0.3,0.18", penwidth="1.4")
    g.attr("edge", color="#1f3a68", arrowsize="0.8", penwidth="1.4")

    g.node("IN", "Wejście — sekwencja 6 × 3\n(PAY, BILL_AMT, PAY_AMT dla\nmiesięcy kwiecień–wrzesień)",
           fillcolor="#e8eef7", color="#1f3a68")
    g.node("LSTM", "Warstwa LSTM (32 jednostki)\nbramki: input, forget, output,\nstan ukryty h_t i stan komórki c_t",
           fillcolor="#d4e3f2", color="#1f3a68")
    g.node("DROP", "Dropout (p = 0.3)\nregularyzacja",
           fillcolor="#f2e9d4", color="#c9772e")
    g.node("DENSE", "Warstwa Dense (16 neuronów,\naktywacja ReLU)",
           fillcolor="#e0ecd1", color="#6b8e23")
    g.node("OUT", "Wyjście — Dense (1 neuron,\naktywacja sigmoid)\n→ P(Default)",
           fillcolor="#f5d7db", color="#a63446")

    g.edge("IN", "LSTM", label="  (batch, 6, 3)  ", fontsize="9", fontcolor="#555")
    g.edge("LSTM", "DROP", label="  (batch, 32)  ", fontsize="9", fontcolor="#555")
    g.edge("DROP", "DENSE")
    g.edge("DENSE", "OUT", label="  (batch, 16)  ", fontsize="9", fontcolor="#555")

    g.attr(label="Rysunek 2.4. Architektura sieci LSTM wykorzystanej do oceny zdolności kredytowej",
           labelloc="b", fontsize="12", fontname="Helvetica")
    return g


if __name__ == "__main__":
    save_graphviz(build(), chapter=2, idx="4", name="architektura_lstm",
                  comment="Schemat warstw modelu LSTM (Input 6×3 → LSTM 32 → Dropout → Dense 16 → Sigmoid) z oznaczonymi wymiarami tensorów między warstwami.")
