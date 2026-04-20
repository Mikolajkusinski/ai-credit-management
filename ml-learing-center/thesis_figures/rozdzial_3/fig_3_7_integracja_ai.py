"""Rysunek 3.7 — Integracja modeli AI z backendem."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import graphviz
from common import save_graphviz


def build():
    g = graphviz.Digraph("integracja_ai", format="png")
    g.attr(rankdir="LR", bgcolor="white", pad="0.4", nodesep="0.3", ranksep="0.7")
    g.attr("node", fontname="Helvetica", fontsize="10", shape="box",
           style="rounded,filled", margin="0.22,0.14", penwidth="1.3")
    g.attr("edge", color="#1f3a68", arrowsize="0.8")

    with g.subgraph(name="cluster_net") as c:
        c.attr(label=".NET 8 / ASP.NET Core", style="rounded,dashed",
               color="#1f3a68", fontname="Helvetica-Bold")
        c.node("CTRL", "PredictController\n[HttpPost(\"/api/Predict\")]",
               fillcolor="#d4e3f2", color="#1f3a68")
        c.node("SRV", "PredictionService\n(HttpClient wrapper)",
               fillcolor="#e8eef7", color="#1f3a68")
        c.node("DTO", "DTO: PredictRequest,\nPredictResponse",
               fillcolor="#eef3f8", color="#99a8b8", fontsize="9")
        c.edge("CTRL", "SRV", label="  deserializacja  ", fontsize="9", fontcolor="#555")
        c.edge("CTRL", "DTO", arrowhead="none", style="dashed", color="#888")
        c.edge("SRV", "DTO", arrowhead="none", style="dashed", color="#888")

    with g.subgraph(name="cluster_flask") as c:
        c.attr(label="Flask ML-service (Python)", style="rounded,dashed",
               color="#a63446", fontname="Helvetica-Bold")
        c.node("APP", "app.py\n@app.route(\"/predict\")",
               fillcolor="#f5d7db", color="#a63446")
        c.node("FE_PY", "Feature engineering\n+ StandardScaler",
               fillcolor="#fde9b1", color="#c9772e", fontsize="9")
        c.node("MOD", "RF / XGB / LSTM\npredict_proba(...)",
               fillcolor="#fff3e0", color="#c9772e", fontsize="9")
        c.edge("APP", "FE_PY")
        c.edge("FE_PY", "MOD")
        c.edge("MOD", "APP", label="  probas  ", fontsize="9", fontcolor="#555",
               style="dashed", constraint="false")

    g.edge("SRV", "APP",
           label="  HTTP POST http://ml-service:5001/predict\n  Content-Type: application/json  ",
           fontsize="9", fontcolor="#555", color="#a63446", penwidth="1.5")
    g.edge("APP", "SRV",
           label="  200 OK (JSON z 3 predykcjami)  ", fontsize="9", fontcolor="#555",
           style="dashed", color="#6b8e23", constraint="false")

    g.attr(label="Rysunek 3.7. Integracja backendu .NET z usługą predykcji Flask",
           labelloc="b", fontsize="12", fontname="Helvetica")
    return g


if __name__ == "__main__":
    save_graphviz(build(), chapter=3, idx="7", name="integracja_ai",
                  comment="Schemat integracji backendu .NET (PredictController + PredictionService) z usługą Flask ML-service wraz z wewnętrznym pipeline'em feature engineering i predykcji trzech modeli.")
