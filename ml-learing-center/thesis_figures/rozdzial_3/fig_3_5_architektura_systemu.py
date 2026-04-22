"""Rysunek 3.5 — Architektura systemu eksperymentalnego."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import graphviz
from common import save_graphviz


def build():
    g = graphviz.Digraph("architektura_systemu", format="png")
    g.attr(rankdir="LR", bgcolor="white", pad="0.4", nodesep="0.35", ranksep="0.9")
    g.attr("node", fontname="Helvetica", fontsize="11", shape="box",
           style="rounded,filled", penwidth="1.4", margin="0.25,0.18")
    g.attr("edge", color="#1f3a68", arrowsize="0.8", penwidth="1.2")

    # Warstwy — klastry
    with g.subgraph(name="cluster_frontend") as c:
        c.attr(label="Warstwa prezentacji", style="rounded,dashed",
               color="#6b8e23", fontcolor="#6b8e23", fontname="Helvetica-Bold")
        c.node("FE", "Frontend\nReact 19 + Vite\n(port 5173)",
               fillcolor="#e0ecd1", color="#6b8e23")

    with g.subgraph(name="cluster_backend") as c:
        c.attr(label="Warstwa aplikacyjna", style="rounded,dashed",
               color="#1f3a68", fontcolor="#1f3a68", fontname="Helvetica-Bold")
        c.node("BE", "Backend .NET 8\nASP.NET Core Web API\n(PredictController)",
               fillcolor="#d4e3f2", color="#1f3a68")

    with g.subgraph(name="cluster_ml") as c:
        c.attr(label="Warstwa usług ML", style="rounded,dashed",
               color="#a63446", fontcolor="#a63446", fontname="Helvetica-Bold")
        c.node("ML", "ML-service\nFlask + TensorFlow\n(port 5001)",
               fillcolor="#f5d7db", color="#a63446")
        c.node("RF", "rf_model.pkl", fillcolor="#fff3e0", color="#c9772e", fontsize="10")
        c.node("XGB", "xgb_model.pkl", fillcolor="#fff3e0", color="#c9772e", fontsize="10")
        c.node("LSTM", "lstm_model.keras", fillcolor="#fff3e0", color="#c9772e", fontsize="10")
        c.edge("ML", "RF", arrowhead="none", style="dashed", color="#888")
        c.edge("ML", "XGB", arrowhead="none", style="dashed", color="#888")
        c.edge("ML", "LSTM", arrowhead="none", style="dashed", color="#888")

    with g.subgraph(name="cluster_data") as c:
        c.attr(label="Warstwa danych", style="rounded,dashed",
               color="#6c757d", fontcolor="#6c757d", fontname="Helvetica-Bold")
        c.node("CSV", "Zbiór UCI\ndefault_of_credit_card_clients.csv",
               fillcolor="#f0f0f0", color="#6c757d")

    g.edge("FE", "BE", label="  HTTPS / JSON  ", fontsize="10", fontcolor="#555")
    g.edge("BE", "ML", label="  HTTP POST /predict  ", fontsize="10", fontcolor="#555")
    g.edge("CSV", "ML", label="  trening\n  (main.py)  ", fontsize="9",
           fontcolor="#555", style="dotted", color="#888")

    g.attr(label="Rysunek 3.5. Architektura systemu eksperymentalnego",
           labelloc="b", fontsize="12", fontname="Helvetica")
    return g


if __name__ == "__main__":
    save_graphviz(build(), chapter=3, idx="5", name="architektura_systemu",
                  comment="Czterowarstwowa architektura systemu: frontend React, backend .NET, ML-service Flask z trzema modelami oraz warstwa danych UCI.")
