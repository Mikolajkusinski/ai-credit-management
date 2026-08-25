# FIGURY.md — mapa „numer rysunku w pracy → plik → zmiana vs v8 → sekcja"

> Ścieżki względem root repo. PNG 300 DPI (+SVG obok w `thesis_figures/output/`).
> Nazwy plików w `\includegraphics` bez ścieżek — `\graphicspath` w main_test.tex
> pokazuje właściwe katalogi (w Overleafie: wgrać PNG do projektu).

## Rozdział 4 (podmiany figur v8)

| Rys. | Plik | Zmiana vs v8 | Sekcja |
|---|---|---|---|
| 4.1 | `ml-learing-center/thesis_figures/output/rozdzial_4/fig_4_1_podzial_danych.png` | **60/20/20** (było 56/14/30 z legacy 70/30) | 4.1.1 |
| 4.2 | `ml-learing-center/thesis_figures/output/rozdzial_4/fig_4_2_smote.png` | bez zmian (analiza alternatyw) | 4.1.2 |
| 4.3 | `ml-learing-center/thesis_figures/output/rozdzial_4/fig_4_3_krzywe_uczenia_lstm.png` | wariant **W3 (3,3)**, seed 42; w v8 podpisy 4.3↔4.4 były **zamienione** | 4.2.2 |
| 4.4 | `ml-learing-center/thesis_figures/output/rozdzial_4/fig_4_4_hiperparametry_lstm.png` | bez zmian; poprawić PODPIS (zamiana z 4.3) | 4.2.2 |
| 4.5 | `ml-learing-center/thesis_figures/output/rozdzial_4/fig_4_5_heatmapa_rf_cv.png` | **CV-AUC na treningu** (było AUC testu!); ramka na (500, 10) zgodna z tekstem (stara: depth=8) | 4.3.1 |
| 4.6 | `ml-learing-center/thesis_figures/output/rozdzial_4/fig_4_6_feature_importance_rf.png` | z finalnego artefaktu **rf_model_w3** | 4.3.2 |
| 4.7 | `ml-learing-center/thesis_figures/output/rozdzial_4/fig_4_7_heatmapa_xgb_cv.png` | **CV-AUC na treningu** (było AUC testu); ramka (0.02, 4) | 4.4.1 |
| 4.8 | `ml-learing-center/thesis_figures/output/rozdzial_4/fig_4_8_shap_xgb.png` | z finalnego artefaktu **xgb_model_w3**, dane W3 | 4.4.2 |
| 4.9 | `ml-learing-center/thesis_figures/output/rozdzial_4/fig_4_9_cross_validation.png` | bez zmian (schemat 5-fold; po podmianie Z5 ilustruje CV Optuny) | 4.4.1 |
| 4.x (NOWA, opcjonalna) | `ml-learing-center/reports/calibration_comparison_w3.png` | krzywe kalibracji do nowej sekcji 4.6 | 4.6 |

## Rozdział 5 (nowe figury)

| Rys. (propozycja numeru) | Plik | Sekcja |
|---|---|---|
| 5.1 | `ml-learing-center/reports/roc_comparison_w3.png` | 5.2 |
| 5.2 | `ml-learing-center/reports/pr_comparison_w3.png` | 5.2/5.3 |
| 5.3 | `ml-learing-center/reports/bootstrap_auc_w3.png` | 5.3 |
| 5.4a–e | `ml-learing-center/reports/static_vs_dynamic_random_forest_w3.png`, `..._xgboost_w3.png`, `..._lightgbm_w3.png`, `..._catboost_w3.png`, `..._lstm_w3.png` | 5.4 (w pracy min. CatBoost + LSTM; komplet w repo) |
| 5.5a–e | `ml-learing-center/reports/pd_per_window_random_forest.png`, `..._xgboost.png`, `..._lightgbm.png`, `..._catboost.png`, `..._lstm.png` | 5.4 (diagnoza; w pracy 1–2 reprezentatywne) |
| 5.6 | `ml-learing-center/reports/slope_boxplot_catboost_w3.png` (reszta modeli w repo) | 5.4 |
| 5.7 | `ml-learing-center/reports/trajectory_examples_catboost_w3.png` (reszta w repo) | 5.4 |
| 5.10 | `ml-learing-center/thesis_figures/output/rozdzial_5/fig_5_10_audyt_fairness.png` | 5.5b |
| (alt. 5.10) | `ml-learing-center/reports/fairness_selection_rate_w3.png`, `fairness_tpr_fpr_w3.png` | 5.5b (wariant dwóch osobnych) |

## Rozdziały 1–3 (istniejące generatory w `thesis_figures/output/rozdzial_{1,2,3}/`)

Figury 1.1–2.3 bez zmian (v8 OK). Rozdział 3 draftu odwołuje się do
`fig_4_1_podzial_danych.png` (sekcja 3.3.5) oraz diagramu architektury —
diagram w `thesis_figures/output/rozdzial_3/` (jeśli wygenerowany przez
istniejące skrypty `rozdzial_3/`) lub verbatim-ASCII z `rozdzial3.tex`.
