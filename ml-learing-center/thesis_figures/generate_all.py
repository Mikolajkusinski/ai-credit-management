"""Master script — generuje wszystkie wykresy pracy magisterskiej.

Użycie:
    python generate_all.py                  # wszystkie rozdziały
    python generate_all.py --chapter 3      # tylko rozdział 3
    THESIS_NO_CACHE=1 python generate_all.py  # wymuś retrening (ignoruj cache)

Wyniki: output/rozdzial_{1..5}/fig_*.{png,svg}
"""
import argparse
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CHAPTERS = [1, 2, 3, 4, 5]


def run(script: Path) -> tuple[bool, float]:
    t0 = time.time()
    result = subprocess.run(
        [sys.executable, str(script)],
        cwd=ROOT,
        capture_output=True, text=True,
    )
    dt = time.time() - t0
    ok = result.returncode == 0
    if not ok:
        print(f"  [FAIL] {script.name} ({dt:.1f}s)")
        print(result.stderr.strip()[-1000:])
    return ok, dt


def main():
    parser = argparse.ArgumentParser(description="Generator wykresów do pracy magisterskiej")
    parser.add_argument("--chapter", type=int, choices=CHAPTERS,
                        help="Uruchom tylko wybrany rozdział")
    args = parser.parse_args()

    chapters = [args.chapter] if args.chapter else CHAPTERS

    total_ok = 0
    total_fail = 0
    total_time = 0.0
    t_start = time.time()

    for chapter in chapters:
        chapter_dir = ROOT / f"rozdzial_{chapter}"
        scripts = sorted(chapter_dir.glob("fig_*.py"))
        if not scripts:
            print(f"[SKIP] Brak skryptów w {chapter_dir}")
            continue
        print(f"\n=== Rozdział {chapter} ({len(scripts)} wykresów) ===")
        for script in scripts:
            print(f"> {script.name}", end="", flush=True)
            ok, dt = run(script)
            total_time += dt
            if ok:
                print(f"  ({dt:.1f}s)")
                total_ok += 1
            else:
                total_fail += 1

    elapsed = time.time() - t_start
    print(f"\n{'=' * 60}")
    print(f"Sukces: {total_ok}  |  Błąd: {total_fail}  |  Czas: {elapsed:.1f}s")
    print(f"Wyniki zapisane w: {ROOT / 'output'}")
    sys.exit(0 if total_fail == 0 else 1)


if __name__ == "__main__":
    main()
