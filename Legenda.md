# Legenda.md — słownik kluczowych pojęć projektu

> **Dla kogo:** osoby, która nie brała udziału w projekcie, ale ma za chwilę zaprezentować go na seminarium dyplomowym i potrzebuje rozumieć, o czym mówi.
>
> **Jak korzystać:** czytaj od góry — kategorie ułożone w kolejności, w jakiej pojawiają się w pracy (domena kredytowa → dane → modele → metryki → kalibracja → monitoring → interpretowalność → fairness → architektura → metodologia). Każdy termin: **definicja** + **rola w projekcie**. Dla najważniejszych pojęć (PD, sliding-window, AUC, Brier, kalibracja izotoniczna, monitoring trajektorii, SHAP, DPD/EOD) — głębsza wersja.
>
> **Co warto przeczytać równolegle:** `PrezentacjaSeminarium2.md` (kontekst i liczby), `plan_sprintow_wariant_B.md` (metodologia projektu).

---

## Spis treści

- [A. Domena: kredyt, ryzyko, regulacje](#a-domena-kredyt-ryzyko-regulacje)
- [B. Dane i sliding-window panel](#b-dane-i-sliding-window-panel)
- [C. Modele uczenia maszynowego](#c-modele-uczenia-maszynowego)
- [D. Inżynieria cech (feature engineering)](#d-inżynieria-cech-feature-engineering)
- [E. Metryki ewaluacji](#e-metryki-ewaluacji)
- [F. Kalibracja prawdopodobieństw](#f-kalibracja-prawdopodobieństw)
- [G. Decyzje i progi alertu](#g-decyzje-i-progi-alertu)
- [H. Monitoring kalendarzowy (Wariant B)](#h-monitoring-kalendarzowy-wariant-b)
- [I. Interpretowalność (SHAP)](#i-interpretowalność-shap)
- [J. Fairness i audyt dyskryminacji](#j-fairness-i-audyt-dyskryminacji)
- [K. Architektura systemu (REST + persystencja)](#k-architektura-systemu-rest--persystencja)
- [L. Stack technologiczny](#l-stack-technologiczny)
- [M. Metodologia pracy zespołowej](#m-metodologia-pracy-zespołowej)
- [N. Pojęcia specyficzne dla tej pracy](#n-pojęcia-specyficzne-dla-tej-pracy)

---

## A. Domena: kredyt, ryzyko, regulacje

### PD (Probability of Default)
Prawdopodobieństwo, że dłużnik nie wykona zobowiązania kredytowego w określonym horyzoncie (zwykle 12 miesięcy). To **kluczowa wielkość** w nowoczesnej ocenie ryzyka kredytowego. W naszym projekcie PD liczone jest dla horyzontu „default w następnym miesiącu" i serwowane jako liczba w przedziale [0, 1] z każdego z 5 modeli ML.

### LGD (Loss Given Default)
**Strata przy defaulcie** — procent ekspozycji, którego bank nie odzyska po defaulcie kredytobiorcy (po realizacji zabezpieczeń, ugodach, windykacji). Razem z PD i EAD składa się na *expected loss* = `PD × LGD × EAD`. **W projekcie nie modelowane** — zbiór UCI nie zawiera danych o odzyskach. Wzmianka pojawia się w Roz. 1 jako kontekst teorii kredytu.

### EAD (Exposure at Default)
**Ekspozycja w momencie defaultu** — kwota, jaką dłużnik jest winien w chwili niewypłacalności. Dla kart kredytowych odpowiada faktycznie wykorzystanemu limitowi. **W projekcie nie modelowane** (jak LGD).

### Default
Niespełnienie zobowiązania umownego — typowo opóźnienie spłaty ≥ 90 dni lub upadłość. W zbiorze UCI etykieta binarna `default_payment_next_month` (1 = default, 0 = brak). To etykieta, którą wszystkie modele projektu próbują przewidzieć.

### Credit scoring
Liczbowa ocena ryzyka kredytowego klienta. Dwa tradycyjne nurty: (a) **scoring aplikacyjny** (decyzja na wejściu, na podstawie wniosku) i (b) **scoring behawioralny** (ocena istniejącej relacji, na podstawie historii spłat). Wariant B tego projektu należy do (b) — operujemy na 6-miesięcznej historii istniejącego klienta.

### Karta scoringowa
Klasyczna forma scoringu: każdej zmiennej przypisuje się punktację za przedziały wartości, suma punktów daje wynik. Łatwo interpretowalna, ale ograniczona w pochwytywaniu interakcji nieliniowych. **W pracy:** opisana jako baseline w Roz. 1.2.1.

### Scoring behawioralny
Ocena ryzyka aktywnego klienta na podstawie *zachowania* (terminowość spłat, wykorzystanie limitu, historia opóźnień) zamiast tylko cech wnioskowych. To bezpośredni intelektualny przodek monitoringu kalendarzowego Wariantu B.

### Cykl życia ekspozycji
Faza relacji: udzielenie → obsługa → monitoring → ewentualnie restrukturyzacja / windykacja. **Wariant B operuje na fazie monitoringu** — nie decyduje, czy udzielić kredytu, lecz śledzi już istniejącą ekspozycję.

### Prawo bankowe (art. 69, art. 70)
Polskie regulacje: art. 69 definiuje umowę kredytową; art. 70 wymaga od banku zbadania **zdolności kredytowej** kredytobiorcy. Cytowane w Roz. 1.1 pracy jako podstawa prawna oceny ryzyka.

### Rekomendacje T / S KNF
Wytyczne polskiego nadzoru (KNF):
- **Rekomendacja T** — zarządzanie ryzykiem detalicznych ekspozycji kredytowych.
- **Rekomendacja S** — zarządzanie ekspozycjami zabezpieczonymi hipotecznie.
Cytowane w Roz. 1.2.2 jako otoczenie regulacyjne polskiej bankowości.

### EBA / wytyczne EBA
European Banking Authority — europejski organ nadzoru wydający wiążące wytyczne (np. **GL/2020/06** dotyczące udzielania i monitoringu kredytów). Stanowią kontekst regulacyjny dla scoringów ML w UE.

### AI Act (Art. 9 / Art. 15)
Unijne rozporządzenie o sztucznej inteligencji (2024). **Klasyfikuje credit scoring jako system AI „wysokiego ryzyka"** (Annex III). Art. 9 wymaga zarządzania ryzykiem, Art. 15 — adekwatności, robustności i braku dyskryminacji. **W projekcie**: zaadresowane przez kalibrację (Brier), audyt fairness (CREDIT-112) i SHAP (CREDIT-107) — domykane jako AI Act compliance checkbox.

### RODO (GDPR)
Rozporządzenie o ochronie danych osobowych. Dla scoringu istotne: prawo do wyjaśnienia decyzji zautomatyzowanej (Art. 22) → przekłada się na wymóg interpretowalności (SHAP). Atrybuty chronione (płeć, pochodzenie, religia, orientacja) wymagają specjalnej ochrony i audytu fairness.

### Atrybuty chronione (sensitive features)
Cechy, względem których system nie może dyskryminować pośrednio ani bezpośrednio. W UCI dostępne: `SEX`, `AGE`, `EDUCATION`, `MARRIAGE`. **W projekcie audytujemy SEX** (CREDIT-112) — to standard w literaturze credit scoring; pozostałe to kandydaci na rozszerzenia.

---

## B. Dane i sliding-window panel

### UCI „Default of Credit Card Clients" (Taiwan 2005)
Publiczny zbiór UCI Machine Learning Repository: 30 000 klientów banku tajwańskiego, 22 cechy wejściowe, etykieta defaultu w październiku 2005. To **standardowy benchmark** w literaturze credit scoring — pozwala porównywać wyniki z istniejącymi pracami.

### 22 cechy wejściowe UCI
Pięć demograficznych (`LIMIT_BAL`, `SEX`, `EDUCATION`, `MARRIAGE`, `AGE`) + 6 statusów płatności (`PAY_0`, `PAY_2`..`PAY_6`) + 6 sald (`BILL_AMT1..6`) + 6 wpłat (`PAY_AMT1..6`). **Razem 22 surowych pól** — z nich projekt wylicza 13 cech pochodnych w `engineer_features()`.

### LIMIT_BAL
Limit karty kredytowej w dolarach tajwańskich (zakres 10 000–1 000 000). W projekcie cecha demograficzna, używana przez wszystkie modele.

### PAY_0..PAY_6 (status płatności)
Stan spłaty za 6 ostatnich miesięcy: `-2` = brak konsumpcji, `-1` = spłacone w pełni, `0` = aktywne saldo / na czas, `1..8` = liczba miesięcy opóźnienia. **Quirk UCI: kolumna `PAY_1` nie istnieje** — sekwencja to PAY_0, PAY_2, PAY_3, PAY_4, PAY_5, PAY_6 (znana cecha zbioru). Mapowanie kalendarzowe: PAY_0 = wrzesień (najnowszy), PAY_6 = kwiecień (najstarszy).

### BILL_AMT1..6 / PAY_AMT1..6
Salda rachunku (`BILL_AMT`) i wpłaty (`PAY_AMT`) za 6 miesięcy. `BILL_AMT1` = wrzesień, `BILL_AMT6` = kwiecień (analogicznie dla PAY_AMT). Mogą być ujemne (nadpłaty).

### Niezbalansowanie klas (class imbalance)
W UCI ~22% klientów defaultuje, ~78% nie. To **lekkie niezbalansowanie** — dla credit scoring typowe. W projekcie zamiast wagi klas używamy: (a) kalibracji izotonicznej (CREDIT-105) i (b) progów cost-optymalnych (CREDIT-106), co jest bardziej defensible niż `class_weight="balanced"`.

### Stratified split
Podział train/test zachowujący proporcję klas w obu podzbiorach. **W projekcie:** 80% train / 20% test, `stratify=y`, `random_state=42` → 6 000 klientów w teście, byte-identyczny zestaw w całym pipeline'ie ewaluacyjnym.

### Sliding-window panel — KLUCZOWE POJĘCIE
**Technika konstruowania panelu czasowego z jednego wiersza danych.** UCI dostarcza statyczny snapshot (1 wiersz = 1 klient × 6 miesięcy historii × 1 etykieta). Wariant B wymaga panelu czasowego, ale **nie wolno fabrykować danych**. Sliding-window rozwiązuje to przesuwając okno 3-miesięczne wzdłuż 6 dostępnych miesięcy → **4 okna 3-mies. per klient** (W0..W3), bez generowania nowych wartości.

### Okna W0..W3
Cztery nakładające się okna 3-miesięczne, od najstarszego do najnowszego:

| Okno | Miesiące | PAY | BILL_AMT | PAY_AMT |
|------|----------|-----|----------|---------|
| W0 (najstarsze) | kwi-cze | 6, 5, 4 | 6, 5, 4 | 6, 5, 4 |
| W1 | maj-lip | 5, 4, 3 | 5, 4, 3 | 5, 4, 3 |
| W2 | cze-sie | 4, 3, 2 | 4, 3, 2 | 4, 3, 2 |
| W3 (najnowsze) | lip-wrz | 3, 2, 0 | 3, 2, 1 | 3, 2, 1 |

Modele trenowane na W3 (najnowsze, zgodne z etykietą październikową) → inferencja na W0..W3 → **4-punktowa trajektoria PD**.

### Zasada „nie fabrykujemy danych"
Reguła nadrzędna pracy: każde okno W0..W3 to **realny 3-mies. wycinek prawdziwej historii klienta**. Etykieta defaultu (październik) jest wspólna dla wszystkich okien — nie przypisujemy klientowi „pośrednich" etykiet w marcu, kwietniu itd. To zachowuje uczciwość metodologiczną i odporność na zarzuty „augmentacja danych".

### Zgodność rozkładów trening = inferencja
Trening odbywa się na oknie W3 (3 mies., zgodne z etykietą). W inferencji **ten sam model** przesuwany jest na W0, W1, W2, W3 → ponieważ każde okno ma identyczną strukturę (3 timesteps × 3 kanały), rozkład inferencyjny jest taki sam jak treningowy. **Brak out-of-distribution shift** — to fundament metodologiczny Wariantu B.

### 3-way split (train / calib / test)
Podział 60/20/20 — train dla treningu modelu bazowego, calib dla dopasowania kalibratora izotonicznego, test dla finalnej oceny. Konieczny w CREDIT-105: kalibrator nie może widzieć danych treningowych modelu bazowego (inaczej kalibracja byłaby przepasowana).

### `random_state=42`
Standardowy seed używany w całym projekcie do deterministycznych podziałów i tasowania. Pozwala na **reprodukowalność** wyników między uruchomieniami i między skryptami (każdy raport ma ten sam test set).

---

## C. Modele uczenia maszynowego

### Random Forest (RF)
**Bagging** drzew decyzyjnych — wiele drzew trenowanych na różnych próbkach bootstrapowych i podzbiorach cech, finalna predykcja = średnia (regresja) lub głosowanie (klasyfikacja). **Mocna strona:** odporność na overfitting, stabilność. **Słaba:** wolniejszy trening i większa pamięć niż gradient boosting. **W projekcie:** 500 drzew, depth 10; AUC 0.7741 (po kalibracji).

### XGBoost
**Extreme Gradient Boosting** — sekwencyjne dodawanie słabych drzew, każde koryguje błędy poprzednich. **Mocna strona:** zwykle najwyższe AUC w tabularnych konkursach Kaggle. **Słaba:** wrażliwy na hiperparametry. **W projekcie:** 800 iteracji, lr 0.02, depth 4; AUC 0.7760.

### LightGBM
Wariant gradient boosting Microsoftu (2017). Trzy innowacje: (a) **histogram-based binning** (binowanie cech ciągłych — szybsze niż exact split), (b) **leaf-wise growth** (rozrost drzewa po liściu o największej redukcji loss, zamiast level-wise), (c) **GOSS** (Gradient-based One-Side Sampling — selekcja próbek po wielkości gradientu) i **EFB** (Exclusive Feature Bundling — łączenie rzadko współwystępujących cech). Wynik: szybkość i pamięć. **W projekcie:** dodany w CREDIT-109; AUC 0.7764.

### CatBoost
Wariant Yandexa (2018). Dwie innowacje: (a) **ordered boosting** — używa permutacji do redukcji *prediction shift* (uprzedzenia spowodowanego użyciem tej samej próbki do estymacji gradientu i predykcji), (b) **ordered target statistics** — natywna obsługa cech kategorycznych bez one-hot. **W projekcie:** dodany w CREDIT-109; **best single model** AUC 0.7802, Brier 0.1354.

### LSTM (Long Short-Term Memory)
Rekurencyjna sieć neuronowa z **bramkami** (forget, input, output) — pozwala uczyć się długoterminowych zależności w sekwencjach, omijając problem znikającego gradientu. W projekcie warstwa LSTM (32 jednostek) na wejściu o kształcie `(3, 3)` — 3 kroki czasowe × 3 kanały (PAY, BILL, PAY_AMT). **AUC 0.7610** — nieco z tyłu, ponieważ 3-elementowa sekwencja to minimum, na którym LSTM może operować.

### Stacking ensemble (LR meta-learner)
**Modele dwupiętrowe:** bazowe modele (RF, XGB, LightGBM, CatBoost, LSTM) generują predykcje out-of-fold, na nich trenuje się **meta-model** (zwykle prosta regresja logistyczna), który nauczy się łączyć opinie bazowych. **W projekcie:** zaplanowany jako CREDIT-113 (Sprint 6); oczekiwany uplift AUC 0.5–1 pp + lepsza kalibracja.

### Out-of-distribution (OOD) shift
Sytuacja, gdy rozkład danych w inferencji różni się od treningowego → model widzi „obce" przypadki i jego predykcje są niewiarygodne. **W projekcie:** sliding-window jest projektowany tak, aby OOD shift nie wystąpił (struktura W0..W3 identyczna jak W3 treningowy).

### Class imbalance handling
Trzy strategie radzenia z niezbalansowaniem klas: (a) **oversampling** (np. SMOTE — generowanie syntetycznych próbek mniejszości), (b) **weighting** (`class_weight="balanced"` lub `scale_pos_weight` w XGB — wyższa kara za błędy klasy mniejszościowej), (c) **cost-sensitive thresholds** — domyślny próg 0.5 zastąpiony progiem minimalizującym oczekiwaną stratę. **W projekcie używamy (c)** plus kalibracji — strategia bardziej defensible niż weighting.

---

## D. Inżynieria cech (feature engineering)

13 cech pochodnych liczonych na 3 miesiącach okna (kontrast: PDF v8 nadal opisuje wersję 6-mies.):

### PAY_mean
Średnia statusu płatności w oknie — proxy „przeciętnej terminowości spłat". Wyższe = gorzej.

### PAY_max
Najgorszy status w oknie (max). Cecha sygnałowa: pojedynczy miesiąc poważnego opóźnienia kosztuje więcej niż wiele drobnych.

### BILL_mean
Średnie saldo w oknie. Pomocne dla normalizacji utilization rate.

### BILL_std
Odchylenie standardowe sald — proxy zmienności zachowania. Wysokie = chaotyczne wydatki.

### BILL_trend
Nachylenie regresji liniowej dopasowanej do 3 sald w oknie. Wzrost = klient zaciąga coraz więcej długu.

### payment_ratio
`PAY_AMT / BILL_AMT` — jaką część zobowiązania klient spłacił. Niski = ryzyko.

### late_count
Liczba miesięcy w oknie, w których klient był w jakimkolwiek opóźnieniu (`PAY ≥ 1`).

### severe_late
Binarna: czy w oknie był chociaż jeden miesiąc z poważnym opóźnieniem (`PAY ≥ 2`). Cecha kluczowa — silnie skorelowana z defaultem.

### utilization_rate
`BILL_mean / LIMIT_BAL` — jaki procent limitu klient wykorzystuje. Wysokie wykorzystanie limitu zwiększa ryzyko (mniej buforu).

### recent_pay_status
Status najnowszego miesiąca w oknie (najświeższa informacja). Często najsilniejszy pojedynczy predyktor.

### Bug-fix CREDIT-102 (silent train/serve corruption)
W Sprincie 1 wykryto **2 bugi w `ml-service/app.py`**: `utilization_rate` używał `BILL_AMT1 / LIMIT_BAL` zamiast `BILL_mean / LIMIT_BAL`; `severe_late` używał `.sum()` zamiast `.any().astype(int)`. **Skutek przed fixem:** Flask robił scoring na cechach poza rozkładem treningowym — modele zwracały „poprawne" odpowiedzi na zepsute dane. Defensible talking point podczas obrony: rygor train/serve consistency.

---

## E. Metryki ewaluacji

### AUC (Area Under ROC Curve)
Pole pod krzywą ROC. Mierzy **zdolność dyskryminacyjną** — prawdopodobieństwo, że losowy default dostanie wyższy score niż losowy non-default. **Zakres** [0.5, 1.0]: 0.5 = losowy, 1.0 = idealny. **W projekcie:** główna metryka rankingu modeli. Wartości 0.76-0.78 są typowe dla credit scoring na UCI.

### ROC (Receiver Operating Characteristic)
Krzywa pokazująca trade-off między **TPR** (true positive rate) a **FPR** (false positive rate) przy przechodzeniu progu od 1.0 do 0.0. Każdy punkt = inny próg decyzyjny. ROC nie zależy od proporcji klas — to jej zaleta nad accuracy.

### Gini coefficient
`Gini = 2 × AUC − 1`. Liniowe przeskalowanie AUC do zakresu [0, 1]. **Standard w bankowości** — częściej raportowane niż AUC. W projekcie podane w tabeli metryk obok AUC dla porównań z literaturą.

### KS (Kolmogorov-Smirnov)
Maksymalna różnica między dystrybuantami PD dla defaultów i non-defaultów. **Wysokie KS** (np. 0.4) = klasy dobrze rozdzielone. **W projekcie:** najlepszy XGBoost (0.4248). KS jest mniej wrażliwe na proporcje klas niż AUC i często używane w scoringu.

### Brier Score
Średni kwadrat błędu między PD a etykietą binarną. **Im niżej, tym lepiej**. Mierzy **łącznie dyskryminację i kalibrację** — model z wysokim AUC, ale niekalibrowanymi PD, dostanie wysoki Brier. **W projekcie kluczowy**, bo trajektoria PD wymaga kalibrowanych liczb. Spadek Briera o 19-24% po izotonic = dowód, że kalibracja działa.

### Precision / Recall / F1
Klasyczne metryki klasyfikacji (po wyborze progu):
- **Precision** = TP / (TP + FP) — z tych, których zaalarmowaliśmy, ile faktycznie zdefaultowało.
- **Recall** (czułość, TPR) = TP / (TP + FN) — z tych, którzy zdefaultowali, ilu złapaliśmy.
- **F1** = 2 × Precision × Recall / (Precision + Recall) — harmoniczna średnia.

Dla credit scoring **mniej istotne niż AUC + Brier**, bo wymagają stałego progu, a my używamy progu cost-optymalnego.

### Confusion matrix (macierz pomyłek)
Tabela 2×2: TP / FP / FN / TN dla wybranego progu. **W projekcie:** publikowana w `reports/confusion_*_w3.png` przy progu 0.5 (referencyjne) — w produkcji używamy progu cost-optymalnego.

### PR curve (Precision-Recall)
Trade-off Precision vs Recall. **Bardziej informatywna od ROC dla niezbalansowanych klas** — przy 22% defaultów PR uchwyca to, czego ROC nie widzi. **W projekcie:** `pr_comparison_w3.png` jako uzupełnienie ROC overlay.

### Calibration curve / Reliability diagram
Wykres: na osi X przewidywane PD w binach (np. 0.0-0.1, 0.1-0.2, ...), na osi Y faktyczna częstość defaultu w tym binie. **Idealnie pokrywa się z diagonalą.** **W projekcie:** `calibration_comparison_w3.png` po izotonic — wszystkie 5 modeli blisko diagonali.

### Catch rate
Procent defaulterów, których system flaguje przy danym progu (= recall). **W projekcie:** używane jako oś Y w eksperymencie static-vs-dynamic (CREDIT-111).

### False Alarm rate (FA)
Procent non-defaulterów, których system błędnie zaalarmował (= FPR). Operacjonalizacja „budżetu fałszywych alarmów" — w realnym banku liczba false alerts jest twardo ograniczona (każdy wymaga ręcznego review).

---

## F. Kalibracja prawdopodobieństw

### Kalibracja vs ranking
Model może mieć **wysokie AUC** (dobry ranking) ale **złe absolutne PD** (np. zawsze zaniżone). Brier penalizuje to, AUC nie. **Kalibracja** = dopasowanie monotonicznej funkcji na surowym output modelu tak, by przewidywane PD odpowiadały realnym częstościom defaultów w populacji.

### Isotonic regression
**Nieparametryczna kalibracja** — dopasowuje monotonicznie rosnącą funkcję schodkową na (raw_score, label). Nie zakłada konkretnej rodziny krzywych (kontrast: Platt zakłada sigmoid). **W projekcie:** sklearn `IsotonicRegression` dla LSTM (raw output → calibrated PD).

### Platt scaling
**Parametryczna kalibracja** — dopasowuje logistic regression na (raw_score, label). Szybsza, mniej elastyczna. **W projekcie nie używana** — drzewa nie pasują do sigmoidalnej kalibracji (możliwy underfit).

### CalibratedClassifierCV (sklearn)
Wrapper sklearn owijający dowolny klasyfikator kalibratorem. **W projekcie:** `CalibratedClassifierCV(FrozenEstimator(base), method='isotonic', cv='prefit')` dla RF/XGB/LightGBM/CatBoost.

### FrozenEstimator
Nowy klasa sklearn (od 1.6) — owinięcie pre-trenowanego modelu tak, by `CalibratedClassifierCV` mógł dopasować kalibrator na calib secie **bez retreningu bazy**. Wcześniej wymagało `cv='prefit'`; FrozenEstimator daje czystsze API.

### Monotonicity (kalibracji)
Izotonic to **funkcja monotoniczna** — zachowuje ranking surowych predykcji. **Konsekwencja:** AUC i Gini się nie zmieniają (ranking taki sam), zmienia się tylko Brier (kalibracja). To jest *dlaczego* w projekcie Brier po izotonic spada o 19-24%, a AUC pozostaje bez zmian.

### Reliability diagram
Drugie określenie *calibration curve*. **W projekcie:** `calibration_comparison_w3.png`. Jeśli linia modelu leży poniżej diagonali → model **przeszacowuje** ryzyko; powyżej → **zaniża**.

---

## G. Decyzje i progi alertu

### Threshold / cut-off (próg decyzyjny)
Wartość PD, powyżej której system flaguje klienta jako „ryzykownego". Standard akademicki: **0.5** (próg neutralny). W praktyce credit scoring 0.5 jest rzadko optymalne — zwykle używa się progu cost-optymalnego.

### Asymmetric loss (asymetryczna funkcja kosztu)
Założenie, że **FN ≠ FP kosztem**. W kredycie: przegapienie defaultu (FN — udzielona pożyczka okazała się stratna) kosztuje znacznie więcej niż fałszywy alarm (FP — niepotrzebna inspekcja). Standardowa asymetria: **FN = 5× FP**.

### Cost ratio FN:FP
Stosunek kosztu FN do FP. **W projekcie 5:1** — typowa wartość dla credit scoring (przykład z literatury: Hand & Henley 1997, Verbraken et al. 2014). Sensitivity analysis (3:1, 10:1, 20:1) jest kandydatem na appendix CREDIT-114.

### Cost-optimal threshold (próg cost-optymalny)
Próg minimalizujący oczekiwany koszt `5·FN + 1·FP` na test secie. **W projekcie (CREDIT-106):** RF 0.145, XGB 0.180, LightGBM 0.160, CatBoost 0.130, LSTM 0.175 — wszystkie znacznie poniżej 0.5. Bias w stronę niskich progów to bezpośrednia konsekwencja asymetrii kosztu.

### `alert_thresholds.json`
Plik zapisujący 5 progów cost-optymalnych + meta (cost ratio, źródło, data). Ładowany przez Flask przy starcie, serwowany w response `/predict/timeseries` jako `costThresholds`. Frontend używa go do kolorowania punktów Timeline per model.

### `windowAlerts`
Tabela bool 5 modeli × 4 okna w response Flaska — wskazuje, w których oknach (W0..W3) PD przekroczyło próg cost-optymalny tego modelu. Pozwala na granularny semafor („alert wystartował już w W1") zamiast pojedynczego sygnału.

---

## H. Monitoring kalendarzowy (Wariant B)

### Wariant B (definicja)
Schemat oceny, w którym **ten sam klient jest oceniany wielokrotnie w czasie**. System śledzi trajektorię PD przez kolejne migawki i wykrywa pogorszenie sytuacji **zanim** dojdzie do defaultu. Kontrast: Wariant A = jednorazowa ocena statyczna (PD z jednej migawki, decyzja, koniec).

### Snapshot (migawka)
Pojedynczy „pomiar" klienta w konkretnym momencie kalendarzowym — 22 cechy + data. Każda migawka generuje 1 trajektorię PD (4 punkty W0..W3) per model. **W projekcie:** persistowane w tabeli `Snapshot` w PostgreSQL.

### Trajektoria PD
**Kluczowy artefakt Wariantu B.** Sekwencja PD dla okien W0, W1, W2, W3 jednej migawki, *plus* sekwencja PD W3 z kolejnych migawek tego samego klienta w czasie. Pierwsza (W0→W3) jest **wewnątrz-migawkowa** (analityczny widok 3-miesięcznych okien), druga (snapshot 1 → snapshot N) jest **między-migawkowa** (kalendarzowa historia). To rozróżnienie jest często mylące i wymaga klarowności na slajdach.

### Slope (W3 − W0)
Nachylenie trajektorii PD: `slope = PD_W3 − PD_W0` per model. **Reguła alertu:** slope > +0.10 → `INCREASING_RISK`; slope < −0.10 → `DECREASING_RISK`; |slope| ≤ 0.10 → `STABLE`. Próg 0.10 ustalono w kontrakcie CREDIT-210.

### INCREASING_RISK / DECREASING_RISK / STABLE
Trzy kategorie alertu trendu. Wyświetlane jako semafor (czerwony / zielony / żółty) w `TrendAlerts.tsx`.

### Static rule vs Monitoring rule (eksperyment CREDIT-111)
**Dwie reguły decyzyjne** porównane przy tym samym budżecie FA:
- **Static:** flaguj jeśli `PD_W3 ≥ threshold` (jedna ocena, jedno PD).
- **Monitoring:** flaguj jeśli `max(PD_W0, PD_W1, PD_W2, PD_W3) ≥ threshold` (max-aggregator po 4 oknach).

Eksperyment kanoniczny dla dowodu tezy: który schemat ma wyższy catch rate przy tym samym FA.

### max-aggregator (i jego cena)
`max(W0..W3)` widzi **4× więcej szumu** niż pojedyncze skalibrowane W3 — każde okno ma swój własny rozkład fałszywych alarmów, max sumuje je. Dlatego przy tym samym budżecie FA monitoring musi mieć **wyższy próg** niż statyka, co kosztuje 1-8 pp catch rate. Inne agregatory (np. `mean(W0..W3)`, `slope > 0 + last(W3) > θ`) są alternatywami; max wybrano w CREDIT-210 dla prostoty.

### Lead time
**Wyprzedzenie ostrzeżenia.** Dla defaulterów, którzy zostali złapani: ile okien przed W3 system zaalarmował po raz pierwszy. **W projekcie:** mean lead 1.99-2.19 okien per model ≈ **2 miesiące wcześniej** niż statyka. Główny argument za monitoringiem.

### Catch rate vs lead time
**Dwie konkurencyjne metryki**: catch rate (ile złapaliśmy) i lead time (jak wcześnie złapaliśmy). Statyka wygrywa catch rate (mniej szumu), monitoring wygrywa lead time (4 szansy zamiast 1). Honest verdict pracy: monitoring **nie dominuje strictly**; bilans jest funkcją modelu kosztów.

### only_monitor_catches
Liczba defaulterów złapanych **wyłącznie przez monitoring**, a nieznalezionych przez statykę przy tym samym budżecie FA. **W projekcie (FA=10%):** 36-72 per model. Argument za monitoringiem nawet przy gorszej catch rate — to są klienci, których statyka by przegapiła zupełnie.

### slope_auc vs w3_auc
Eksperyment z CREDIT-110: czy sam slope (jako feature) ma moc predykcyjną?
- **w3_auc** ~0.77 — AUC pojedynczego PD W3 (silny predyktor).
- **slope_auc** ~0.59 — AUC slope jako feature (słaby standalone).

Wniosek: monitoring **dodaje** wymiar czasu do dobrego pojedynczego PD, nie **zastępuje** go. Slope sam w sobie jest niewystarczający.

---

## I. Interpretowalność (SHAP)

### SHAP (SHapley Additive exPlanations)
Metoda wyjaśnialności oparta na **wartościach Shapleya** z teorii gier kooperatywnych. Każdej cesze przypisuje wkład w odchylenie predykcji od średniej (`expected_value`). SHAP ma **3 pożądane własności**: lokalna dokładność (suma wkładów = predykcja), brak wpływu nieobecnych cech, monotoniczność. **Standard regulatorny** dla wyjaśniania decyzji ML w UE (AI Act, RODO Art. 22).

### Shapley values (krótko, teoria)
Z teorii gier: gracze (cechy) tworzą koalicje, każdy dostaje wkład proporcjonalny do swojego marginalnego udziału w wartości dodanej. Dla ML: średni wkład cechy do predykcji po wszystkich możliwych permutacjach.

### TreeExplainer
Optymalna implementacja SHAP dla **drzew decyzyjnych** (RF, XGB, LightGBM, CatBoost). **Exact**, nie sampling, czas O(`TLD²`) gdzie T = liczba drzew, L = liście, D = głębokość. **W projekcie:** 102 ms dla 4 modeli × 22 cechy — 20× pod DoD 2s.

### KernelExplainer
Generyczny SHAP dla dowolnego modelu (działa też dla LSTM, sieci, MLP). **Sampling-based** — wolniejszy o rzędy wielkości niż TreeExplainer. **W projekcie nie używany** — wybiłby budżet czasu dla LSTM (~10s na predykcję).

### Top-5 features
Konwencja projektu: w response Flaska zwracamy 5 cech o najwyższej **wartości absolutnej** SHAP per model. Top-5 to pragmatyczny kompromis między informatywnością a czytelnością UI.

### Konwencja znaku (+/−)
**Wartość > 0** = cecha pcha PD w górę (w stronę DEFAULT), w UI **czerwony pasek (→)**. **Wartość < 0** = pcha PD w dół, **zielony pasek (←)**. Długość paska proporcjonalna do |value| / max.

### `_unwrap_calibrated`
Helper w `ml-service/app.py` wyciągający bazowy estimator z otoczki `CalibratedClassifierCV(FrozenEstimator(base))`. Niezbędny, bo TreeExplainer nie umie chodzić po kalibratorze izotonicznym — pracuje na surowym drzewie. **Bezpieczne, bo kalibracja jest monotoniczna** — ranking cech zachowany.

### SHAP a kalibracja
SHAP liczymy na surowym output bazowego modelu, **nie** na skalibrowanym. To uczciwe: izotonic jest monotoniczne, więc ranking ważności cech taki sam, ale absolutne wartości SHAP nie są kalibrowane do PD. Konwencja kolorów (+/−) nadal działa.

### SHAP scoring-time only (decyzja CREDIT-211)
SHAP **nie jest persistowany w bazie** — liczony świeżo przy każdym scoringu i zwracany w response `POST /clients/{ref}/snapshots`. Endpoint `GET /history` nie zawiera SHAP. Powód: historical SHAP jest mało wartościowy (interpretacja decyzji ma sens w momencie scoringu), a persistence kosztowne (5 modeli × top-5 × każda migawka).

---

## J. Fairness i audyt dyskryminacji

### Fairness (definicja)
**Brak systematycznego biasu modelu** względem atrybutu chronionego (np. SEX). Nie istnieje jedna „prawdziwa" definicja — różne miary (DPD, EOD, predictive parity) **nie mogą być spełnione jednocześnie** (twierdzenie Chouldechovej 2017). Wybór miary jest decyzją normatywną.

### fairlearn
Microsoftowa biblioteka Python do mierzenia i mitygacji fairness. **W projekcie:** `>=0.10`, używana w `fairness_audit.py` (CREDIT-112).

### DPD (Demographic Parity Difference)
**Różnica selection rate między grupami chronionymi:**
`DPD = |P[ŷ=1 | SEX=1] − P[ŷ=1 | SEX=2]|`
Mierzy, czy obie grupy są flagowane równie często. **Próg ostrzegawczy:** 0.10 (konsensus). **Słabość:** ignoruje base rate (jeśli jedna grupa faktycznie defaultuje częściej, model powinien ją flagować częściej).

### EOD (Equalized Odds Difference)
**Max różnicy TPR i FPR między grupami:**
`EOD = max(|ΔTPR|, |ΔFPR|)`
Mierzy, czy model jest *równie dobry* dla obu grup. Bardziej rygorystyczna niż DPD, bo uwzględnia label.

### Selection rate
Procent klientów w grupie zaalarmowanych przez model: `P[ŷ=1 | grupa]`. Pierwszy element rachunku DPD.

### TPR (True Positive Rate / sensitivity / recall)
Procent faktycznych defaulterów w grupie, których model złapał. Pierwszy człon EOD.

### FPR (False Positive Rate / 1 − specificity)
Procent faktycznych non-defaulterów w grupie błędnie zaalarmowanych. Drugi człon EOD.

### Disparate impact
Sytuacja, gdy model produkuje **systematycznie różne wyniki dla grup chronionych** mimo braku jawnego użycia atrybutu. Mierzona DPD, EOD lub *disparate impact ratio* (P[ŷ=1|A=0] / P[ŷ=1|A=1]). **W projekcie nie zmaterializowany** — wszystkie 5 modeli |DPD| ≤ 0.04.

### Base rate (prior)
Faktyczna częstość pozytywnej klasy w grupie. **W UCI:** SEX=1 (mężczyźni) — base rate defaultów 24.2%, SEX=2 (kobiety) 20.8%. **Konsekwencja:** model trafnie odzwierciedlający strukturę danych będzie miał dodatnie DPD — to **nie czysty bias**, lecz odbicie rzeczywistości.

### Audit przy cost-opt thresholds (kluczowa decyzja CREDIT-112)
**Audyt fairness liczony przy progach faktycznie używanych w produkcji**, nie przy arbitralnym 0.5. **W projekcie:** binaryzacja przy progach z `alert_thresholds.json` (0.130-0.180). Defensible: mierzymy fairness **realnego zachowania systemu**, nie hipotetycznego.

### Mitigation (mityacja)
Techniki redukcji DPD/EOD po treningu: **ExponentiatedGradient** (reweighting), **ThresholdOptimizer** (per-group threshold tuning), pre-processing reweighting. **W projekcie nie potrzebne** — wszystkie modele zdają. Mitigation jako kandydat na appendix CREDIT-114.

---

## K. Architektura systemu (REST + persystencja)

### REST API
Architektura HTTP-based: zasoby pod URL, operacje przez metody (GET, POST, etc.). **W projekcie:** wszystkie endpointy backendu i Flaska są REST, JSON request/response, wersjonowanie przez `/api/v1/`.

### Stateless service (Flask)
Usługa **bez stanu** między requestami — każdy request niezależny, brak bazy, brak sesji. **W projekcie:** Flask `/predict/timeseries` jest świadomie bezstanowy; orkiestrację i persystencję robi .NET. Skutek: Flask można skalować horyzontalnie bez koordynacji.

### Orchestrator pattern (.NET)
Backend .NET jako **warstwa pośrednia**: waliduje wejście, woła Flask, wzbogaca response (data, labelki), zapisuje do DB, tłumaczy błędy. Klient (React) widzi tylko backend, nie Flaska.

### camelCase vs snake_case
Konwencja JSON: React/JS używa **camelCase** (`limitBal`, `payAmt1`), Python/Flask **snake_case** (`limit_bal`, `pay_amt1`). Backend .NET tłumaczy między nimi (`PredictRequest.cs` ↔ `FlaskPredictRequest.cs`).

### ErrorEnvelope
Wspólny format błędów backendu z kontraktu CREDIT-210:
```json
{ "code": "VALIDATION_FAILED", "message": "age must be 18..100", "details": {...} }
```
Kody: `VALIDATION_FAILED` (400), `ML_SERVICE_ERROR` (502), `ML_SERVICE_UNAVAILABLE` (503), `CONFLICT` (409), `CLIENT_NOT_FOUND` (404), `INTERNAL_ERROR` (500).

### 409 Conflict (idempotency)
HTTP status zwracany przy próbie zapisu duplikatu `(clientRef, snapshotDate)`. **Decyzja projektu (CREDIT-203):** 409 zamiast cichego upsertu — chroni przed przypadkowym podwójnym zapisem tej samej daty.

### Auto-migracje EF Core
`db.Database.Migrate()` w `Program.cs` — przy starcie backendu sprawdza i aplikuje pending migracje schematu. **W projekcie:** włączone (CREDIT-402) → `docker-compose up` stawia bazę i automatycznie tworzy/aktualizuje schemat.

### DataAnnotations
Atrybuty .NET deklarujące walidację: `[Range(18, 100)]`, `[Required]`, `[StringLength(64)]`. **W projekcie:** stosowane w `Snapshot22Features.cs` — automatyczna walidacja przez ASP.NET, błędy mapowane do `ErrorEnvelope.ValidationFailed`.

### WebApplicationFactory
Klasa .NET do testów integracyjnych — odpala in-memory hostowany serwer ASP.NET z prawdziwym pipeline'em DI. **W projekcie:** wszystkie testy backendu (28 testów) używają jej + stub `HttpMessageHandler` zamiast realnego Flaska.

### Testcontainers
Biblioteka uruchamiająca prawdziwy kontener Docker (np. `postgres:16-alpine`) na czas testu. **W projekcie (CREDIT-205):** 8 testów persystencji na realnym Postgresie, jeden kontener per klasa testów, `TRUNCATE ... RESTART IDENTITY CASCADE` między testami. Wyłapuje to, czego EF InMemory nie sprawdza: constrainty, kaskady FK, defaulty serwera.

---

## L. Stack technologiczny

### React 19 + TypeScript + Vite
**Frontend, port 5173.** React 19 (najnowszy), TypeScript dla type safety, Vite jako bundler i dev server (hot reload). **W projekcie:** komponenty `InputForm`, `TimelineChart`, `TrendAlerts`, `ClientList`, `ClientHistory`, `SnapshotForm`, `ShapExplanation`.

### .NET 8 ASP.NET Core
**Backend, port 5120.** Microsoft LTS, framework do REST API. **W projekcie:** `WebApi/`, kontrolery `MonitoringController` + `PredictController`, EF Core dla DB.

### EF Core + Npgsql
**ORM dla .NET + driver PostgreSQL.** Pozwala mapować klasy C# na tabele DB, automatyczne migracje schemy. **W projekcie:** `AppDbContext`, encje `Client/Snapshot/Prediction/Trend`.

### PostgreSQL 16
**Relacyjna baza danych, port 5432.** Wybrana dla solidnej obsługi `timestamptz` (dat z timezone), wsparcia dla EF Core przez Npgsql, dojrzałości. **W projekcie:** persystencja migawek + predykcji + trendów, uruchamiana w Dockerze.

### Flask 3 + Python 3.11
**ML service, port 5001.** Flask jako lekki framework REST, Python 3.11 dla najnowszych bibliotek ML. **W projekcie:** `ml-service/app.py`, ładuje 5 modeli + 5 kalibratorów + scalers + SHAP TreeExplainery przy starcie.

### TensorFlow / Keras
Framework do sieci neuronowych Google. **W projekcie:** używany do LSTM (`lstm_model_w3.keras`). Keras to wysokopoziomowe API TF.

### scikit-learn
Biblioteka klasycznych modeli ML i utilities Pythonowych. **W projekcie:** Random Forest, IsotonicRegression, CalibratedClassifierCV, StandardScaler, StratifiedKFold, train_test_split, metrics.

### XGBoost, LightGBM, CatBoost
**Trzy biblioteki gradient boosting.** Każda jest standalone (osobny pakiet Python z natywną implementacją C++). **W projekcie:** XGB od początku (CREDIT-102), LightGBM + CatBoost od CREDIT-109.

### SHAP, Fairlearn, Optuna
- **SHAP** — `shap.TreeExplainer` (CREDIT-107).
- **Fairlearn** — `demographic_parity_difference`, `equalized_odds_difference`, `MetricFrame` (CREDIT-112).
- **Optuna** — Bayesian hyperparameter tuning z TPESampler (CREDIT-108).

### Recharts
Biblioteka React do wykresów (oparta na D3). **W projekcie:** `TimelineChart.tsx` (LineChart 5 linii trajektorii), `ComparisonChart.tsx` (BarChart porównanie modeli).

### Vitest / xUnit / pytest / Testcontainers
**Stack testowy.**
- **Vitest** (frontend) — szybki test runner kompatybilny z Jest API.
- **xUnit** (.NET) — standard test framework Microsoftu.
- **pytest** (Python) — najbardziej popularny test framework Pythonowy.
- **Testcontainers** — prawdziwy Postgres w Dockerze do testów integracyjnych (zob. K).

### docker-compose
**Orkiestracja wielu kontenerów.** `docker-compose.yml` w rootcie definiuje `db` + `backend` + `ml-service` (frontend POZA compose — uruchamiany lokalnie przez `npm run dev` dla wygody hot-reloadu).

---

## M. Metodologia pracy zespołowej

### GitHub Flow
Schemat branchingu: `main` zawsze zielony; każda zmiana przez **feature branch** + Pull Request + code review + zielone CI. **W projekcie:** branche `sprintN/krótka-nazwa`, np. `sprint5/fairness`. Merge tylko przez PR.

### Sprint (2 tygodnie)
**Iteracja czasowa Scruma.** W projekcie 6 sprintów × 2 tygodnie kalendarzowe (2 cze 2026 → 24 sie 2026), plus bufor pisarski wrzesień.

### CREDIT-XXX (task ID)
Unikalny identyfikator zadania (np. CREDIT-101). 30 zadań w backlogu (`TASKS.md`), 26 zamkniętych do 2026-06-06.

### Definition of Done (DoD)
**Lista warunków, które zadanie musi spełnić, żeby zostać uznane za zamknięte.** Zwykle: kod + testy + zaktualizowana dokumentacja przy zmianach kontraktu. **W TASKS.md** każde CREDIT-XXX ma własne DoD.

### Priorytety P0 / P1 / P2
- **P0** — must-have, blokuje obronę tezy.
- **P1** — should-have, znacząco wpływa na wynik.
- **P2** — nice-to-have, polish.

W projekcie ścieżka krytyczna tezy (`101 → 102 → 104 → 110 → 111 → 114`) jest cała P0.

### SWAP-OK
Tag oznaczający zadania **łatwe do zamiany właścicielem** (GF ↔ MK). Sygnalizuje, że task nie wymaga specyficznej wiedzy tylko jednej osoby. Przykład: `CREDIT-106 cost thresholds` jest SWAP-OK.

### Ścieżka krytyczna (oś tezy)
Sekwencja zadań, których opóźnienie przesuwa dowód tezy. **W projekcie:** `101 → 102 → 104 → 110 → 111 → 114`. Stan na 2026-06-06: 5/6 ogniw zamkniętych, zostaje CREDIT-114 (czeka na CREDIT-113).

### Risk register
Lista zidentyfikowanych ryzyk projektu z prawdopodobieństwem, wpływem i mitygacją. **W projekcie 5 ryzyk** (R1-R5) — np. R2 „monitoring nie bije statyki w eksperymencie" → mitygacja: framing „dynamika daje lead time, nawet jeśli AUC podobne".

### CI/CD (Continuous Integration)
**Automatyczne uruchamianie testów przy każdym PR.** W projekcie GitHub Actions (`.github/workflows/ci.yml`) — 3 joby równolegle (xUnit backend, pytest ML, Vitest frontend). Czerwone CI blokuje merge. Wall-clock ~70s.

### Smoke test
**Najprostszy test** sprawdzający, czy podstawowy use case działa (np. czy serwis się uruchamia). Wprowadzony w CREDIT-201 — po jednym smoke teście per stack jako fundament infrastrukturalny.

### Audit-trail tasks (CREDIT-115, CREDIT-116)
Zadania utworzone post-factum dla **transparentności historii** — kiedy gap wykryty był poza scope'em pierwotnego zadania (CREDIT-109), ale wykonanie chronologicznie dopisuje się do oryginału. Honest framing: „powinno być w scope'ie CREDIT-109, nie było — dlatego osobne zadania dla audit trail".

### Pivot (CREDIT-109 out-of-order)
Świadoma zmiana kolejności zadań pod ścieżkę krytyczną. **W projekcie:** CREDIT-109 (Sprint 5 P2) wzięty w Sprincie 4 out-of-order, żeby odblokować łańcuch `109 → 113 → 114`. Defensible decyzja P0-driven, udokumentowana w `PodsumowanieSprintu4_GF.md` §1.

---

## N. Pojęcia specyficzne dla tej pracy

### „Dynamiczne" — dwoiste znaczenie
**Termin z tytułu pracy** ma w v8 PDF **dwa poziomy**:
1. **Dynamiczna architektura modelu** — LSTM jako sieć rekurencyjna (sekwencyjna).
2. **Dynamiczna ocena (Wariant B)** — monitoring kalendarzowy, trajektoria PD w czasie.

**Drugie znaczenie jest istotniejsze** dla tezy. Pierwsza prezentacja seminarium 2 explicit wprowadza tę dwoistość — to **kluczowy talking point obrony**.

### Wariant B (vs Wariant A)
**Wariant B** = monitoring kalendarzowy (trajektoria PD, wiele migawek). **Wariant A** = ocena statyczna (jedno PD na klienta). Praca realizuje Wariant B; Wariant A jest **baselinem** porównawczym w eksperymencie CREDIT-111.

### THE thesis slide
Slajd 8 prezentacji seminarium — eksperyment **statyka vs monitoring** (CREDIT-111). To **jedyny slajd, który rozstrzyga tezę liczbowo**. Musi zawierać honest verdict (zob. niżej), nie tylko liczby wzrostu lead time.

### Honest verdict
**Świadomy framing pracy** zapobiegający nadinterpretacji: *„Monitoring nie wygrywa czystej catch rate przy FA=10% — traci 1-8 pp. Wygrywa lead time (~2 okna) i 36-72 unikalnych catchy/model. Bilans korzyści jest funkcją modelu kosztów."* Powtarzane w speaker notes slajdów 8, 13. Antywzorzec: „monitoring strictly dominuje" — to byłoby kłamstwo.

### Operating point
**Konkretny próg używany w produkcji.** W projekcie: cost-optymalne progi z `alert_thresholds.json`. Decyzje analityczne (fairness audit, walidacja kalibracji) liczone **przy operating point**, nie przy 0.5 — defensible i zgodne z realnym zachowaniem systemu.

### Live demo (V.1-V.5)
Sekcja `PrezentacjaSeminarium2.md` opisująca scenariusz prezentacji systemu na żywo: 3 terminale, pre-seed, scenariusz 5 kroków (8-12 min). Wszystko z backup planem.

### Pre-seed
Zasianie bazy danych demonstracyjnymi klientami **przed seminarium** przez `seed_demo_clients.py` — 3 klientów × 4 migawki dające trajektorie INCREASING_RISK / STABLE / DECREASING_RISK. Bezpieczniejsze niż „live empty-state add".

### 5-modelowy passthrough (CREDIT-115, CREDIT-116)
Wymóg, by **5 modeli zachowywało się jak rodzina end-to-end**: Flask → .NET DTO → frontend. Wcześniej (przed CREDIT-115) backend silently dropował LightGBM + CatBoost z response, mimo że Flask zwracał 5. Wykryte podczas demo prep, naprawione w 2 PR-ach.

### „Cascade redo"
Sytuacja, gdy zmiana w jednym module wymaga ponownego uruchomienia łańcucha zależnych modułów. **Przykład z CREDIT-108:** promocja tuned hyperparameters do produkcji wymagałaby re-run CREDIT-105 (kalibracja na nowych bazach) + CREDIT-106 (cost thresholds) + CREDIT-109 (raporty). Zbyt drogie dla < 0.5 pp uplift → tuned modele NIE promoted do produkcji.

### Stan pracy pisemnej (v3 → v8)
Aktualna wersja PDF pracy: **v8 (47 stron)**. Status: Wstęp + Roz. 1 + Roz. 2 + Bibliografia (31 pozycji) kompletne; **Roz. 3 (metodologia) i Roz. 5 (analiza wyników) puste** — czekają na CREDIT-114. Roz. 4 napisany, ale opisuje wczesną wersję projektu (3 modele, okno 6-mies., class_weight) — wymaga aktualizacji do v9. Szczegóły: `DokumentRoznice.md`, `WalidacjaPDFv7.md`.

### v8 vs projekt — kluczowe rozjazdy do zapamiętania
- **Modele:** PDF mówi 3 (RF/XGB/LSTM), projekt ma 5 (+ LightGBM + CatBoost).
- **Okno:** PDF opisuje 6-miesięczne, projekt używa 3-miesięcznych (W3).
- **Split:** PDF 70/30, projekt 80/20.
- **Imbalance:** PDF class_weight + SMOTE, projekt isotonic + cost thresholds.
- **LSTM:** PDF (6, 3), projekt (3, 3).
- **SHAP:** PDF tylko XGB, projekt 4 modele tree-based.
- **CV:** PDF schematyczne, projekt Optuna 5-fold (CREDIT-108).

Te rozjazdy są transparentne na seminarium — nie ukrywamy ich. Slajd 12 prezentacji o tym wprost.
