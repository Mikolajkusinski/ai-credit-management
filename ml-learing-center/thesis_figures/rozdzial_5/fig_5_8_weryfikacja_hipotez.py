"""Rysunek 5.8 — Diagram weryfikacji hipotez badawczych (placeholder)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from common import apply_style, save_figure, PALETTE

apply_style()

# TODO: podmień na rzeczywiste hipotezy z pracy magisterskiej
HYPOTHESES = [
    {
        "h": "Hipoteza H1",
        "tytul": "[Tu wpisz treść hipotezy H1]",
        "wynik": "[Skrótowy wynik / metryka]",
        "status": "potwierdzona",     # potwierdzona / częściowo / odrzucona
    },
    {
        "h": "Hipoteza H2",
        "tytul": "[Tu wpisz treść hipotezy H2]",
        "wynik": "[Skrótowy wynik / metryka]",
        "status": "częściowo",
    },
    {
        "h": "Hipoteza H3",
        "tytul": "[Tu wpisz treść hipotezy H3]",
        "wynik": "[Skrótowy wynik / metryka]",
        "status": "potwierdzona",
    },
    {
        "h": "Hipoteza H4",
        "tytul": "[Tu wpisz treść hipotezy H4]",
        "wynik": "[Skrótowy wynik / metryka]",
        "status": "odrzucona",
    },
]

STATUS_COLORS = {
    "potwierdzona": PALETTE[2],
    "częściowo":    PALETTE[4],
    "odrzucona":    PALETTE[1],
}


def build():
    n = len(HYPOTHESES)
    fig, ax = plt.subplots(figsize=(12, 1.1 + n * 1.4))

    row_h = 1.1
    for i, hip in enumerate(HYPOTHESES):
        y = (n - 1 - i) * (row_h + 0.2)
        color = STATUS_COLORS[hip["status"]]
        # Badge hipotezy
        ax.add_patch(mpatches.FancyBboxPatch((0, y), 2.2, row_h,
                                             boxstyle="round,pad=0.05",
                                             facecolor=color, edgecolor="white", linewidth=2))
        ax.text(1.1, y + row_h / 2, hip["h"], ha="center", va="center",
                color="white", fontsize=13, fontweight="bold")

        # Treść
        ax.add_patch(mpatches.FancyBboxPatch((2.5, y), 5.5, row_h,
                                             boxstyle="round,pad=0.05",
                                             facecolor="white", edgecolor=color, linewidth=1.5))
        ax.text(2.7, y + row_h * 0.75, hip["tytul"], ha="left", va="center",
                fontsize=10, color="#333")
        ax.text(2.7, y + row_h * 0.28, f"Wynik: {hip['wynik']}", ha="left", va="center",
                fontsize=10, color="#666", style="italic")

        # Strzałka
        ax.annotate("", xy=(8.3, y + row_h / 2), xytext=(8.05, y + row_h / 2),
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=2))

        # Status
        ax.add_patch(mpatches.FancyBboxPatch((8.5, y), 3.2, row_h,
                                             boxstyle="round,pad=0.05",
                                             facecolor=color, edgecolor="white", linewidth=2))
        ax.text(10.1, y + row_h / 2, hip["status"].upper(), ha="center", va="center",
                color="white", fontsize=12, fontweight="bold")

    # Legenda
    legend_patches = [mpatches.Patch(color=c, label=l.capitalize())
                      for l, c in STATUS_COLORS.items()]
    ax.legend(handles=legend_patches, loc="lower center",
              bbox_to_anchor=(0.5, -0.08), ncol=3, frameon=True, fontsize=10)

    ax.set_xlim(-0.3, 12)
    ax.set_ylim(-0.8, n * (row_h + 0.2))
    ax.set_axis_off()
    ax.set_title("Weryfikacja hipotez badawczych pracy",
                 fontsize=14, fontweight="bold", pad=14)
    return fig


if __name__ == "__main__":
    fig = build()
    save_figure(fig, chapter=5, idx="8", name="weryfikacja_hipotez",
                comment="[PLACEHOLDER] Tabela wizualna weryfikacji hipotez — hipoteza → wynik → status (potwierdzona/częściowo/odrzucona). Podmień HYPOTHESES w pliku generatora na rzeczywiste hipotezy z pracy.")
    plt.close(fig)
