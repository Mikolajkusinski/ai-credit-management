# B4: Kontr-eksperyment fairness — modele bez atrybutu SEX

Protokół identyczny z produkcyjnym W3 (60/20/20, seed 42, kalibracja izotoniczna, progi kosztowe na splicie kalibracyjnym); jedyna różnica: kolumny `SEX_*` usunięte z wektora cech. SEX służy wyłącznie do slicingu metryk. LSTM pominięty — jego tensor (3,3) nigdy nie zawierał demografii, więc produkcyjny LSTM (DPD +0.006) już jest punktem odniesienia bez SEX.

| Model | AUC z SEX → bez | Brier z → bez | DPD z SEX → bez | EOD z SEX → bez |
|---|---|---|---|---|
| Random Forest | 0.7741 → 0.7748 | 0.1374 → 0.1369 | +0.0345 → +0.0266 | +0.0282 → +0.0215 |
| XGBoost | 0.7761 → 0.7758 | 0.1360 → 0.1357 | +0.0358 → +0.0105 | +0.0279 → +0.0039 |
| LightGBM | 0.7767 → 0.7756 | 0.1363 → 0.1364 | +0.0351 → +0.0068 | +0.0274 → +0.0024 |
| CatBoost | 0.7793 → 0.7798 | 0.1357 → 0.1357 | +0.0392 → +0.0216 | +0.0329 → +0.0167 |

Maksymalne przesunięcia: |ΔAUC| = 0.0011, |ΔDPD| = 0.0283, |ΔEOD| = 0.0251.

**Odczyt do obrony:** usunięcie SEX przesuwa metryki w stopniu widocznym — patrz tabela; wynik wymaga omówienia w pracy (kierunek zmian wskaże, czy SEX działał bezpośrednio, czy przez korelaty).
