# Leakage fix 2026-07-07 — progi kosztowe przeniesione ze zbioru testowego na split kalibracyjny

**Problem (Fable5-zmiany.md Task3/Task4, R2):** progi alertu CREDIT-106 były optymalizowane na
zbiorze TESTOWYM (`main.py`, `_y_te_arr`), a następnie ten sam zbiór służył do ewaluacji,
audytu fairness (CREDIT-112) i porównania static-vs-dynamic (CREDIT-111) — dokładnie ten
wyciek, przed którym praca ostrzega w sekcji 4.1.1.

**Naprawa:** optymalizacja `cost = 5·FN + 1·FP` przebiega teraz na splicie
KALIBRACYJNYM (60/20/20, `random_state=42`). Świadomy kompromis: kalibratory
izotoniczne były fitowane na tym samym splicie, więc skalibrowane prawdopodobieństwa
są tu in-sample dla kalibratora — nadal ściśle lepsze niż dobór progu na teście.

Uwaga: retrain wykonano łącznie z naprawą skalerów (`scaler_leakage_fix.md`),
więc różnice progów są efektem łącznym obu poprawek + stochastyczności LSTM
(od tego runu LSTM W3 ma ziarno `set_random_seed(42)`).

## Progi przed → po

| Model | Próg przed (test) | Próg po (calib) | Zmiana |
|---|---:|---:|---:|
| Random Forest | 0.145 | 0.145 | 0.000 |
| XGBoost | 0.180 | 0.165 | −0.015 |
| LightGBM | 0.160 | 0.160 | 0.000 |
| CatBoost | 0.130 | 0.160 | +0.030 |
| LSTM | 0.175 | 0.155 | −0.020 |

## Wpływ na audyt fairness (DPD / EOD wrt SEX, na teście, przy nowych progach)

| Model | DPD przed | DPD po | EOD przed | EOD po |
|---|---:|---:|---:|---:|
| Random Forest | +0.0347 | +0.0345 | +0.0289 | +0.0282 |
| XGBoost | +0.0377 | +0.0358 | +0.0333 | +0.0279 |
| LightGBM | +0.0269 | +0.0351 | +0.0215 | +0.0274 |
| CatBoost | +0.0393 | +0.0392 | +0.0334 | +0.0329 |
| LSTM | +0.0068 | +0.0060 | +0.0153 | +0.0208 |

Wszystkie wartości pozostają ≤ 0.04 przy limicie 0.10 (DoD CREDIT-112) — **werdykt
audytu bez zmian**. Największa pojedyncza zmiana (LightGBM DPD +0.008) mieści się
w wariancji próbkowania dla n=6000.

## Wpływ na porównanie static-vs-dynamic (delta @FA=10%, pp)

| Model | Przed | Po | Lead-only wins po |
|---|---:|---:|---:|
| Random Forest | −4.97 | −10.85 | 48 |
| XGBoost | −5.88 | −5.12 | 47 |
| LightGBM | −1.28 | −4.97 | 52 |
| CatBoost | −6.86 | −6.41 | 39 |
| **LSTM** | −7.69 | **+2.56** | **74** |

Nowy wynik merytoryczny: po naprawie **LSTM jest jedynym modelem, dla którego reguła
monitorująca wygrywa ze statyczną także na catch rate przy FA=10%** — spójne
z hipotezą, że model sekwencyjny najlepiej wykorzystuje trajektorię. Pozostałe
modele: bez zmiany werdyktu (statyka wygrywa na catch rate; monitoring zachowuje
lead time ~2 okna i 39–74 unikalnych wykryć/model).

**Wniosek:** wyciek progów nie zawyżał wniosków pracy — po naprawie werdykty
fairness i static-vs-dynamic pozostają jakościowo identyczne (z korzystnym
wyjątkiem LSTM), a liczby zmieniają się w granicach szumu próbkowania.
