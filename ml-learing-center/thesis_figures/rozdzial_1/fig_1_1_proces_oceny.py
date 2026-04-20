"""Rysunek 1.1 — Diagram procesu oceny zdolności kredytowej."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import graphviz
from common import save_graphviz


def build():
    g = graphviz.Digraph("proces_oceny", format="png")
    g.attr(rankdir="LR", bgcolor="white", pad="0.4", nodesep="0.4", ranksep="0.8")
    g.attr("node", fontname="Helvetica", fontsize="12", shape="box",
           style="rounded,filled", fillcolor="#e8eef7", color="#1f3a68",
           penwidth="1.4", margin="0.25,0.15")
    g.attr("edge", color="#1f3a68", penwidth="1.2", arrowsize="0.8",
           fontname="Helvetica", fontsize="10")

    g.node("A", "Wniosek klienta\n(dane osobowe, finansowe)")
    g.node("B", "Analiza i weryfikacja\ndanych wejściowych")
    g.node("C", "Scoring\n(model ilościowy)", fillcolor="#d9e2f3")
    g.node("D", "Decyzja kredytowa\n(akceptacja / odrzucenie)",
           fillcolor="#f5d7db", color="#a63446")
    g.node("E", "Monitoring ryzyka\ni spłat", fillcolor="#e5efdf", color="#6b8e23")

    g.edge("A", "B")
    g.edge("B", "C")
    g.edge("C", "D")
    g.edge("D", "E", label="  klient aktywny  ")
    g.edge("E", "B", label="  aktualizacja danych  ", style="dashed", constraint="false")

    g.attr(label="Rysunek 1.1. Proces oceny zdolności kredytowej",
           labelloc="b", fontsize="13", fontname="Helvetica")
    return g


if __name__ == "__main__":
    save_graphviz(build(), chapter=1, idx="1", name="proces_oceny",
                  comment="Przepływ etapów oceny zdolności kredytowej od wniosku klienta aż po monitoring spłat, z pętlą aktualizacji danych.")
