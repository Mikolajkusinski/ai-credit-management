"""Rysunek 1.2 — Schemat rodzajów ryzyka kredytowego."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import graphviz
from common import save_graphviz


def build():
    g = graphviz.Digraph("rodzaje_ryzyka", format="png")
    g.attr(rankdir="TB", bgcolor="white", pad="0.4", nodesep="0.3", ranksep="0.6")
    g.attr("node", fontname="Helvetica", fontsize="11", shape="box",
           style="rounded,filled", margin="0.2,0.12")
    g.attr("edge", color="#333", penwidth="1.0", arrowhead="none")

    g.node("ROOT", "Ryzyko kredytowe",
           fillcolor="#1f3a68", fontcolor="white", fontsize="13",
           color="#1f3a68", penwidth="2")

    categories = [
        ("NIEW", "Ryzyko niewypłacalności", "#a63446",
         "Niezdolność dłużnika do\nwywiązania się ze zobowiązań"),
        ("OPOZ", "Ryzyko opóźnień", "#c9772e",
         "Spóźnienia w spłatach rat,\nkoszty windykacji"),
        ("SEKT", "Ryzyko sektorowe", "#6b8e23",
         "Pogorszenie kondycji branży\nklienta lub rynku"),
        ("MAKRO", "Ryzyko makroekonomiczne", "#3e7cb1",
         "Stopy procentowe, inflacja,\nbezrobocie, kurs walut"),
    ]
    for code, label, color, desc in categories:
        g.node(code, label, fillcolor=color, fontcolor="white",
               color=color, penwidth="1.4")
        g.node(f"{code}_D", desc, shape="note", fillcolor="#f8f8f8",
               color="#888", fontsize="9", fontname="Helvetica-Oblique")
        g.edge("ROOT", code)
        g.edge(code, f"{code}_D", style="dotted", color="#888")

    g.attr(label="Rysunek 1.2. Klasyfikacja ryzyka kredytowego",
           labelloc="b", fontsize="13", fontname="Helvetica")
    return g


if __name__ == "__main__":
    save_graphviz(build(), chapter=1, idx="2", name="rodzaje_ryzyka",
                  comment="Hierarchiczna klasyfikacja czterech głównych typów ryzyka kredytowego wraz z krótkim opisem każdego.")
