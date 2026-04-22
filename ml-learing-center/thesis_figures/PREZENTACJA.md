# Przewodnik prezentacyjny — jak czytać i omawiać wykresy

Dokument towarzyszący wykresom z `output/`. Dla każdej figury:
- **Co przedstawia** — jedno zdanie opisu
- **Jak czytać** — kluczowe elementy wizualne i ich znaczenie
- **Co powiedzieć** — 2–4 punkty do wygłoszenia w trakcie obrony

---

## Rozdział 1 — Kredyt i ocena zdolności kredytowej

### Rysunek 1.1 — Proces oceny zdolności kredytowej
**Co przedstawia:** Pięcioetapowy przepływ od wniosku klienta, przez analizę, scoring i decyzję, aż po monitoring spłat.

**Jak czytać:** Strzałki ciągłe = kolejne etapy chronologicznie. Strzałka przerywana wracająca do analizy = cykliczna aktualizacja danych klienta w trakcie trwania umowy.

**Co powiedzieć:**
- Ocena zdolności kredytowej to proces iteracyjny, nie jednorazowa decyzja.
- Najważniejszy etap z perspektywy ML to scoring (trzeci blok) — tu właśnie podstawiamy modele uczenia maszynowego.
- Decyzja kredytowa nie kończy procesu — monitoring ryzyka trwa przez cały okres spłaty i zasila dane wejściowe do ponownej oceny.

---

### Rysunek 1.2 — Rodzaje ryzyka kredytowego
**Co przedstawia:** Hierarchiczną klasyfikację czterech głównych typów ryzyka: niewypłacalności, opóźnień, sektorowego i makroekonomicznego.

**Jak czytać:** Kolor bloku = kategoria ryzyka, szara „karteczka" pod każdym = krótkie wyjaśnienie. Najważniejsze dla tej pracy są pierwsze dwa (czerwony i pomarańczowy) — bo to one są modelowane.

**Co powiedzieć:**
- Praca koncentruje się na ryzyku niewypłacalności i opóźnień — to, co bezpośrednio odpowiada zmiennej `Default` w zbiorze UCI.
- Ryzyko sektorowe i makroekonomiczne są poza zakresem modelu — wymagałyby danych makroekonomicznych, których zbiór UCI nie zawiera.
- Taki podział jest zgodny z Bazyleą III i nadzorem KNF.

---

### Rysunek 1.3 — Porównanie tradycyjnych metod oceny (heatmapa)
**Co przedstawia:** Ocenę 3 tradycyjnych metod (ekspercka, scoring punktowy, analiza finansowa) wg 4 kryteriów w skali 1–5.

**Jak czytać:** Zielony = mocna strona metody, czerwony = słaba. Wartość 5 = bardzo dobrze spełnia kryterium.

**Co powiedzieć:**
- Żadna klasyczna metoda nie dominuje we wszystkich kryteriach.
- Scoring punktowy wygrywa na szybkości i koszcie, ale nie jest najskuteczniejszy.
- Analiza finansowa jest najskuteczniejsza, ale wolna i droga.
- To uzasadnia szukanie alternatywy w ML — chcemy uzyskać jednoczesnie szybkość (5) i skuteczność (5).

---

### Rysunek 1.4 — Ograniczenia klasycznych metod scoringowych (radar)
**Co przedstawia:** Sześć ograniczeń klasycznego scoringu na wykresie radarowym — im dalej od środka, tym poważniejsze ograniczenie.

**Jak czytać:** Czerwone pole = obszar „bolączek" klasycznych metod. Im większa powierzchnia, tym więcej argumentów za ML.

**Co powiedzieć:**
- Trzy najpoważniejsze ograniczenia to: słaba skuteczność dla danych nieliniowych, brak uczenia się z nowych danych, niska adaptacyjność.
- Każde z nich jest adresowane przez jedną z metod ML użytych w pracy — XGBoost/RF modelują nieliniowości, modele można retrenować na nowych danych, LSTM uczy się wzorców czasowych.
- Ten wykres jest logicznym mostem między rozdziałem 1 a 2.

---

## Rozdział 2 — Uczenie maszynowe w finansach

### Rysunek 2.1 — Taksonomia uczenia maszynowego
**Co przedstawia:** Drzewo trzech głównych paradygmatów ML (nadzorowane, nienadzorowane, wzmacniane) z przykładami zastosowań finansowych.

**Jak czytać:** Czytaj od góry. Pod gałęzią „uczenie nadzorowane" są dwie podgałęzie (klasyfikacja / regresja) — credit scoring to klasyfikacja binarna.

**Co powiedzieć:**
- Praca opiera się wyłącznie na uczeniu nadzorowanym — konkretnie klasyfikacji binarnej (Default = 0 / 1).
- Uczenie nienadzorowane używane jest w finansach do AML i segmentacji klientów — wykracza poza zakres pracy.
- Takie umiejscowienie porządkuje słownik — w pracy używam tylko trzech algorytmów, ale każdy jest innej rodziny: RF (ensemble), XGBoost (boosting), LSTM (deep learning).

---

### Rysunek 2.2 — Pipeline uczenia maszynowego
**Co przedstawia:** Sześć etapów standardowego pipeline'u ML — od danych wejściowych do predykcji — oraz dwie pętle sprzężenia zwrotnego.

**Jak czytać:** Linia ciągła = flow główny. Czerwona przerywana (walidacja → trenowanie) = retrening po słabych wynikach walidacji. Zielona kropkowana (predykcja → preprocessing) = pętla produkcyjna z nowymi danymi.

**Co powiedzieć:**
- Ten schemat dokładnie odzwierciedla implementację w `main.py` — każdy etap ma odpowiednik w kodzie.
- Pętle zwrotne to coś, czego klasyczny scoring nie posiada — model ML można ciągle doskonalić.
- Rozdział 3 szczegółowo omawia preprocessing (rys. 3.4), rozdział 4 — trenowanie i walidację.

---

### Rysunek 2.3 — Zastosowania ML w finansach
**Co przedstawia:** Siedem obszarów zastosowań ML w sektorze finansowym z ich względną częstością wg przeglądu literatury.

**Jak czytać:** Dłuższy słupek = częstsze zastosowanie w publikacjach i praktyce. Credit scoring (95%) jest dominujący.

**Co powiedzieć:**
- Credit scoring jest najczęściej badanym zastosowaniem ML w finansach — to potwierdza, że praca wpisuje się w główny nurt badań.
- Wykrywanie fraudów (88%) i prognoza ryzyka (74%) są blisko związane metodologicznie — te same algorytmy można przenieść między tymi domenami.
- Sektor wciąż eksploruje ML — robo-doradztwo i compliance są na rozwoju.

---

### Rysunek 2.4 — Architektura modelu LSTM
**Co przedstawia:** Warstwy sieci neuronowej LSTM użytej w pracy: wejście 6×3 → LSTM(32) → Dropout → Dense(16) → sigmoid.

**Jak czytać:** Przepływ od góry. Etykiety na strzałkach = wymiary tensora. „6×3" oznacza 6 miesięcy historii × 3 cechy (PAY, BILL_AMT, PAY_AMT).

**Co powiedzieć:**
- Wejście 6×3 = każdy klient reprezentowany jako sekwencja 6 miesięcy danych o płatnościach.
- 32 jednostki LSTM to kompromis między mocą a ryzykiem przeuczenia (potwierdzony w rys. 4.4).
- Dropout 0.3 = regularyzacja — losowo wyłączam 30% neuronów w treningu.
- Sigmoid na wyjściu → wartość 0–1 interpretowana jako P(Default).

---

### Rysunek 2.5 — Random Forest (bagging + głosowanie)
**Co przedstawia:** Schemat działania Random Forest: dane wejściowe → N niezależnych drzew decyzyjnych → głosowanie większościowe → klasa wynikowa.

**Jak czytać:** Każde drzewo wytrenowane na innej bootstrapowej próbce danych. Linie łączące drzewa z głosowaniem = agregacja predykcji.

**Co powiedzieć:**
- Kluczowa idea: pojedyncze drzewo jest słabym klasyfikatorem, zespół 500 drzew redukuje wariancję i przeuczenie.
- Każde drzewo widzi inną próbkę + inny podzbiór cech — to wymusza różnorodność w zespole.
- W pracy używam 500 drzew (widać na rys. 4.5 że więcej nie daje wyraźnej poprawy).

---

### Rysunek 2.6 — XGBoost (gradient boosting)
**Co przedstawia:** Sekwencyjne dodawanie drzew, gdzie każde kolejne uczy się korygować błędy (residua) poprzedników.

**Jak czytać:** Strzałki ciągłe = flow trenowania sekwencyjnego. Strzałki przerywane (residua) = sygnał uczący dla kolejnego drzewa. Kropkowane do „Suma" = końcowa agregacja ważona.

**Co powiedzieć:**
- XGBoost różni się od Random Forest kierunkowo: RF to paraleliczny zespół niezależnych drzew, XGBoost to sekwencyjna korekta błędów.
- Każde kolejne drzewo „skupia się" na przypadkach, z którymi poprzednie modele miały problem.
- W pracy: 800 iteracji, learning_rate=0.02 — wolne uczenie z dużą liczbą drzew daje lepsze wyniki (rys. 4.7).

---

### Rysunek 2.7 — Porównanie algorytmów (teoretyczne, radar)
**Co przedstawia:** Ocenę teoretyczną 4 podejść (LSTM, RF, XGBoost, scoring) wg 6 kryteriów na radarze.

**Jak czytać:** Większa powierzchnia koloru = lepszy model „na papierze". Porównaj kształty — LSTM jest dobry w dokładności, ale słaby w interpretowalności.

**Co powiedzieć:**
- To jest ocena **teoretyczna** — wynika z własności algorytmów i literatury.
- Scoring tradycyjny wygrywa w interpretowalności, ale traci w dokładności.
- RF i XGBoost dają zbalansowany kompromis.
- Na rysunku 5.5 pokazuję ten sam radar z **empirycznymi** wynikami z moich modeli — porównanie teorii z praktyką.

---

## Rozdział 3 — Metodologia i projekt systemu

### Rysunek 3.1 — Rozkład zmiennej docelowej
**Co przedstawia:** Liczbę klientów spłacających (~23 tys.) vs. niespłacających (~6,6 tys.) w zbiorze UCI.

**Jak czytać:** Dwa słupki, zielony dominuje — klasa spłacająca stanowi ~78%.

**Co powiedzieć:**
- Zbiór jest **niezbalansowany** — to jedno z kluczowych wyzwań tej pracy.
- 22% niespłacających to stosunkowo dobry wskaźnik jak na zbiór kredytowy — bywają sytuacje z 2–3% klasy mniejszościowej.
- Niezbalansowanie oznacza, że accuracy jest mylącą metryką — zawsze patrzę na precision, recall, F1 i ROC-AUC (rys. 5.1).
- SMOTE (rys. 4.2) + class_weight w modelach to moje rozwiązania na tę nierównowagę.

---

### Rysunek 3.2 — Histogramy i boxploty kluczowych zmiennych
**Co przedstawia:** 4 zmienne (LIMIT_BAL, AGE, BILL_mean, late_count) pokazane w dwóch ujęciach: histogram (góra) i boxplot z podziałem na klasy (dół).

**Jak czytać:** W histogramach czerwony = niespłacający, zielony = spłacający. W boxplotach — porównaj medianę i zakres kwartyli między klasami. Im większa różnica, tym silniejszy predyktor.

**Co powiedzieć:**
- LIMIT_BAL: niespłacający mają niższe limity — banki już wcześniej postrzegają ich jako ryzykownych.
- AGE: rozkład podobny w obu klasach — wiek słabo dyskryminuje (niska istotność w rys. 4.6).
- late_count: największa różnica między klasami — oczywisty predyktor, potwierdzony też przez feature importance.
- Te wykresy uzasadniają inżynierię cech — surowe dane wymagają transformacji (np. late_count = zagregowana cecha z PAY_0..PAY_6).

---

### Rysunek 3.3 — Heatmapa korelacji
**Co przedstawia:** Trójkątna macierz korelacji Pearsona dla 16 zmiennych (15 cech + `Default`).

**Jak czytać:** Czerwony = korelacja dodatnia, niebieski = ujemna, biały = brak. Kolumna/wiersz `Default` pokazuje siłę liniowego związku każdej cechy z targetem.

**Co powiedzieć:**
- Silne bloki czerwone: grupa PAY_* (≈0.6–0.8), grupa BILL_AMT* (≈0.9) — miesiące są silnie skorelowane między sobą.
- `Default` jest najsilniej skorelowany z PAY_0 (≈0.32) i recent_pay_status — najnowsze opóźnienie to najsilniejszy predyktor liniowy.
- Korelacja Pearsona to tylko związki liniowe — drzewa i LSTM wyłapują też nieliniowości, które tu nie są widoczne.
- Wysoka korelacja BILL_AMT* uzasadniła utworzenie `BILL_mean` i `BILL_std` zamiast używania wszystkich 6 kolumn osobno.

---

### Rysunek 3.4 — Diagram preprocessingu
**Co przedstawia:** Siedmioetapowy pipeline przetwarzania danych: od surowego CSV, przez czyszczenie, imputację, feature engineering (wyróżnione), encoding, normalizację, aż po podział.

**Jak czytać:** Żółty blok (feature engineering) = najbardziej twórczy etap, gdzie ja dodaję wiedzę dziedzinową.

**Co powiedzieć:**
- Feature engineering to etap, który dodał najwięcej wartości — sam fillna i encoding to „higiena", ale utilization_rate czy BILL_trend to cechy wygenerowane z wiedzy o finansach.
- StandardScaler jest konieczny dla LSTM (inaczej gradient eksploduje/znika) i nieszkodliwy dla RF/XGBoost.
- Stratyfikowany split zachowuje proporcję klas 78/22 w train i test.

---

### Rysunek 3.5 — Architektura systemu eksperymentalnego
**Co przedstawia:** Czterowarstwowy stack: React frontend → C# backend → Flask ML-service (z 3 modelami) → dane UCI.

**Jak czytać:** Każda przerywana ramka = osobna warstwa architektoniczna. Trzy pliki pod ML-service = wytrenowane modele załadowane do pamięci przy starcie.

**Co powiedzieć:**
- Separacja odpowiedzialności: backend .NET zarządza API i walidacją, ml-service wykonuje inferencję.
- Taki podział pozwala skalować każdą warstwę niezależnie — np. uruchomić więcej instancji ml-service pod obciążeniem.
- Całość jest konteneryzowana (Docker) — wdrożenie wymaga tylko docker-compose up.

---

### Rysunek 3.6 — Przepływ danych (sequence diagram)
**Co przedstawia:** 8 kroków cyklu żądania predykcji — od wypełnienia formularza do prezentacji wyniku.

**Jak czytać:** Linie życia u góry = aktorzy systemu. Poziome strzałki = komunikaty (niebieskie = żądanie, czerwone przerywane = odpowiedź). Czytać z góry na dół.

**Co powiedzieć:**
- Kroki 4–5 to serce systemu: feature engineering + predykcja trzech modeli równolegle.
- Całość trwa zwykle 100–300 ms — wystarczająco szybko dla UX bankowej aplikacji.
- Każdy krok ma zdefiniowany scenariusz błędu (rys. 3.8).

---

### Rysunek 3.7 — Integracja AI z backendem
**Co przedstawia:** Wewnętrzną komunikację między warstwą .NET (PredictController + PredictionService + DTO) a warstwą Flask (app.py + preprocessing + modele).

**Jak czytać:** Przerywane ramki = granice technologiczne. Strzałka pomarańczowa z labelką HTTP = zewnętrzna komunikacja. Strzałka zielona = odpowiedź.

**Co powiedzieć:**
- Backend .NET nie zna żadnego detalu ML — po prostu przesyła JSON dalej. To pozwala wymienić modele lub dodać kolejne bez zmiany frontendu.
- DTO (PredictRequest, PredictResponse) to warstwa kontraktu — zmiana schematu API zmusza do updateu obu stron.

---

### Rysunek 3.8 — Scenariusze wyjątków
**Co przedstawia:** Drzewo decyzyjne 5 typów błędów: 400 (brak danych), 422 (zły format), 504 (timeout), 500 (schema), 503 (usługa offline).

**Jak czytać:** Romby (diamond) = punkty decyzyjne. Zielony blok = ścieżka sukcesu. Czerwone = każdy rodzaj błędu wraz z kodem HTTP.

**Co powiedzieć:**
- Każdy błąd ma dedykowany kod HTTP — zgodnie ze standardami REST.
- 504 to najbardziej podchwytliwy — model może nie odpowiedzieć w terminie przy wzroście ruchu.
- 500 ze schemą to ochrona przed silent failure, gdy retrenuję model z inną liczbą cech.

---

### Rysunek 3.9 — Stos technologiczny
**Co przedstawia:** Macierz warstw × technologie — 6 warstw architektonicznych z konkretnymi narzędziami.

**Jak czytać:** Wiersz = warstwa, kolumna = konkretna technologia w ramach tej warstwy.

**Co powiedzieć:**
- Stack jest świadomie heterogeniczny: .NET do API (stabilność, szybkość), Python do ML (ekosystem), React do UI (DX).
- Docker unifikuje deployment — wszystkie komponenty w kontenerach.
- Wybór TensorFlow dla LSTM i sklearn dla RF to standard branżowy — łatwo znaleźć pomoc i dokumentację.

---

## Rozdział 4 — Implementacja i trenowanie modeli

### Rysunek 4.1 — Podział danych train / val / test
**Co przedstawia:** Podział 30 000 rekordów na 56% trenowanie, 14% walidacja, 30% test — dwa ujęcia: donut + pasek liniowy.

**Jak czytać:** Pasek u góry pokazuje proporcje w bezwzględnej skali. test_size=0.3 (podstawowe cięcie), potem validation_split=0.2 w samym treningu LSTM.

**Co powiedzieć:**
- Test set (30%) jest „zamrożony" — model go nie widzi, używam dopiero na końcu do raportu metryk.
- Walidacja (14%) służy do EarlyStopping i wyboru hiperparametrów — nie wolno jej używać do finalnej oceny.
- Stratyfikacja zapewnia, że w każdym splicie jest ~22% klasy mniejszościowej.

---

### Rysunek 4.2 — SMOTE przed i po
**Co przedstawia:** Górny wiersz: słupki klas przed i po SMOTE. Dolny wiersz: rzut 2D-PCA — rozkład klas w przestrzeni zmiennych.

**Jak czytać:** Po SMOTE liczebność klas jest wyrównana (każda = ok. 16 tys.). Na scatter po SMOTE punkty czerwone „zagęszczają się" — są to syntetyczne przykłady wygenerowane interpolacją.

**Co powiedzieć:**
- SMOTE tworzy syntetyczne przykłady klasy mniejszościowej metodą interpolacji liniowej między sąsiadami.
- Na rzucie PCA widać, że nowe punkty leżą w tych samych obszarach co oryginały — SMOTE nie wprowadza obcej struktury.
- W finalnej implementacji używam alternatywy: class_weight="balanced" + scale_pos_weight w XGBoost. Oba mają tę samą intencję, ale class_weight nie zmienia danych, więc jest bezpieczniejszy.

---

### Rysunek 4.3 — Krzywe uczenia LSTM
**Co przedstawia:** Dwa panele — accuracy (lewo) i loss (prawo) w funkcji epoki, dla zbioru treningowego i walidacyjnego.

**Jak czytać:** Jeśli krzywe train i val rozjeżdżają się (train rośnie, val spada) → przeuczenie. Jeśli obie rosną równolegle → zdrowe uczenie. Moment, w którym val przestaje się poprawiać, to aktywacja EarlyStopping.

**Co powiedzieć:**
- Accuracy rośnie przez kilka pierwszych epok, potem plateau — model szybko się uczy podstawowej struktury.
- Loss walidacyjny spada monotonicznie, brak przeuczenia — zasługa Dropout + EarlyStopping.
- Nie używam pełnych 40 epok — EarlyStopping najczęściej kończy trening wcześniej.

---

### Rysunek 4.4 — Wpływ hiperparametrów LSTM
**Co przedstawia:** Trzy panele — AUC walidacyjne w funkcji liczby epok, batch size, liczby jednostek LSTM. Czerwone okręgi = maksimum na każdym panelu.

**Jak czytać:** Szukam „kolanka" krzywej — punktu, po którym dodawanie zasobów nie daje już poprawy.

**Co powiedzieć:**
- Liczba epok: po ~15 AUC już się stabilizuje — więcej epok nie pomaga (a grozi przeuczeniem).
- Batch size: zbyt mały (64) jest wolny i szumny, 256–512 to sweet spot.
- Liczba jednostek: 32 to optimum — mniejsze niedouczają, większe przeuczają.
- Te wykresy uzasadniają moje wybory hiperparametrów w main.py.

---

### Rysunek 4.5 — Hiperparametry Random Forest
**Co przedstawia:** Heatmapa AUC testowego dla siatki n_estimators × max_depth. Czerwone obramowanie = optymalna konfiguracja.

**Jak czytać:** Jasno-żółte komórki = wysokie AUC. Przechodząc z góry na dół (rosnąca głębokość) AUC rośnie do pewnego punktu. Przechodząc w prawo (więcej drzew) — zysk maleje asymptotycznie.

**Co powiedzieć:**
- Zbyt płytkie drzewa (max_depth=4) niedouczają — AUC niski w górnym wierszu.
- Zbyt głębokie drzewa (None = bez ograniczenia) zaczynają przeuczać — dlatego wybrałem max_depth=10 jako kompromis.
- 500 drzew jest bezpieczne — dalsze zwiększanie daje marginalny zysk przy kwadratowym koszcie treningu.

---

### Rysunek 4.6 — Feature importance Random Forest
**Co przedstawia:** Top 20 cech wg Gini importance z wytrenowanego modelu — od najważniejszej (góra) do najmniej ważnej (dół).

**Jak czytać:** Im dłuższy słupek, tym większy wpływ cechy na decyzje drzew. Liczby na słupkach to wartość istotności (suma po wszystkich drzewach).

**Co powiedzieć:**
- TOP 3: PAY_0 / recent_pay_status / late_count — wszystkie dotyczą najnowszego zachowania płatniczego.
- Cechy inżynierowane (late_count, severe_late, utilization_rate) są wśród najważniejszych — to potwierdza wartość dodaną feature engineering.
- Zmienne demograficzne (AGE, SEX, EDUCATION, MARRIAGE) są na dole — w tym zbiorze zachowanie płatnicze liczy się znacznie bardziej niż profil demograficzny.

---

### Rysunek 4.7 — Grid Search XGBoost
**Co przedstawia:** Heatmapa AUC testowego dla kombinacji learning_rate × max_depth. Zielone obramowanie = optymalna konfiguracja.

**Jak czytać:** Patrzę na najjaśniejszy obszar — to sweet spot hiperparametrów. Zbyt wysokie lr (0.1) przy dużej głębokości = szybkie przeuczenie.

**Co powiedzieć:**
- XGBoost preferuje niskie learning_rate (0.01–0.02) i płytkie drzewa (max_depth=3–4) — zgodnie z zaleceniami twórców.
- Kompensuję niskie lr dużą liczbą iteracji (800) — to klasyczny kompromis: wolne uczenie, duża liczba kroków.
- Taki wybór daje też lepszą regularyzację niż agresywny boost.

---

### Rysunek 4.8 — Wartości SHAP dla XGBoost
**Co przedstawia:** Lewo — beeswarm plot (każda kropka = jedna próbka, pozycja na osi X = wpływ cechy na predykcję). Prawo — bar plot średniej |SHAP|.

**Jak czytać:**
- **Beeswarm:** czerwone kropki = wysoka wartość cechy, niebieskie = niska. Pozycja prawa = zwiększa P(Default), lewa = zmniejsza.
- **Bar:** globalna istotność cechy (uśredniona wartość bezwzględna SHAP).

**Co powiedzieć:**
- SHAP to „złoty standard" wyjaśnialności — pochodzi z teorii gier Shapleya.
- PAY_0 ma najsilniejszy wpływ: wysokie opóźnienie (kropka czerwona, prawa strona) zawsze zwiększa P(Default).
- SHAP pozwala wyjaśnić każdą pojedynczą predykcję klientowi: „nie dostał pan kredytu, bo PAY_0 wzmacnia ryzyko o +0.3".
- To argument za XGBoost w regulowanej bankowości: AI Act i GDPR wymagają wyjaśnialności.

---

### Rysunek 4.9 — Walidacja krzyżowa 5-fold
**Co przedstawia:** Schemat ilustracyjny 5-fold cross-validation — w każdej z 5 iteracji inny fold pełni rolę walidacji.

**Jak czytać:** Rząd = iteracja. Kolumna = fold. Czerwony = walidacja w danej iteracji, niebieski = trenowanie.

**Co powiedzieć:**
- CV pozwala oszacować wariancję modelu — jeden split to jedna obserwacja, 5 splitów to 5 niezależnych ocen.
- Stratified CV zachowuje proporcję klas w każdym foldzie — kluczowe przy niezbalansowanych danych.
- W pracy używam prostego train/test split (rys. 4.1) zamiast CV — CV przy 500-drzewowym RF i 800-iteracyjnym XGB byłoby niepotrzebnie kosztowne. Ten schemat pokazuję jako standardową technikę referencyjną.

---

## Rozdział 5 — Analiza wyników i ocena modeli

### Rysunek 5.1 — Metryki modeli (bar + tabela)
**Co przedstawia:** Pięć metryk klasyfikacji (accuracy, precision, recall, F1, ROC-AUC) dla LSTM, RF i XGBoost — słupki + pełna tabela liczbowa.

**Jak czytać:** Każda trójka słupków to jedna metryka. Porównuję modele wzdłuż danej metryki. ROC-AUC jest najbardziej odporny na niezbalansowanie — dlatego to moja główna metryka.

**Co powiedzieć:**
- Accuracy jest myląca — nawet model zgadujący klasę większościową miałby 78%.
- Recall ważniejszy od precision w credit scoring — wolimy fałszywie zakwalifikować dobrego klienta jako ryzykownego (false positive) niż przeoczyć ryzykownego (false negative).
- F1 to harmonijny kompromis między precision i recall.
- XGBoost i LSTM typowo wygrywają w AUC — to właśnie wskazuje na lepszą zdolność dyskryminacji klas.

---

### Rysunek 5.2 — Krzywe ROC
**Co przedstawia:** Trzy krzywe ROC (jeden model = jedna krzywa) + linia diagonalna (klasyfikator losowy).

**Jak czytać:** Im bardziej krzywa wypychana w lewy górny róg, tym lepiej. Pole pod krzywą (AUC) = pojedyncza liczba mierząca ogólną jakość.

**Co powiedzieć:**
- Przykładowo: jeśli chcę recall=80%, czytam z osi Y, a na osi X zobaczę, jaki FPR to kosztuje — i porównuję między modelami.
- Linia diagonalna = klasyfikator losowy (AUC=0.5) — model sensowny musi ją pokonać.
- Krzywa ROC jest niezależna od progu klasyfikacji — pokazuje zdolność modelu w pełnym zakresie.

---

### Rysunek 5.3 — Macierze pomyłek
**Co przedstawia:** Trzy heatmapy 2×2 (jedna per model) — każda komórka pokazuje liczbę klientów + procent w ramach rzeczywistej klasy.

**Jak czytać:**
- **Lewy górny (TN):** prawidłowo zaklasyfikowani dobrzy klienci.
- **Prawy dolny (TP):** prawidłowo wykryci niespłacający — **najważniejsze**.
- **Prawy górny (FP):** „fałszywe alarmy" — dobrzy klienci sklasyfikowani jako ryzykowni.
- **Lewy dolny (FN):** przeoczeni niespłacający — **najgorszy błąd**.

**Co powiedzieć:**
- W bankowości FN (pominięty niespłacający) kosztuje utratę kapitału, FP kosztuje tylko utraconą marżę z niezawartej umowy.
- Dlatego optymalizuję recall dla klasy 1 (niespłacający) — widać to w procencie w prawym dolnym rogu.
- Normalizacja wierszami (procent w ramach prawdziwej klasy) pozwala porównywać modele mimo niezbalansowanych klas.

---

### Rysunek 5.4 — Porównanie modeli (4 kryteria)
**Co przedstawia:** Grupowe słupki trzech modeli × cztery kryteria (dokładność, interpretowalność, szybkość inferencji, stabilność) w skali 1–5.

**Jak czytać:** Stabilność = 5 − znormalizowane std AUC z 40 bootstrapów testu. Im mniejszy std (mniej różne wyniki na różnych próbkach), tym wyższa ocena.

**Co powiedzieć:**
- Ten wykres operacjonalizuje porównanie teoretyczne z rys. 2.7 — zastępuję wartości z literatury własnymi pomiarami.
- LSTM ma najmniejszą interpretowalność (ocena 1.5), ale konkurencyjną dokładność.
- XGBoost i RF dają zbalansowany profil — prawdopodobnie wybrałbym jeden z nich do produkcji.
- Pod wykresem jest notka z dokładnymi wartościami std AUC bootstrapu.

---

### Rysunek 5.5 — Radar empiryczny
**Co przedstawia:** Ten sam radar co rys. 2.7, ale z rzeczywistymi metrykami moich modeli (accuracy, precision, recall, F1, ROC-AUC).

**Jak czytać:** Porównaj z rysunkiem 2.7 — to była predykcja teoretyczna, ten wykres to empiryczny fakt.

**Co powiedzieć:**
- Dobra prezentacja ciągłości pracy: teoria (rys. 2.7) → wyniki eksperymentalne (rys. 5.5).
- Każdy model ma inny „kształt" — np. LSTM może mieć wysoki recall kosztem precision, XGBoost bardziej zbalansowany.
- Radar ułatwia wybór modelu do konkretnego scenariusza: „potrzebuję modelu o wysokim recall" → wybieram po kształcie.

---

### Rysunek 5.6 — ML vs scoring tradycyjny
**Co przedstawia:** Cztery modele (regresja logistyczna jako baseline scoringu + 3 modele ML) × 3 metryki.

**Jak czytać:** Regresja logistyczna reprezentuje klasyczny scoring punktowy — to moja „punkt odniesienia do pokonania".

**Co powiedzieć:**
- Regresja logistyczna to minimalny sensowny baseline — scoring bankowy najczęściej też opiera się na modelu liniowym.
- Każdy z trzech modeli ML przewyższa baseline w AUC i F1 — to jest liczbowa odpowiedź na pytanie „czy warto wdrażać ML?".
- Różnica AUC 0.02–0.05 wydaje się mała, ale przekłada się na miliony PLN przy dużych portfelach kredytowych.

---

### Rysunek 5.7 — Interpretowalność (heatmapa)
**Co przedstawia:** Heatmapa 5×3: pięć wymiarów interpretowalności (globalna, lokalna, feature importance, narzędzia SHAP/LIME, wizualizacja) × trzy modele.

**Jak czytać:** Im bardziej zielone, tym łatwiej wyjaśnić model. Pod wykresem suma punktów dla każdego modelu → ocena końcowa (niska/średnia/wysoka).

**Co powiedzieć:**
- LSTM jest najsłabszy w interpretowalności — sieci rekurencyjne są „czarną skrzynką".
- RF wygrywa w wizualizacji decyzji (można narysować pojedyncze drzewo), XGBoost — w integracji z SHAP.
- Ten wykres uzasadnia wybór XGBoost lub RF do rozmowy z klientem/regulatorem, mimo porównywalnej dokładności z LSTM.

---

### Rysunek 5.8 — Weryfikacja hipotez [PLACEHOLDER]
**Co przedstawia:** Tabela wizualna: hipoteza → wynik → status potwierdzenia (zielony = potwierdzona, pomarańczowy = częściowo, czerwony = odrzucona).

**Jak czytać:** Każdy wiersz to jedna hipoteza badawcza z pracy.

**Co powiedzieć:**
- ⚠ **Wypełnij przed prezentacją!** — wykres zawiera placeholdery, podmień je w kodzie na rzeczywiste hipotezy z rozdziału wstępnego pracy.
- Typowe hipotezy credit scoring to np. „modele ML osiągają wyższe AUC niż regresja logistyczna" (potwierdzona w rys. 5.6) lub „LSTM wykorzystujący dane sekwencyjne przewyższa modele statyczne".
- Status koloru = szybki przekaz dla komisji, czy praca osiągnęła zamierzone cele.

---

### Rysunek 5.9 — Wnioski i kierunki dalszych badań [PLACEHOLDER]
**Co przedstawia:** Mind mapa — praca magisterska w centrum, dwa gałęzie (wnioski / kierunki badań), listy punktów na końcach.

**Jak czytać:** Zielone bloki = osiągnięte rezultaty, czerwone = otwarte problemy.

**Co powiedzieć:**
- ⚠ **Wypełnij przed prezentacją!** — podmień listy CONCLUSIONS i FUTURE_WORK w generatorze.
- Typowe wnioski: „XGBoost osiąga najlepszy kompromis", „feature engineering ma istotny wpływ", „LSTM wnosi wartość przy danych sekwencyjnych".
- Typowe kierunki: dane behawioralne, modele transformerowe, wyjaśnialność dla regulatorów (AI Act), online learning.
- Ten wykres to ostatni slajd prezentacji — powinien pozostawić komisję z jasną listą „co zostało zrobione" i „co dalej".

---

## Ogólne wskazówki prezentacyjne

### Struktura narracji
1. **Motywacja** (rys. 1.1–1.4): dlaczego klasyczne metody nie wystarczają.
2. **Narzędzia** (rys. 2.1–2.7): jakie algorytmy ML mamy do dyspozycji.
3. **Dane i system** (rys. 3.1–3.9): na czym pracowałem, jak to wdrożyłem.
4. **Eksperyment** (rys. 4.1–4.9): jak trenowałem, jakie decyzje podejmowałem.
5. **Wyniki** (rys. 5.1–5.9): co uzyskałem, jaki jest wniosek.

### Top 5 wykresów do koniecznego wspomnienia
1. **Rys. 3.1** — rozkład klas (uzasadnienie metodyki)
2. **Rys. 4.8** — SHAP values (wyjaśnialność, mocny punkt dla komisji)
3. **Rys. 5.1** — metryki (główne liczby pracy)
4. **Rys. 5.2** — krzywe ROC (porównanie modeli w jednym obrazku)
5. **Rys. 5.6** — ML vs baseline (konkretny argument „po co to wszystko")

### Najczęstsze pytania komisji
- **„Dlaczego akurat te trzy modele?"** → reprezentują trzy różne rodziny: ensemble (RF), boosting (XGBoost), deep learning (LSTM). Rys. 2.1 uzasadnia.
- **„Co z niezbalansowaniem klas?"** → class_weight + scale_pos_weight, optymalizuję AUC i F1 (odporne na niezbalansowanie), rys. 3.1 i 4.2.
- **„Czy model będzie działał w praktyce?"** → pełny pipeline wdrożenia (rys. 3.5–3.7), Docker, API. SHAP zapewnia wyjaśnialność wymaganą prawnie.
- **„Co dalej?"** → rys. 5.9 (po wypełnieniu).
