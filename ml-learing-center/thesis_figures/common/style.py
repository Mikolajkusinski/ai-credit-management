"""Spójna paleta i styl akademicki dla wszystkich wykresów pracy magisterskiej."""
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns

PALETTE = ["#1f3a68", "#a63446", "#6b8e23", "#6c757d", "#d4a017", "#3e7cb1"]
MODEL_COLORS = {
    "LSTM": "#1f3a68",
    "Random Forest": "#a63446",
    "XGBoost": "#6b8e23",
    "Scoring tradycyjny": "#6c757d",
    "Regresja logistyczna": "#6c757d",
}

FIGSIZE_SMALL = (6, 4)
FIGSIZE_MEDIUM = (8, 5)
FIGSIZE_LARGE = (10, 6)
FIGSIZE_WIDE = (12, 5)
FIGSIZE_TALL = (8, 8)

GRAPHVIZ_ATTRS = {
    "fontname": "Helvetica",
    "fontsize": "11",
    "rankdir": "LR",
    "bgcolor": "white",
    "pad": "0.3",
}


def apply_style():
    sns.set_theme(style="whitegrid", palette=PALETTE)
    mpl.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 11,
        "axes.titlesize": 13,
        "axes.titleweight": "bold",
        "axes.labelsize": 11,
        "axes.edgecolor": "#333333",
        "axes.linewidth": 0.8,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 10,
        "legend.frameon": True,
        "legend.framealpha": 0.9,
        "figure.dpi": 110,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "grid.color": "#e0e0e0",
        "grid.linewidth": 0.6,
    })
