"""Rysunek 3.8 — Scenariusze wyjątków w systemie."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import graphviz
from common import save_graphviz


def build():
    g = graphviz.Digraph("scenariusze_wyjatkow", format="png")
    g.attr(rankdir="TB", bgcolor="white", pad="0.4", nodesep="0.3", ranksep="0.6")
    g.attr("node", fontname="Helvetica", fontsize="10", shape="box",
           style="rounded,filled", margin="0.2,0.12", penwidth="1.3")
    g.attr("edge", color="#333", arrowsize="0.8")

    g.node("REQ", "Żądanie predykcji\nPOST /api/Predict",
           fillcolor="#e8eef7", color="#1f3a68")
    g.node("VAL", "Walidacja\nJSON + DTO",
           fillcolor="#fde9b1", color="#c9772e", shape="diamond")
    g.node("ML", "Wywołanie ML-service",
           fillcolor="#d4e3f2", color="#1f3a68", shape="diamond")
    g.node("OK", "200 OK\nPredictResponse",
           fillcolor="#e0ecd1", color="#6b8e23")

    errors = [
        ("E1", "400 Bad Request\n— brak pola wymaganego\n(required field missing)"),
        ("E2", "422 Unprocessable\n— zły format danych\n(np. string zamiast int)"),
        ("E3", "504 Gateway Timeout\n— ML-service nie odpowiada\nw zadanym czasie"),
        ("E4", "500 Internal Error\n— niezgodność cech\n(liczba kolumn ≠ schema)"),
        ("E5", "503 Service Unavailable\n— ML-service offline\nlub model niezaładowany"),
    ]
    for code, label in errors:
        g.node(code, label, fillcolor="#f5d7db", color="#a63446")

    g.edge("REQ", "VAL")
    g.edge("VAL", "ML", label="  dane OK  ", fontsize="9", fontcolor="#555")
    g.edge("VAL", "E1", label="  brak danych  ", fontsize="9", fontcolor="#a63446")
    g.edge("VAL", "E2", label="  zły format  ", fontsize="9", fontcolor="#a63446")
    g.edge("ML", "OK", label="  sukces  ", fontsize="9", fontcolor="#6b8e23")
    g.edge("ML", "E3", label="  timeout  ", fontsize="9", fontcolor="#a63446")
    g.edge("ML", "E4", label="  błąd schema  ", fontsize="9", fontcolor="#a63446")
    g.edge("ML", "E5", label="  brak usługi  ", fontsize="9", fontcolor="#a63446")

    g.attr(label="Rysunek 3.8. Scenariusze wyjątków w procesie predykcji",
           labelloc="b", fontsize="12", fontname="Helvetica")
    return g


if __name__ == "__main__":
    save_graphviz(build(), chapter=3, idx="8", name="scenariusze_wyjatkow",
                  comment="Drzewo decyzyjne pięciu typowych scenariuszy błędów w pipeline predykcji — walidacja żądania i komunikacja z ML-service.")
