"""Rysunek 2.5 — Schemat działania Random Forest (bagging + głosowanie)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
from common import apply_style, save_figure, PALETTE

apply_style()


def _add_tree(G, root_id: str, levels: int = 3):
    """Zbuduj binarne drzewo o `levels` poziomach zaczepione w root_id."""
    queue = [(root_id, 0)]
    counter = [0]
    while queue:
        parent, depth = queue.pop(0)
        if depth >= levels:
            continue
        for _ in range(2):
            child = f"{root_id}_{counter[0]}"
            counter[0] += 1
            G.add_node(child, kind="leaf" if depth == levels - 1 else "node")
            G.add_edge(parent, child)
            queue.append((child, depth + 1))


def build():
    fig, ax = plt.subplots(figsize=(11, 6))
    n_trees = 4
    tree_roots = [f"T{i}" for i in range(n_trees)]

    G = nx.DiGraph()
    for root in tree_roots:
        G.add_node(root, kind="root")
        _add_tree(G, root, levels=3)

    # Układ: dane wejściowe po lewej, drzewa w kolumnie, głosowanie i wynik po prawej
    pos = {}
    tree_width = 2.0
    for ti, root in enumerate(tree_roots):
        # root
        pos[root] = (0, -ti * 3)
        # potomkowie
        sub_nodes = [n for n in G.successors(root)]
        for si, s in enumerate(sub_nodes):
            pos[s] = (1, -ti * 3 - 0.8 + si * 1.6)
            children = list(G.successors(s))
            for ci, c in enumerate(children):
                pos[c] = (2, -ti * 3 - 1.2 + si * 1.6 + ci * 0.8)
                grand = list(G.successors(c))
                for gi, g in enumerate(grand):
                    pos[g] = (3, -ti * 3 - 1.4 + si * 1.6 + ci * 0.8 + gi * 0.4)

    # Dane wejściowe
    G.add_node("X", kind="input")
    pos["X"] = (-1.7, -4.5)
    for root in tree_roots:
        G.add_edge("X", root)

    # Głosowanie
    G.add_node("VOTE", kind="vote")
    pos["VOTE"] = (4.5, -4.5)
    for root in tree_roots:
        # Łączenie: wszystkie liście drzewa → VOTE (uproszczone przez root)
        G.add_edge(root, "VOTE")

    # Wynik
    G.add_node("OUT", kind="out")
    pos["OUT"] = (6.2, -4.5)
    G.add_edge("VOTE", "OUT")

    def node_style(kind):
        return {
            "input": ("#e8eef7", "#1f3a68", 2000),
            "root": ("#d4e3f2", "#1f3a68", 900),
            "node": ("#eef3f8", "#99a8b8", 360),
            "leaf": ("#f7f7f7", "#999", 220),
            "vote": ("#f2e9d4", "#c9772e", 1800),
            "out": ("#f5d7db", "#a63446", 1800),
        }[kind]

    for kind in ["input", "root", "node", "leaf", "vote", "out"]:
        nodes = [n for n, d in G.nodes(data=True) if d["kind"] == kind]
        if not nodes:
            continue
        fc, ec, size = node_style(kind)
        nx.draw_networkx_nodes(G, pos, nodelist=nodes, node_color=fc,
                               edgecolors=ec, node_size=size, linewidths=1.5, ax=ax)

    nx.draw_networkx_edges(G, pos, edge_color="#888", width=0.8,
                           arrowsize=10, arrowstyle="-|>", ax=ax,
                           connectionstyle="arc3,rad=0.02")

    # Etykiety tylko dla kluczowych węzłów
    labels = {"X": "Dane\nwejściowe", "VOTE": "Głosowanie\nwiększościowe", "OUT": "Klasa\nwynikowa"}
    for ti, root in enumerate(tree_roots):
        labels[root] = f"Drzewo {ti + 1}"
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=9,
                            font_weight="bold", ax=ax)

    ax.set_axis_off()
    ax.set_title("Random Forest — zespół drzew decyzyjnych z agregacją przez głosowanie",
                 pad=10)
    ax.set_xlim(-3, 7.5)
    ax.set_ylim(-11, 1)
    return fig


if __name__ == "__main__":
    fig = build()
    save_figure(fig, chapter=2, idx="5", name="random_forest",
                comment="Schemat algorytmu Random Forest: N niezależnych drzew decyzyjnych wytrenowanych na bootstrapowych próbach danych, a ich predykcje agregowane są przez głosowanie większościowe.")
    plt.close(fig)
