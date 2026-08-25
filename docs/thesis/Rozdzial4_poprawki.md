# Rozdział 4 — poprawki istniejących sekcji + nowe sekcje 4.6 / 4.7 / 4.8

> **Draft do wklejenia (2026-07-07).** Część A: teksty zamienne do istniejących
> sekcji (co i czym zastąpić). Część B: pełna proza trzech nowych sekcji.
> Liczby zgodne z artefaktami po naprawach 2026-07-07.

---

## CZĘŚĆ A — poprawki istniejących sekcji

### A.1. Wstęp rozdziału 4 — zamiana „trzy klasyfikatory" na pięć

**Zastąpić** zdanie „W ramach pracy zaimplementowano trzy różne klasyfikatory…"
oraz dalszy opis trójki tekstem:

> W ramach pracy zaimplementowano pięć klasyfikatorów reprezentujących odmienne
> rodziny algorytmiczne: las losowy (zespół drzew z agregacją bagging), trzy
> warianty wzmacniania gradientowego — XGBoost, LightGBM i CatBoost — oraz sieć
> LSTM. Cztery pierwsze operują na statycznym, zagregowanym obrazie klienta
> i odpowiadają klasycznemu ujęciu scoringowemu. Piąty traktuje dane wejściowe
> jako szereg czasowy trzech kolejnych miesięcy historii płatniczej, modelując
> progresję zachowań. Dynamika w rozumieniu tytułu pracy realizowana jest jednak
> przede wszystkim na poziomie nadrzędnym — schematu oceny: każdy z pięciu
> modeli, niezależnie od architektury, stosowany jest do czterech przesuwanych
> okien W0..W3 (rozdz. 3.3.4), co daje trajektorię PD i umożliwia porównanie
> reguły statycznej z monitorującą w rozdziale 5.

*(Uwaga redakcyjna: usunąć z 4.2 sformułowanie o LSTM jako „głównym nośniku
dynamicznego ujęcia" — wiąże tezę z jednym modelem; dynamika = schemat oceny.)*

### A.2. Sekcja 4.1.1 — podział zbioru: 60/20/20 zamiast 70/30

**Zastąpić** opis podziału 70/30 (test 9 000; proporcje 56/14/30 oraz snippet
`test_size=0.3`) tekstem:

> Finalny protokół walidacji opiera się na trójdzielnym, stratyfikowanym
> podziale 60/20/20 (`random_state = 42`): 18 000 obserwacji treningowych,
> 6 000 kalibracyjnych i 6 000 testowych. Wydzielenie osobnej części
> kalibracyjnej jest konieczne, ponieważ kalibrator izotoniczny (sekcja 4.6)
> nie może być dopasowywany na danych, które widział model bazowy — w
> przeciwnym razie korekta prawdopodobieństw odtwarzałaby przeuczenie zamiast
> je korygować. Na tej samej części kalibracyjnej wyznaczane są progi alertu
> (sekcja 4.7). Zbiór testowy pozostaje w pełni zamrożony: nie uczestniczy
> w treningu, doborze hiperparametrów, kalibracji ani doborze progów.
> Konsekwentnie, standaryzacja cech dopasowywana jest wyłącznie na części
> treningowej — dopasowanie skalera na pełnym zbiorze, choć liczbowo pomijalne
> przy 30 000 obserwacji, naruszałoby deklarację zamrożenia testu (weryfikację
> empiryczną znikomości tego efektu zawiera repozytorium,
> `reports/scaler_leakage_fix.md`).

Podział 70/30 z pierwotnego pipeline'u można pozostawić wyłącznie jako wzmiankę
historyczną (baseline 6-miesięczny). **Rysunek 4.1 wymaga regeneracji** pod
proporcje 60/20/20.

### A.3. Sekcja 4.1.2 — niezbalansowanie klas: dopisać tandem z kalibracją

Opis `class_weight="balanced"` / `scale_pos_weight` **pozostaje** (finalne
modele faktycznie ich używają). **Dopisać na końcu sekcji:**

> Ważenie klas poprawia ranking obserwacji, lecz celowo zniekształca skalę
> prawdopodobieństw — model „podbija" klasę mniejszościową, przez co surowe
> wyjścia nie odpowiadają częstościom empirycznym. W klasycznym scoringu
> progowym bywa to akceptowalne; w schemacie monitoringu trajektorii jest
> dyskwalifikujące, bo porównywanie PD między oknami wymaga skali absolutnej.
> Deformację tę koryguje kalibracja izotoniczna opisana w sekcji 4.6 —
> ważenie klas i kalibracja pełnią więc role komplementarne: pierwsze dba
> o jakość rankingu, druga o interpretowalność liczbową wyników.

### A.4. Sekcja 4.2.1 — LSTM: dwie wersje wejścia

**Zastąpić** bezwarunkowy opis wejścia (6, 3) tekstem:

> Sieć zaimplementowano w dwóch wariantach wejścia. Wariant bazowy,
> 6-miesięczny, przyjmuje tensor (6, 3) — sześć kroków czasowych po trzy cechy
> (status płatności, saldo, wpłata) — i służy jako punkt odniesienia dla
> hipotezy H1. Wariant finalny, zgodny ze schematem przesuwanego okna, operuje
> na tensorze (3, 3): trzech miesiącach okna uporządkowanych od najstarszego do
> najnowszego. Pozostałe elementy architektury (warstwa LSTM o 32 jednostkach,
> Dropout 0,3, Dense(16, ReLU), sigmoidalne wyjście) oraz procedura treningu
> (Adam, binary crossentropy, EarlyStopping i ReduceLROnPlateau na AUC
> walidacyjnym) są wspólne. Trening wariantu finalnego jest deterministyczny
> (ustalone ziarno losowe), a skalery kanałowe dopasowywane są wyłącznie na
> części treningowej i zapisywane do użycia w serwisie predykcyjnym.

Analogicznie w 4.3.2 i dalszych: cechy pochodne liczone są **na oknie
3-miesięcznym** (parametryzacja `engineer_features(df, window)`), nie na sześciu
miesiącach; opisy „w sześciomiesięcznym oknie" zamienić na „w oknie obserwacji".

### A.5. Sekcja 4.4.1 — strojenie: Optuna zamiast „CV schematycznie"

**Zastąpić** akapit o rezygnacji z walidacji krzyżowej („zaprezentowano
schematycznie…") tekstem:

> Hiperparametry przyjęte w implementacji wybrano heurystycznie na etapie
> prototypowania, a następnie zweryfikowano systematycznie: dla lasu losowego
> i XGBoost przeprowadzono strojenie Optuna (TPESampler, 30 prób na model)
> z pięciokrotną stratyfikowaną walidacją krzyżową na części treningowej.
> Najlepsze konfiguracje poprawiły AUC testowe o mniej niż 0,5 punktu
> procentowego względem przyjętych wartości, co świadczy o płaskości
> powierzchni hiperparametrów w otoczeniu wybranego punktu. Strojone warianty
> świadomie nie zostały wdrożone do systemu — zysk nie uzasadniał powtórzenia
> kaskady kalibracji i progów; pełny raport strojenia znajduje się
> w repozytorium (`reports/optuna_study.md`).

*(Heatmapy 4.5/4.7, jeśli pozostają, muszą prezentować CV-AUC na części
treningowej — nie AUC testowe; alternatywnie zastąpić je wykresem prób Optuny.)*

### A.6. Sekcja 4.5 — bootstrap: obietnica ma teraz pokrycie

**Zastąpić** zdanie o „raportowanej w rozdziale 5 wariancji AUC z 40
bootstrapowanych powtórzeń" (dotychczas bez pokrycia) tekstem:

> Stabilność oceny na pojedynczym podziale zweryfikowano bootstrapem: 40
> repróbkowań zbioru testowego ze zwracaniem, z których wyznaczono odchylenie
> standardowe i 95-procentowe przedziały ufności AUC każdego modelu oraz —
> w wariancie sparowanym — przedziały ufności różnic między modelami. Wyniki
> (rozdz. 5.3) pokazują, które różnice są rozróżnialne przy tej liczebności
> próby, a które należy raportować jako porównywalne.

---

## CZĘŚĆ B — nowe sekcje

### 4.6. Kalibracja prawdopodobieństw (regresja izotoniczna)

W schemacie monitoringu trajektorii kalibracja nie jest kosmetyką, lecz
warunkiem sensowności całej konstrukcji: wzrost PD z 0,30 do 0,45 między oknami
musi oznaczać rzeczywisty wzrost ryzyka, a nie artefakt skali konkretnego
modelu. Modele trenowane z ważeniem klas (sekcja 4.1.2) systematycznie
zawyżają surowe prawdopodobieństwa, dlatego każdy z pięciu klasyfikatorów
poddano kalibracji potreningowej na wydzielonej części kalibracyjnej
(rozdz. 3.3.5).

Wybrano regresję izotoniczną — nieparametryczną, monotoniczną korektę skali —
zamiast parametrycznej metody Platta, ponieważ nie narzuca ona sigmoidalnej
postaci rozjazdu między wynikiem modelu a częstością empiryczną, a przy 6 000
obserwacji kalibracyjnych ryzyko przeuczenia korekty jest niewielkie. Dla
czterech modeli drzewiastych zastosowano opakowanie
`CalibratedClassifierCV(FrozenEstimator(model), method="isotonic")` (estymator
bazowy zamrożony — kalibrator dopasowuje się wyłącznie na części
kalibracyjnej); dla LSTM — zewnętrzny obiekt `IsotonicRegression` aplikowany do
surowych wyjść sieci i serializowany obok modelu. Kalibracja poprawiła wynik
Briera o 19–25% (las losowy: 0,1689 → 0,1374; XGBoost: 0,1787 → 0,1360; LSTM:
0,1850 → 0,1385) przy praktycznie niezmienionym AUC — korekta monotoniczna nie
zmienia rankingu. Wykres kalibracji (reliability curve) po korekcie przebiega
blisko przekątnej [RYS: calibration_comparison_w3.png].

### 4.7. Progi alertu optymalne kosztowo

Domyślny próg klasyfikacyjny 0,5 jest w ocenie kredytowej arbitralny: koszt
przeoczenia przyszłego defaultu (utrata kapitału) wielokrotnie przewyższa koszt
fałszywego alarmu (koszt przeglądu, ewentualna utrata marży). Przyjęto model
kosztu FN = 5 × FP i dla każdego modelu wyznaczono próg minimalizujący koszt
oczekiwany, przeszukując zakres [0,1; 0,9] z krokiem 0,005 **na części
kalibracyjnej** — zbiór testowy nie uczestniczy w doborze progu, zgodnie
z zasadą z sekcji 4.1.1. (Świadomy kompromis: część kalibracyjna służy również
dopasowaniu kalibratora, więc prawdopodobieństwa są tam dla niego in-sample;
alternatywa — dobór progu na teście — naruszałaby zamrożenie testu, co
zweryfikowano wprost: `reports/threshold_leakage_fix.md`.)

Wyznaczone progi: las losowy 0,145; XGBoost 0,165; LightGBM 0,160; CatBoost
0,160; LSTM 0,155. Wszystkie leżą daleko poniżej 0,5 — bezpośrednie
odzwierciedlenie asymetrii kosztów: system woli częściej alarmować, niż
przeoczyć default. Progi są serializowane do pliku `alert_thresholds.json`
i serwowane przez API (pola `costThresholds` i `windowAlerts` odpowiedzi),
dzięki czemu warstwa decyzyjna systemu operuje na tych samych wartościach,
które audytowane są w rozdziale 5 (fairness liczony przy progach
produkcyjnych, nie przy umownym 0,5).

### 4.8. Implementacja LightGBM i CatBoost

Oba warianty wzmacniania gradientowego (teoria: sekcje 2.3.4 i 2.3.5) włączono
do eksperymentu w tym samym reżimie co las losowy i XGBoost: identyczny podział
danych, ta sama przestrzeń cech okna W3, ważenie klas
(`class_weight="balanced"` / `auto_class_weights="Balanced"`), kalibracja
izotoniczna na części kalibracyjnej i próg kosztowy z sekcji 4.7.
Hiperparametry ujednolicono z XGBoost dla porównywalności (800 iteracji,
learning rate 0,02, głębokość 4, subsampling 0,7); CatBoost używa
bootstrapu Bernoulliego i regularyzacji l2_leaf_reg = 3,0. Odpowiedź serwisu
predykcyjnego, DTO backendu oraz interfejs użytkownika zostały rozszerzone do
pełnej, pięciomodelowej postaci (trajektoria, trendy, progi i alerty per
model). Porównanie ilościowe całej piątki — wraz z przedziałami ufności
bootstrap — zawiera rozdział 5.3.
