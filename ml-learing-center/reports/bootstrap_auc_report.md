# B3: Bootstrap wariancji AUC (40 powtórzeń zbioru testowego)

Repróbkowanie ze zwracaniem, n=6000, 40 powtórzeń, seed=42. Realizacja obietnicy z sekcji 4.5 pracy.

| Model | AUC (pełny test) | Bootstrap mean | Std | 95% CI |
|---|---:|---:|---:|---|
| Random Forest | 0.7741 | 0.7754 | 0.0064 | [0.7648, 0.7860] |
| XGBoost | 0.7761 | 0.7770 | 0.0068 | [0.7670, 0.7888] |
| LightGBM | 0.7767 | 0.7779 | 0.0069 | [0.7657, 0.7898] |
| CatBoost | 0.7793 | 0.7805 | 0.0062 | [0.7702, 0.7928] |
| LSTM | 0.7614 | 0.7627 | 0.0060 | [0.7534, 0.7717] |

## Rozróżnialność par modeli (bootstrap sparowany różnicy AUC)

| Para | Δ AUC (mean) | 95% CI różnicy | CI zawiera 0? |
|---|---:|---|---|
| Random Forest vs XGBoost | -0.0015 | [-0.0047, +0.0019] | tak — nierozróżnialne |
| Random Forest vs LightGBM | -0.0025 | [-0.0075, +0.0010] | tak — nierozróżnialne |
| Random Forest vs CatBoost | -0.0051 | [-0.0085, -0.0021] | nie — **rozróżnialne** |
| Random Forest vs LSTM | +0.0127 | [+0.0080, +0.0199] | nie — **rozróżnialne** |
| XGBoost vs LightGBM | -0.0009 | [-0.0044, +0.0017] | tak — nierozróżnialne |
| XGBoost vs CatBoost | -0.0035 | [-0.0075, -0.0006] | nie — **rozróżnialne** |
| XGBoost vs LSTM | +0.0143 | [+0.0076, +0.0221] | nie — **rozróżnialne** |
| LightGBM vs CatBoost | -0.0026 | [-0.0063, +0.0010] | tak — nierozróżnialne |
| LightGBM vs LSTM | +0.0152 | [+0.0092, +0.0239] | nie — **rozróżnialne** |
| CatBoost vs LSTM | +0.0178 | [+0.0116, +0.0245] | nie — **rozróżnialne** |

**Wniosek do pracy:** różnice między modelami drzewiastymi raportować jako porównywalne, chyba że CI różnicy nie zawiera zera (patrz tabela); przewaga nad LSTM jest oczekiwanie stabilna. Uwaga metodologiczna: bootstrap repróbkuje wyłącznie zbiór testowy przy ustalonych modelach — nie obejmuje wariancji treningu.
