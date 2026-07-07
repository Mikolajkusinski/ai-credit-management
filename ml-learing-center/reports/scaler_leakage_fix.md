# Leakage fix 2026-07-07 — skalery fitowane po splicie (tylko na części treningowej)

**Problem (Fable5-zmiany.md Task3 U4):** `StandardScaler` (statyczny `scaler_w3`) oraz
3 skalery kanałowe LSTM (`lstm_scalers_w3`) były fitowane na PEŁNYM zbiorze
30 000 wierszy PRZED podziałem train/calib/test — statystyki (mean/std)
zawierały wiersze testowe, co przeczy deklaracji „zamrożonego" zbioru testowego.

**Naprawa (pipeline W3; legacy 6-mies. pozostaje jako baseline historyczny):**
podział indeksów wykonywany jest najpierw (przydział wierszy niezmieniony —
stratyfikowany split zależy tylko od `y`, rozmiarów i `random_state=42`),
a skalery fitowane wyłącznie na 60% treningowych i stosowane przez `transform`
do części kalibracyjnej i testowej. `prepare_lstm_sequences` przyjmuje teraz
parametr `scalers` (transform bez refitu). Dodatkowo trening LSTM W3 otrzymał
`keras.utils.set_random_seed(42)` — wyniki są odtwarzalne między re-runami.

Uwaga: retrain wykonano łącznie z naprawą progów (`threshold_leakage_fix.md`),
więc poniższe różnice to efekt łączny obu poprawek.

## Metryki na zbiorze testowym przed → po (modele skalibrowane)

| Model | AUC przed | AUC po | ΔAUC | Brier przed | Brier po |
|---|---:|---:|---:|---:|---:|
| Random Forest | 0.7741 | 0.7741 | +0.0000 | 0.1372 | 0.1374 |
| XGBoost | 0.7760 | 0.7761 | +0.0001 | 0.1360 | 0.1360 |
| LightGBM | 0.7764 | 0.7767 | +0.0003 | 0.1366 | 0.1363 |
| CatBoost | 0.7802 | 0.7793 | −0.0009 | 0.1354 | 0.1357 |
| LSTM | 0.7610 | 0.7614 | +0.0003 | 0.1387 | 0.1388 |

**Bramka bezpieczeństwa |ΔAUC| ≤ 0.005: spełniona z dużym zapasem**
(maksymalna zmiana −0.0009, CatBoost). Ranking modeli niezmieniony
(CatBoost > LightGBM ≳ XGBoost > RF > LSTM).

## Wniosek (materiał na obronę)

Wyciek statystyk skalera był metodologicznie realny, ale liczbowo pomijalny:
przy n=30 000 średnia i odchylenie standardowe policzone na 60% treningowych
są praktycznie identyczne z pełnozbiorowymi, więc żaden wniosek pracy nie
opierał się na tym wycieku. Po naprawie deklaracja „zbiór testowy zamrożony,
niewidziany na żadnym etapie treningu ani preprocessingu" jest prawdziwa
bez gwiazdek.
