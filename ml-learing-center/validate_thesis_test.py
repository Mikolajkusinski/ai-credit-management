"""Testy silnika checków walidatora pracy (na fixtures tekstowych, bez PDF)."""
from pathlib import Path

from validate_thesis import run_checks

REPORTS = Path(__file__).parent / "reports"

GOOD = (
    "Rozdział 3. Metodologia badań " + "x" * 6000 + " H1 H2 H3 60/20/20\n"
    "Rozdział 4. Implementacja pięć klasyfikatorów LightGBM CatBoost "
    "LightGBM CatBoost LightGBM CatBoost "
    "kalibracja izotoniczna 0,145 0,165 DPD EOD\n"
    "Rozdział 5. Analiza wyników " + "x" * 9000 + " 0,7793 0,7741\n"
    "Zakończenie " + "x" * 1500 + "\n"
    "Bibliografia\n"
)

BAD = (
    "Rozdział 3. Metodologia badań\n"
    "Rozdział 4. Implementacja zaimplementowano trzy różne klasyfikatory\n"
    "wydzielono zbiór testowy o udziale 30%, co odpowiada 9 000 obserwacji\n"
    "Wejście sieci ma wymiar (6, 3)\n"
    "Rozdział 5. Analiza wyników\n"
    "Zakończenie\n"
    "Bibliografia\n"
)


def _by_id(checks):
    return {c.id: c for c in checks}


def test_good_text_passes_structural_and_content_checks():
    res = _by_id(run_checks(GOOD, REPORTS))
    for cid in ["ch3_nonempty", "ch5_nonempty", "zakonczenie_nonempty",
                "split_602020", "hipotezy", "five_models", "auc_catboost",
                "thresholds", "fairness_terms", "no_three_classifiers",
                "no_old_split", "no_lstm_63"]:
        assert res[cid].ok, f"{cid}: {res[cid].detail}"


def test_bad_text_fails_relic_checks():
    res = _by_id(run_checks(BAD, REPORTS))
    assert not res["no_three_classifiers"].ok
    assert not res["no_old_split"].ok
    assert not res["no_lstm_63"].ok
    assert not res["ch3_nonempty"].ok      # brak treści po nagłówku
    assert not res["auc_catboost"].ok


def test_check_count_at_least_15():
    assert len(run_checks(GOOD, REPORTS)) >= 15
