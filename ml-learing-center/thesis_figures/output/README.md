# Wykresy do pracy magisterskiej

Wygenerowane automatycznie skryptami z `thesis_figures/`.
Wszystkie figury dostępne w formacie PNG (300 DPI) oraz SVG.

_Ostatnia aktualizacja: 2026-04-19 15:19_


## Rozdział 1
- **fig_1_1_proces_oceny** — Przepływ etapów oceny zdolności kredytowej od wniosku klienta aż po monitoring spłat, z pętlą aktualizacji danych.
- **fig_1_2_rodzaje_ryzyka** — Hierarchiczna klasyfikacja czterech głównych typów ryzyka kredytowego wraz z krótkim opisem każdego.
- **fig_1_3_porownanie_metod** — Heatmapa porównawcza trzech tradycyjnych metod oceny zdolności kredytowej wg czterech kryteriów (szybkość, koszt, interpretowalność, skuteczność).
- **fig_1_4_ograniczenia_klasyczne** — Wykres radarowy prezentujący istotność sześciu głównych ograniczeń tradycyjnych modeli scoringowych — punkt wyjścia dla uzasadnienia użycia uczenia maszynowego.

## Rozdział 2
- **fig_2_1_taksonomia_ml** — Hierarchiczne drzewo trzech głównych paradygmatów uczenia maszynowego z typowymi zastosowaniami w sektorze finansowym.
- **fig_2_2_pipeline_ml** — Typowy pipeline projektu ML: od pozyskania danych, przez preprocessing i trenowanie, aż po wdrożenie i pętle sprzężenia zwrotnego.
- **fig_2_3_zastosowania_ml** — Wykres słupkowy poziomy prezentujący względną częstość siedmiu obszarów zastosowania ML w finansach na podstawie przeglądu literatury.
- **fig_2_4_architektura_lstm** — Schemat warstw modelu LSTM (Input 6×3 → LSTM 32 → Dropout → Dense 16 → Sigmoid) z oznaczonymi wymiarami tensorów między warstwami.
- **fig_2_5_random_forest** — Schemat algorytmu Random Forest: N niezależnych drzew decyzyjnych wytrenowanych na bootstrapowych próbach danych, a ich predykcje agregowane są przez głosowanie większościowe.
- **fig_2_6_xgboost** — Schemat gradient boostingu w XGBoost: każde kolejne drzewo uczy się residuów poprzedniego, a ważona suma wszystkich drzew tworzy predykcję końcową.
- **fig_2_7_porownanie_algorytmow** — Teoretyczne porównanie czterech podejść (LSTM, Random Forest, XGBoost, scoring tradycyjny) na wykresie radarowym wg sześciu kryteriów. Porównanie empiryczne znajduje się w rysunku 5.5.

## Rozdział 3
- **fig_3_1_rozklad_target** — Rozkład klas zmiennej docelowej w zbiorze UCI (default of credit card clients) — widoczna nierównowaga klas (~22% niespłacających).
- **fig_3_2_histogramy_boxploty** — Histogramy i boxploty czterech kluczowych zmiennych (limit kredytu, wiek, średni rachunek, liczba opóźnień) z podziałem na klasy — pokazują różnice rozkładów między klientami spłacającymi i niespłacającymi.
- **fig_3_3_heatmapa_korelacji** — Trójkątna heatmapa korelacji Pearsona dla 16 zmiennych (w tym zmiennej docelowej Default) — widoczne silne korelacje wewnątrz grup PAY_*/BILL_* oraz umiarkowane powiązania z Default.
- **fig_3_4_preprocessing** — Siedmioetapowy pipeline preprocessingu danych zastosowany w pracy: od surowego CSV, przez feature engineering (wyróżnione), aż po stratyfikowany podział 70/30.
- **fig_3_5_architektura_systemu** — Czterowarstwowa architektura systemu: frontend React, backend .NET, ML-service Flask z trzema modelami oraz warstwa danych UCI.
- **fig_3_6_przeplyw_danych** — Diagram sekwencji opisujący pełny cykl żądania predykcji — od wypełnienia formularza przez klienta aż po prezentację wyniku (8 kroków).
- **fig_3_7_integracja_ai** — Schemat integracji backendu .NET (PredictController + PredictionService) z usługą Flask ML-service wraz z wewnętrznym pipeline'em feature engineering i predykcji trzech modeli.
- **fig_3_8_scenariusze_wyjatkow** — Drzewo decyzyjne pięciu typowych scenariuszy błędów w pipeline predykcji — walidacja żądania i komunikacja z ML-service.
- **fig_3_9_stos_technologiczny** — Stos technologiczny projektu w układzie warstwowym — prezentacja (React), aplikacja (.NET), ML (Flask), modele (sklearn/XGB/TF), dane (pandas/CSV) i infrastruktura (Docker).

## Rozdział 4
- **fig_4_2_smote** — Porównanie przed/po zastosowaniu SMOTE: górny wiersz — rozkład klas, dolny — rzut 2D-PCA 5000 próbek z widocznym zagęszczeniem klasy mniejszościowej po oversamplingu.
- **fig_4_4_hiperparametry_lstm** — Trzy panele wpływu hiperparametrów LSTM (liczba epok, batch size, liczba jednostek) na AUC walidacji — czerwone okręgi zaznaczają konfigurację optymalną.
- **fig_4_5_rf_hiperparametry** — Heatmapa AUC testowego dla Random Forest w siatce n_estimators × max_depth — czerwone obramowanie wskazuje konfigurację z maksymalnym AUC.
- **fig_4_7_grid_search_xgb** — Heatmapa wyników grid search dla XGBoost (learning_rate × max_depth) — zielone obramowanie wskazuje konfigurację z maksymalnym AUC na zbiorze testowym.
- **fig_4_9_cross_validation** — Schemat 5-fold walidacji krzyżowej — w każdej z 5 iteracji inny fold pełni rolę zbioru walidacyjnego (kolor czerwony), pozostałe cztery trenują model.
- **fig_4_5_heatmapa_rf_cv** — RF: CV-AUC 5-fold na treningu W3; czerwona ramka = konfiguracja z main.py (500, 10).
- **fig_4_7_heatmapa_xgb_cv** — XGB: CV-AUC 5-fold na treningu W3; zielona ramka = konfiguracja z main.py (lr=0.02, depth=4).
- **fig_4_1_podzial_danych** — Trójdzielny split 60/20/20 (18 000 / 6 000 / 6 000) z osobną częścią kalibracyjną; zgodny z main.py po leakage-fix 2026-07-07.
- **fig_4_3_krzywe_uczenia_lstm** — Krzywe uczenia finalnego LSTM W3 (EarlyStopping na val_auc); retrening deterministyczny wyłącznie po history, model niezapisywany.
- **fig_4_6_feature_importance_rf** — Top-20 cech wg istotności (Gini) finalnego RF W3 (estymator bazowy spod kalibracji) — dominują świeże zachowania płatnicze i inżynierowane wskaźniki opóźnień.
- **fig_4_8_shap_xgb** — Wartości SHAP finalnego XGB W3 (estymator bazowy, n=1000 z testu) — beeswarm pokazuje kierunek i rozkład wpływu cech, bar średnią globalną istotność.

## Rozdział 5
- **fig_5_1_metryki_modeli** — Zestawienie pięciu metryk klasyfikacji (accuracy, precision, recall, F1, ROC-AUC) dla LSTM, Random Forest i XGBoost — wykres słupkowy z pełną tabelą liczbową pod spodem.
- **fig_5_2_krzywe_roc** — Krzywe ROC trzech modeli na jednym wykresie wraz z wartościami AUC w legendzie — im krzywa bliższa lewego górnego rogu, tym lepszy klasyfikator.
- **fig_5_3_macierze_pomylek** — Macierze pomyłek dla trzech modeli na zbiorze testowym — każda komórka podaje liczbę przypadków oraz udział procentowy w danym wierszu (rzeczywistej klasie).
- **fig_5_4_porownanie_modeli** — Porównanie trzech modeli wg czterech kryteriów (dokładność mierzona AUC, interpretowalność ekspercka, szybkość inferencji, stabilność z bootstrapu) w ujednoliconej skali 1–5.
- **fig_5_5_radar_modeli** — Radar chart prezentujący empiryczne wartości pięciu metryk dla każdego z trzech modeli — szybkie wizualne porównanie mocnych i słabych stron każdego podejścia.
- **fig_5_6_vs_scoring_tradycyjny** — Porównanie modeli ML z baseline'em klasycznego scoringu (regresja logistyczna) wg trzech metryk (accuracy, F1, ROC-AUC) — kwantyfikacja przewagi uczenia maszynowego.
- **fig_5_7_interpretowalnosc** — Heatmapa 5×3 prezentująca interpretowalność trzech modeli w pięciu wymiarach — pod nią oceny sumaryczne (LSTM = niska, RF i XGB = średnio/wysoka).
- **fig_5_8_weryfikacja_hipotez** — [PLACEHOLDER] Tabela wizualna weryfikacji hipotez — hipoteza → wynik → status (potwierdzona/częściowo/odrzucona). Podmień HYPOTHESES w pliku generatora na rzeczywiste hipotezy z pracy.
- **fig_5_9_wnioski_kierunki** — [PLACEHOLDER] Mind-map wniosków i kierunków dalszych badań. Podmień treści w listach CONCLUSIONS i FUTURE_WORK na własne.
- **fig_5_10_audyt_fairness** — Audyt fairlearn DPD/EOD wrt SEX dla 5 modeli W3 przy progach kosztowych; wszystkie |diff| <= 0.04 przy limicie 0.10; panel (a) pokazuje też lukę strukturalną ~0.021 z różnicy base rate.
