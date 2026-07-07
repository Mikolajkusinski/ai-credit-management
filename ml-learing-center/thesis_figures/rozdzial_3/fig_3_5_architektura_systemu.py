"""Rysunek 3.5 — Architektura systemu eksperymentalnego (stan finalny: Wariant B).

Aktualizacja 2026-07-07: 5 modeli W3 (kalibrowanych), endpointy monitoringu,
warstwa trwałości PostgreSQL — zgodnie z rozdz. 3.4 pracy.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import graphviz
from common import save_graphviz


def build():
    g = graphviz.Digraph("architektura_systemu", format="png")
    g.attr(rankdir="LR", bgcolor="white", pad="0.4", nodesep="0.35", ranksep="0.8")
    g.attr("node", fontname="Helvetica", fontsize="11", shape="box",
           style="rounded,filled", penwidth="1.4", margin="0.25,0.18")
    g.attr("edge", color="#1f3a68", arrowsize="0.8", penwidth="1.2")

    with g.subgraph(name="cluster_frontend") as c:
        c.attr(label="Warstwa prezentacji", style="rounded,dashed",
               color="#6b8e23", fontcolor="#6b8e23", fontname="Helvetica-Bold")
        c.node("FE", "Frontend React 19 + Vite\n(port 5173)\nPrediction | Monitoring:\nTimeline 5 linii, alerty, SHAP",
               fillcolor="#e0ecd1", color="#6b8e23")

    with g.subgraph(name="cluster_backend") as c:
        c.attr(label="Warstwa aplikacyjna", style="rounded,dashed",
               color="#1f3a68", fontcolor="#1f3a68", fontname="Helvetica-Bold")
        c.node("BE", "Backend .NET 8 (port 5120)\nMonitoringController\nwalidacja 22 cech, labelki okien,\ntransakcja atomowa zapisu",
               fillcolor="#d4e3f2", color="#1f3a68")

    with g.subgraph(name="cluster_ml") as c:
        c.attr(label="Warstwa usług ML", style="rounded,dashed",
               color="#a63446", fontcolor="#a63446", fontname="Helvetica-Bold")
        c.node("ML", "ML-service Flask (port 5001)\n/predict/timeseries:\n5 modeli × 4 okna W0..W3,\ntrendy, progi kosztowe, SHAP",
               fillcolor="#f5d7db", color="#a63446")
        c.node("MODELS", "artefakty W3 (kalibrowane):\nrf | xgb | lightgbm | catboost (.pkl)\nlstm (.keras) + kalibrator\nskalery + alert_thresholds.json",
               fillcolor="#fff3e0", color="#c9772e", fontsize="10")
        c.edge("ML", "MODELS", arrowhead="none", style="dashed", color="#888")

    with g.subgraph(name="cluster_data") as c:
        c.attr(label="Warstwa danych", style="rounded,dashed",
               color="#6c757d", fontcolor="#6c757d", fontname="Helvetica-Bold")
        c.node("DB", "PostgreSQL 16 (port 5432)\nClient / Snapshot(22 cechy) /\nPrediction / Trend",
               fillcolor="#e8e8f5", color="#4a4a8a")
        c.node("CSV", "Zbiór UCI (30 000)\n→ panel sliding-window\n(trening: main.py)",
               fillcolor="#f0f0f0", color="#6c757d", fontsize="10")

    g.edge("FE", "BE", label="  POST/GET /api/v1/monitoring/*  ", fontsize="10", fontcolor="#555")
    g.edge("BE", "ML", label="  POST /predict/timeseries  ", fontsize="10", fontcolor="#555")
    g.edge("BE", "DB", label="  EF Core (Npgsql)  ", fontsize="10", fontcolor="#555")
    g.edge("CSV", "MODELS", label="  trening + kalibracja  ", fontsize="9",
           fontcolor="#555", style="dotted", color="#888")

    g.attr(label="Rysunek 3.5. Architektura systemu eksperymentalnego (Wariant B)",
           labelloc="b", fontsize="12", fontname="Helvetica")
    return g


if __name__ == "__main__":
    save_graphviz(build(), chapter=3, idx="5", name="architektura_systemu",
                  comment="Czterowarstwowa architektura finalna: React (Prediction+Monitoring), .NET 8 z transakcyjną persystencją, Flask z 5 kalibrowanymi modelami W3 i progami kosztowymi, PostgreSQL 16.")
