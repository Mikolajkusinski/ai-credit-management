"""Rysunek 3.9 — Stos technologiczny projektu."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from common import apply_style, save_figure, PALETTE

apply_style()

LAYERS = [
    ("Warstwa prezentacji",   ["React 19", "Vite", "axios", "recharts"],           PALETTE[2]),
    ("Warstwa aplikacyjna",   ["ASP.NET Core 8", "C# 12", "Swagger/OpenAPI"],      PALETTE[0]),
    ("Warstwa usług ML",      ["Flask", "Python 3.11", "Gunicorn", "Docker"],      PALETTE[1]),
    ("Warstwa modeli",        ["scikit-learn", "XGBoost", "TensorFlow / Keras"],   PALETTE[4]),
    ("Warstwa danych",        ["pandas", "NumPy", "CSV (UCI)"],                    PALETTE[5]),
    ("Infrastruktura",        ["Docker", "Docker Compose", "Git / GitHub"],        PALETTE[3]),
]


def build():
    fig, ax = plt.subplots(figsize=(11, 7))
    row_h = 1.0
    col_w = 2.6
    max_cols = max(len(items) for _, items, _ in LAYERS)

    for ri, (layer_name, items, color) in enumerate(LAYERS):
        y = (len(LAYERS) - 1 - ri) * row_h
        # Label warstwy
        ax.add_patch(mpatches.Rectangle((-3.3, y + 0.08), 3.0, row_h - 0.16,
                                        facecolor=color, edgecolor="white", linewidth=2))
        ax.text(-1.8, y + row_h / 2, layer_name, color="white",
                ha="center", va="center", fontsize=11, fontweight="bold")

        for ci, name in enumerate(items):
            x = ci * col_w
            ax.add_patch(mpatches.FancyBboxPatch((x + 0.1, y + 0.12),
                                                  col_w - 0.25, row_h - 0.24,
                                                  boxstyle="round,pad=0.05",
                                                  facecolor="white", edgecolor=color,
                                                  linewidth=1.6))
            ax.text(x + col_w / 2, y + row_h / 2, name,
                    ha="center", va="center", fontsize=10, color="#333",
                    fontweight="bold")

    ax.set_xlim(-3.5, max_cols * col_w + 0.2)
    ax.set_ylim(-0.2, len(LAYERS) * row_h + 0.3)
    ax.set_axis_off()
    ax.set_title("Stos technologiczny systemu eksperymentalnego",
                 fontsize=13, pad=12, fontweight="bold")
    return fig


if __name__ == "__main__":
    fig = build()
    save_figure(fig, chapter=3, idx="9", name="stos_technologiczny",
                comment="Stos technologiczny projektu w układzie warstwowym — prezentacja (React), aplikacja (.NET), ML (Flask), modele (sklearn/XGB/TF), dane (pandas/CSV) i infrastruktura (Docker).")
    plt.close(fig)
