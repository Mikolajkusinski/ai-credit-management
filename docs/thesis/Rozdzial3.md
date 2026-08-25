# Rozdział 3. Metodologia badań i projekt systemu

> **Draft do wklejenia do pracy (2026-07-07).** Liczby zweryfikowane z kanonicznymi
> artefaktami `ml-learing-center/reports/` po naprawach metodologicznych 2026-07-07.
> Miejsca na rysunki oznaczone `[RYS: ...]`. Nowe pozycje bibliografii oznaczone
> `[NOWE: ...]` — do dodania przy składzie.

## 3.1. Cel i zakres badań

Celem pracy jest zbadanie, czy i w jakim stopniu dynamiczne, kalendarzowe
monitorowanie ryzyka niewykonania zobowiązania przewyższa klasyczną, jednorazową
ocenę statyczną. Rozdziały 1 i 2 wykazały, że zarówno wymogi regulacyjne (art. 70
Prawa bankowego, wytyczne EBA dotyczące monitorowania kredytów [9]), jak i rozwój
metod uczenia maszynowego przesuwają akcent z pojedynczej decyzji kredytowej ku
ciągłej obserwacji ekspozycji. Część badawcza operacjonalizuje tę obserwację
w postaci schematu, w którym ta sama ekspozycja oceniana jest wielokrotnie na
przesuwanym oknie historii płatniczej, a wynikiem jest trajektoria
prawdopodobieństwa niewykonania zobowiązania (PD) zamiast pojedynczego wyniku.

Zakres badań obejmuje: (1) konstrukcję panelu danych z przesuwanym oknem na bazie
publicznego zbioru UCI „default of credit card clients" [13]; (2) trening
i kalibrację pięciu klasyfikatorów reprezentujących odmienne rodziny algorytmiczne
(las losowy, XGBoost, LightGBM, CatBoost — ujęcie statyczne; LSTM — ujęcie
sekwencyjne); (3) budowę kompletnego systemu eksperymentalnego (frontend, backend,
serwis predykcyjny, baza danych) realizującego monitoring trajektorii wraz
z progami alertu i wyjaśnieniami predykcji; (4) ewaluację porównawczą reguły
statycznej i monitorującej oraz audyt sprawiedliwości. Poza zakresem pozostają:
dane dochodowe (nieobecne w zbiorze — ograniczenie omówione we Wstępie), dane
alternatywne oraz zespoły typu stacking (świadoma decyzja zakresu; kierunek
dalszych badań).

## 3.2. Postawione hipotezy badawcze

Pytania badawcze sformułowane we Wstępie skonkretyzowano w postaci trzech
weryfikowalnych hipotez:

**H1 (zachowanie jakości przy krótszym oknie).** *Modele trenowane na
3-miesięcznym oknie obserwacji (W3) zachowują zdolność dyskryminacyjną modeli
6-miesięcznych: strata AUC nie przekracza 1 punktu procentowego.* Hipoteza
warunkuje wykonalność całego schematu monitoringu — okno 3-miesięczne jest ceną
za możliwość zbudowania czterech punktów trajektorii z dostępnych 6 miesięcy
historii.

**H2 (wartość monitoringu).** *Kalendarzowa reguła monitorująca — alert, gdy PD
w którymkolwiek z okien W0..W3 przekracza próg — oferuje wcześniejszą detekcję
pogarszającej się sytuacji dłużnika oraz wykrycia niedostępne regule statycznej
(opartej wyłącznie na najnowszym oknie W3), przy porównywalnej ogólnej zdolności
dyskryminacyjnej.* Hipoteza celowo nie postuluje wyższej czułości przy stałym
budżecie fałszywych alarmów: agregacja maksimum po czterech skorelowanych oknach
zwiększa ekspozycję na szum, a wartością monitoringu jest wyprzedzenie czasowe
i komplementarność, nie substytucja oceny statycznej.

**H3 (sprawiedliwość).** *Modele zachowują parytet względem atrybutu chronionego
SEX: różnica parytetu demograficznego (DPD) oraz różnica wyrównanych szans (EOD)
nie przekraczają 0,10 przy binaryzacji progami produkcyjnymi.* Wybór metryk
i progu omówiono w rozdziale 5.5; wymóg nawiązuje do klasyfikacji scoringu
kredytowego jako zastosowania wysokiego ryzyka w rozporządzeniu o sztucznej
inteligencji [25].

Weryfikację hipotez przedstawia rozdział 5.6.

## 3.3. Struktura i charakterystyka danych dłużników

### 3.3.1. Źródła i sposób pozyskania danych

Wykorzystano publiczny zbiór „default of credit card clients" (UCI Machine
Learning Repository), obejmujący 30 000 posiadaczy kart kredytowych tajwańskiego
banku [13]. Każdy rekord zawiera 23 zmienne objaśniające oraz binarną etykietę
niewykonania zobowiązania w październiku 2005 r. (22,1% obserwacji pozytywnych).
Zbiór jest standardowym benchmarkiem w literaturze credit scoringu, co umożliwia
odniesienie wyników do wcześniejszych badań [10], [13].

### 3.3.2. Opis zmiennych wejściowych i zmiennej docelowej

Zmienne dzielą się na trzy grupy: (1) profil klienta — limit kredytowy
(LIMIT_BAL), płeć (SEX: 1 = mężczyzna, 2 = kobieta), wykształcenie (EDUCATION),
stan cywilny (MARRIAGE), wiek (AGE); (2) historia płatnicza za sześć kolejnych
miesięcy (kwiecień–wrzesień 2005): statusy płatności PAY_*, salda rachunków
BILL_AMT1..6, kwoty wpłat PAY_AMT1..6; (3) zmienna docelowa Default. Istotną
cechą zbioru jest przesunięta numeracja: najnowszy miesiąc (wrzesień) opisują
kolumny PAY_0, BILL_AMT1 i PAY_AMT1, a kolumna PAY_1 nie istnieje. Mapowanie
kolumn na oś czasu przedstawia tabela 3.1.

**Tabela 3.1.** Mapowanie kolumn UCI na miesiące kalendarzowe.

| Miesiąc | Status płatności | Saldo rachunku | Kwota wpłaty |
|---|---|---|---|
| wrzesień (najnowszy) | PAY_0 | BILL_AMT1 | PAY_AMT1 |
| sierpień | PAY_2 | BILL_AMT2 | PAY_AMT2 |
| lipiec | PAY_3 | BILL_AMT3 | PAY_AMT3 |
| czerwiec | PAY_4 | BILL_AMT4 | PAY_AMT4 |
| maj | PAY_5 | BILL_AMT5 | PAY_AMT5 |
| kwiecień (najstarszy) | PAY_6 | BILL_AMT6 | PAY_AMT6 |

### 3.3.3. Preprocessing danych: czyszczenie, normalizacja, inżynieria cech

Dla modeli statycznych z każdego okna obserwacji wyliczane jest 13 cech
pochodnych (m.in. PAY_mean, PAY_max, BILL_mean, BILL_std, BILL_trend,
utilization_rate = BILL_mean / LIMIT_BAL, payment_ratio, late_count,
severe_late, recent_pay_status), uzupełnionych o 9 surowych kolumn okna oraz
zmienne demograficzne kodowane one-hot. Funkcja `engineer_features(df, window)`
jest sparametryzowana oknem — te same definicje cech obowiązują dla każdego
z okien W0..W3, a identyczna kopia modułu działa w treningu i w serwisie
inferencyjnym (spójność trening–serwing jest przypięta testami automatycznymi).
Kodowanie one-hot używa stałych dziedzin kategorii zbioru UCI, dzięki czemu
zestaw kolumn nie zależy od składu przetwarzanej próbki — w szczególności od
pojedynczego rekordu w inferencji. Wartości nieskończone i brakujące powstające
w cechach ilorazowych (np. przy LIMIT_BAL = 0) są zerowane identycznie po obu
stronach. Standaryzacja (StandardScaler) jest dopasowywana wyłącznie na części
treningowej i stosowana przez transformację do pozostałych podzbiorów oraz
w inferencji. Model sekwencyjny otrzymuje surowy tensor 3×3 (trzy miesiące ×
trzy kanały: PAY, BILL_AMT, PAY_AMT), skalowany per kanał skalerami
dopasowanymi na części treningowej — bez cech pochodnych i bez zmiennych
demograficznych.

### 3.3.4. Konstrukcja panelu z przesuwanym oknem (W0..W3)

Rdzeniem części badawczej jest przekształcenie przekrojowego zbioru UCI w panel
umożliwiający symulację monitoringu. Z sześciu miesięcy historii budowane są
cztery nakładające się okna 3-miesięczne, tworzące pseudo-oś czasu (tabela 3.2).

**Tabela 3.2.** Definicje okien przesuwnych.

| Okno | Zakres | Statusy | Salda | Wpłaty |
|---|---|---|---|---|
| W0 (najstarsze) | kwi–cze | PAY_6, PAY_5, PAY_4 | BILL_AMT6,5,4 | PAY_AMT6,5,4 |
| W1 | maj–lip | PAY_5, PAY_4, PAY_3 | BILL_AMT5,4,3 | PAY_AMT5,4,3 |
| W2 | cze–sie | PAY_4, PAY_3, PAY_2 | BILL_AMT4,3,2 | PAY_AMT4,3,2 |
| W3 (najnowsze) | lip–wrz | PAY_3, PAY_2, PAY_0 | BILL_AMT3,2,1 | PAY_AMT3,2,1 |

Obowiązuje zasada nadrzędna: **żadna wartość nie jest fabrykowana**. Każde okno
to rzeczywisty, trzymiesięczny wycinek historii klienta; jedyną operacją jest
wybór miesięcy „widocznych" w danym punkcie pseudo-czasu. Klient ma jedną
prawdziwą etykietę (default w październiku), wspólną dla wszystkich okien — nie
są tworzone żadne etykiety pośrednie.

Modele trenowane są wyłącznie na oknie W3, wyrównanym z etykietą („mając
ostatnie 3 miesiące, czy klient nie wykona zobowiązania w następnym
miesiącu?"). W inferencji ten sam model stosowany jest do każdego z okien
W0..W3 — ponieważ każde okno ma identyczną strukturę 3-miesięcznego wycinka,
rozkład wejść inferencyjnych odpowiada treningowemu. Trening na jednym oknie na
klienta eliminuje ryzyko wycieku etykiet, które niosłaby augmentacja wszystkimi
czterema oknami.

**Ograniczenie metodologiczne (istotne dla interpretacji wyników).** Zbiór UCI
jest przekrojowy, więc monitoring jest symulowany retrospektywnie: cztery okna
tego samego klienta nakładają się w dwóch trzecich, a wszystkie przewidują tę
samą październikową etykietę — okno W0 odpowiada predykcji z czteromiesięcznym
horyzontem, W3 z jednomiesięcznym. Trajektoria PD stanowi zatem przybliżenie
scenariusza produkcyjnego, a nie jego pełną replikę; walidacja na prawdziwym
panelu podłużnym pozostaje kierunkiem dalszych badań. Diagnozę odróżniającą
narastanie ryzyka od ewentualnego przesunięcia rozkładu między oknami
przedstawia rozdział 5.4.

### 3.3.5. Podział zbioru i protokół walidacji

Zastosowano trójdzielny, stratyfikowany podział 60/20/20 (`random_state = 42`):
18 000 obserwacji treningowych, 6 000 kalibracyjnych i 6 000 testowych. Część
kalibracyjna służy wyłącznie dopasowaniu kalibracji izotonicznej (rozdz. 4.6)
oraz wyznaczeniu progów alertu (rozdz. 4.7) — dzięki temu zbiór testowy
pozostaje zamrożony: nie uczestniczy w treningu, doborze hiperparametrów,
kalibracji ani doborze progów, a wchodzi do analizy wyłącznie w finalnej
ewaluacji rozdziału 5. Standaryzacja cech dopasowywana jest na części
treningowej (por. 3.3.3). Stratyfikacja zachowuje w każdym podzbiorze
proporcję klas 78/22.

[RYS: podział 60/20/20 — pierścień + pasek proporcji; do wygenerowania,
zastępuje dotychczasowy rysunek 4.1 z proporcjami 56/14/30]

## 3.4. Projekt architektury systemu eksperymentalnego

### 3.4.1. Architektura ogólna i przepływ danych

System składa się z czterech warstw komunikujących się przez HTTP/JSON
i uruchamianych w kontenerach (docker-compose; frontend w trybie deweloperskim
poza kompozycją):

```
React 19 + TypeScript (5173)
   │  POST/GET /api/v1/monitoring/*
   ▼
ASP.NET Core .NET 8 (5120) — MonitoringController → MonitoringService
   │  walidacja 22 cech, mapowanie nazw, labelki okien, obsługa błędów,
   │  persystencja (EF Core, transakcja atomowa)
   ├──► Flask (5001): POST /predict/timeseries — 5 modeli × 4 okna,
   │        trendy, progi kosztowe, SHAP top-5
   └──► PostgreSQL 16 (5432): Client / Snapshot / Prediction / Trend
```

[RYS: diagram architektury — opracowanie własne]

Przepływ oceny monitorującej: frontend przesyła 22 cechy klienta wraz z datą
migawki; backend waliduje żądanie, wywołuje serwis predykcyjny, wzbogaca
odpowiedź o etykiety kalendarzowe okien i — w ścieżce stanowej — zapisuje
migawkę, predykcje okna W3 oraz trendy w bazie. Kontrakt API (cztery endpointy,
typy, kody błędów) został sformalizowany przed implementacją w dokumencie
`docs/api-contracts/monitoring.md`, co umożliwiło równoległą pracę nad
backendem i frontendem przeciwko wspólnemu mockowi.

### 3.4.2. Warstwa backendowa

Backend pełni rolę bramy i warstwy trwałości. Waliduje wejście (adnotacje
zakresów dla 22 cech), mapuje konwencje nazewnicze (camelCase ↔
SCREAMING_SNAKE_CASE serwisu ML), wyznacza etykiety kalendarzowe okien
względem daty migawki i mapuje błędy na ustrukturyzowaną kopertę
(VALIDATION_FAILED, CONFLICT — duplikat pary klient/data, CLIENT_NOT_FOUND,
ML_SERVICE_ERROR/UNAVAILABLE, INTERNAL_ERROR). Warstwa trwałości (EF Core,
Npgsql, automatyczne migracje przy starcie) przechowuje encje: Client
(unikalny identyfikator biznesowy), Snapshot (data + pełne 22 cechy wejściowe),
Prediction (PD per model dla okna etykietowanego W3) i Trend (nachylenie
trajektorii i alert per model, aktualizowane w trybie upsert). Zapis migawki
wraz z pięcioma predykcjami i pięcioma trendami wykonywany jest w jawnej
transakcji bazodanowej — awaria w trakcie zapisu nie może pozostawić migawki
bez predykcji; właściwość ta jest weryfikowana testem integracyjnym
z wstrzykniętą awarią na rzeczywistym PostgreSQL.

### 3.4.3. Integracja modeli AI z systemem

Serwis predykcyjny (Flask) ładuje przy starcie pięć skalibrowanych artefaktów
W3 (cztery modele drzewiaste `.pkl` — opakowania CalibratedClassifierCV — oraz
model LSTM `.keras` z zewnętrznym kalibratorem izotonicznym), skalery
i plik progów alertu. Endpoint `POST /predict/timeseries` przyjmuje 22 cechy,
wewnętrznie mapuje wartości każdego z okien W0..W3 w sloty kolumn W3 (dzięki
czemu model trenowany na W3 ocenia każde okno w tej samej przestrzeni cech),
i zwraca: trajektorię (5 modeli × 4 okna), trendy z regułą alertu opartą na
nachyleniu (W3 − W0), progi kosztowe, flagi alertów per okno oraz wyjaśnienia
SHAP (pięć najistotniejszych cech per model drzewiasty, dla okna W3). Historyczny
endpoint `POST /predict` (modele 6-miesięczne bez kalibracji) zachowano jako
punkt odniesienia — oba tryby są rozdzielone i nie mieszają artefaktów.

### 3.4.4. Warstwa frontendowa

Interfejs (React 19, TypeScript, Vite; wykresy Recharts) ma dwie zakładki.
Zakładka *Prediction* odtwarza klasyczną, jednorazową ocenę (formularz 22 cech,
karty wyników per model). Zakładka *Monitoring* realizuje Wariant B: lista
monitorowanych klientów z rozwijaną historią (master–detail), wykres trajektorii
PD (pięć linii, cztery okna), karty alertów semaforowych per model, formularz
datowanej migawki z funkcją kopiowania poprzednich wartości oraz komponent
wyjaśnień SHAP (poziome słupki rozbieżne: wkład dodatni podnosi PD). Warstwa
typów TypeScript odwzorowuje kontrakt API w pełnej, pięciomodelowej postaci.

## 3.5. Obsługa wyjątków i scenariusze brzegowe

Obsługę błędów zaprojektowano w trzech warstwach. Serwis ML odrzuca żądania
z brakującym lub nienumerycznym polem (kod VALIDATION_FAILED) — walidacja typów
zapobiega zarówno awarii ścieżki sekwencyjnej, jak i cichej imputacji zera
w ścieżce statycznej (zero jest w tym zbiorze znaczącą wartością statusu
płatności). Backend mapuje niedostępność serwisu ML na 503, jego błędy na 502,
duplikat migawki na 409, nieznanego klienta na 404, a scenariusze brzegowe cech
ilorazowych (np. zerowy limit) neutralizuje identycznie jak trening. Frontend
tłumaczy kody błędów na komunikaty użytkownika. Scenariusze te są pokryte
testami integracyjnymi wszystkich trzech warstw.

## 3.6. Narzędzia i środowisko technologiczne

Stack: Python 3.11 (scikit-learn, XGBoost, LightGBM, CatBoost,
TensorFlow/Keras, fairlearn, SHAP, Optuna), Flask; .NET 8 (ASP.NET Core,
EF Core, Npgsql); React 19 + TypeScript + Vite; PostgreSQL 16; Docker Compose.
Testy: pytest (serwis ML — w tym testy parytetu trening/serwing), xUnit
(backend — w tym testy integracyjne na rzeczywistym PostgreSQL przez
Testcontainers), Vitest (frontend). Metodyka pracy: GitHub Flow — gałęzie
funkcjonalne, przegląd drugiego autora dla każdego pull requesta, ciągła
integracja (cztery zadania: backend, serwis ML, warstwa treningowa, frontend)
blokująca scalenie przy czerwonych testach. Zakres prac zdekomponowano na
zadania CREDIT-XXX z jawnym grafem zależności i definicją ukończenia,
prowadzone w sześciu dwutygodniowych sprintach planistycznych; postęp
dokumentowano w plikach TASKS.md i CHECKLIST.md w repozytorium. Wszystkie
wyniki liczbowe rozdziału 5 są reprodukowalne pojedynczym uruchomieniem
skryptów warstwy treningowej (`main.py` + skrypty ewaluacyjne), a trening
modelu sekwencyjnego jest deterministyczny (ustalone ziarno losowe).
