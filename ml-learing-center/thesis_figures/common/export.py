"""Zapis figur w PNG 300 DPI + SVG backup + agregacja komentarzy."""
from pathlib import Path
from datetime import datetime

OUTPUT_DIR = Path(__file__).resolve().parents[1] / "output"
README_PATH = OUTPUT_DIR / "README.md"


def _chapter_dir(chapter: int) -> Path:
    d = OUTPUT_DIR / f"rozdzial_{chapter}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def save_figure(fig, chapter: int, idx: str, name: str, comment: str = ""):
    """
    Zapisz figurę matplotlib jako PNG 300 DPI + SVG.

    chapter: 1..5
    idx: np. "1" dla fig_2_1_...
    name: slug ASCII, np. "architektura_lstm"
    comment: krótki opis po polsku do README.md
    """
    base = _chapter_dir(chapter) / f"fig_{chapter}_{idx}_{name}"
    png = base.with_suffix(".png")
    svg = base.with_suffix(".svg")
    fig.savefig(png, dpi=300, bbox_inches="tight", facecolor="white")
    fig.savefig(svg, bbox_inches="tight", facecolor="white")
    _log_comment(chapter, idx, name, comment, png)
    print(f"  [OK] {png.name}")


def save_graphviz(digraph, chapter: int, idx: str, name: str, comment: str = ""):
    """Zapisz obiekt graphviz.Digraph jako PNG + SVG."""
    base = _chapter_dir(chapter) / f"fig_{chapter}_{idx}_{name}"
    digraph.format = "png"
    digraph.render(str(base), cleanup=True)
    digraph.format = "svg"
    digraph.render(str(base), cleanup=True)
    _log_comment(chapter, idx, name, comment, base.with_suffix(".png"))
    print(f"  [OK] {base.name}.png + .svg")


def _log_comment(chapter: int, idx: str, name: str, comment: str, path: Path):
    OUTPUT_DIR.mkdir(exist_ok=True)
    if not README_PATH.exists():
        README_PATH.write_text(
            "# Wykresy do pracy magisterskiej\n\n"
            "Wygenerowane automatycznie skryptami z `thesis_figures/`.\n"
            "Wszystkie figury dostępne w formacie PNG (300 DPI) oraz SVG.\n\n"
            f"_Ostatnia aktualizacja: {datetime.now():%Y-%m-%d %H:%M}_\n\n"
        )
    tag = f"fig_{chapter}_{idx}_{name}"
    lines = README_PATH.read_text().splitlines()
    lines = [ln for ln in lines if tag not in ln]
    header = f"## Rozdział {chapter}"
    if header not in "\n".join(lines):
        lines.append("")
        lines.append(header)
    insert_at = len(lines)
    for i, ln in enumerate(lines):
        if ln == header:
            insert_at = i + 1
            while insert_at < len(lines) and lines[insert_at].startswith("- "):
                insert_at += 1
            break
    entry = f"- **{tag}** — {comment}" if comment else f"- **{tag}**"
    lines.insert(insert_at, entry)
    README_PATH.write_text("\n".join(lines) + "\n")
