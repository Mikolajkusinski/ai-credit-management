# Fable5_Task3.md — Rygorystyczny przegląd poprawności kodu ML (trening ↔ inferencja)

> **Autor:** Claude Fable 5 · **Data:** 2026-07-06
> **Zakres:** `ml-service/app.py`, `ml-service/features.py`, `ml-service/sliding_window.py`
> w konfrontacji z kodem treningowym `ml-learing-center/` (main.py, features.py,
> sliding_window.py). Fokus: zgodność cech trening↔inferencja, osie/kolejność sekwencji
> LSTM, obsługa skalerów (transform vs refit), NaN/dzielenie przez zero.
> **Metoda:** lektura pełnego kodu obu stron + **weryfikacja empiryczna** kluczowych
> hipotez na realnych artefaktach (`rf_model_w3.pkl`, `scaler_w3.pkl`, `features_w3.pkl`)
> i realnym zbiorze UCI. Zgodnie z poleceniem raportuję KAŻDE ustalenie, także
> potwierdzenia poprawności — bez wstępnego filtrowania.
>
> Weryfikacje wykonane przed napisaniem tego raportu:
> - `ml-learing-center/features.py` ↔ `ml-service/features.py`: **bajt w bajt identyczne** (diff pusty).
> - `ml-learing-center/sliding_window.py` ↔ `ml-service/sliding_window.py`: **identyczne**.
> - zachowanie `pd.get_dummies(drop_first=True)` na 1-wierszowej ramce: **zwraca 0 kolumn dummy** (pandas 2.3.3).
> - wpływ na predykcje RF W3 (n=300, realni klienci): patrz U1.

---

## 0. Podsumowanie wykonawcze

| ID | Ustalenie | Waga | Pewność |
|---|---|---|---|
| U1 | **Inferencja Flask zeruje WSZYSTKIE cechy demograficzne** (SEX/EDUCATION/MARRIAGE) — `get_dummies(drop_first=True)` na 1-wierszowej ramce zwraca zero kolumn dummy, backfill wstawia 0. Dotyczy OBU ścieżek (legacy i W3) oraz SHAP | **Krytyczna** | Pewne (potwierdzone empirycznie + skwantyfikowane) |
| U2 | `get_dummies` bez stałych kategorii = wynik zależny od kompozycji batcha; działa dziś tylko dlatego, że trening/ewaluacja używają pełnego zbioru | Wysoka | Pewne |
| U3 | Legacy `engineer_features` w app.py **nie ma** `fillna/replace(inf)` — `LIMIT_BAL=0` → inf → wyjątek sklearn → HTTP 500 | Średnia | Pewne (dzielenia potwierdzone empirycznie) |
| U4 | Wszystkie skalery (legacy i W3, statyczne i LSTM) **fitowane na pełnym zbiorze PRZED splitem** — leakage treningowy sprzeczny z deklaracją „zamrożonego" testu w pracy | Średnia (metodologicznie) / niska (liczbowo) | Pewne |
| U5 | Kolejność sekwencji LSTM trening↔inferencja: **ZGODNA** (zweryfikowane, w tym pułapka PAY_0↔BILL_AMT1) | — (OK) | Pewne |
| U6 | Skalery przy inferencji: **wyłącznie `.transform()`, nigdy refit** — ZGODNE z wymaganiem | — (OK) | Pewne |
| U7 | Walidacja wejścia sprawdza tylko obecność kluczy, nie typ/null → `null` daje cichą imputację 0 albo 500 zamiast 400 | Niska | Pewne |
| U8 | Legacy `/predict`: nieskalibrowane modele + próg 0.5 — inne decyzje niż ścieżka W3 | Niska (świadome legacy) | Pewne |
| U9 | SHAP liczony na modelu bazowym (przed kalibracją) — wartości nie sumują się do serwowanego PD | Info | Pewne |
| U10 | SHAP liczony na wejściu dotkniętym U1 (wyzerowane demografie) | Info (pochodna U1) | Pewne |
| U11 | `_shap_values_positive_class` — heurystyka kształtów zależna od wersji shap, bez testu kontraktowego | Niska | Wysokie |
| U12 | Okna W0..W2 transformowane skalerem fitowanym na W3 — świadome, ale nieopisane w pracy przesunięcie rozkładu | Info/średnia (do opisania) | Pewne |
| U13 | `fillna(0)` w features.py — semantycznie znacząca cicha imputacja (PAY=0 to realny status „płaci terminowo") | Niska (mina) | Pewne |
| U14 | `utilization_rate`/`severe_late` trening↔inferencja W3: **ZGODNE** (fix CREDIT-102 potwierdzam) | — (OK) | Pewne |
| U15 | `features_w3.pkl` zgodny z listą generowaną na pełnym zbiorze (assert przeszedł); złamie się przy regeneracji na podzbiorze | Niska | Pewne |
| U16 | Testy `ml-service/tests/` sprawdzają kontrakt JSON, **nie parytet liczbowy** batch↔single-row — dlatego U1 przeszedł niezauważony | Średnia (proces) | Pewne |

**Werdykt przed obroną:** U1 wymaga naprawy przed jakimkolwiek demo na żywo —
system serwujący ocenia dziś każdego klienta tak, jakby miał domyślne dane
demograficzne, więc liczby z demo nie zgodzą się z raportami ewaluacyjnymi
z pracy. Pozostała architektura wymiany cech (kolejność kolumn, osie LSTM,
transform-only skalery) jest poprawna — zweryfikowałem to wprost.

---

## 1. Ustalenia szczegółowe

### U1 — KRYTYCZNE: zerowanie cech demograficznych przy inferencji pojedynczego klienta

**Lokalizacja:**
- `ml-service/features.py:56` — `pd.get_dummies(out, columns=["EDUCATION","MARRIAGE","SEX"], drop_first=True)` wywoływane przez `ml-service/app.py:168` (`engineer_features_w3`) na ramce **z jednym wierszem**;
- `ml-service/app.py:118` — identyczny wzorzec w ścieżce legacy;
- `ml-service/app.py:120-123` i `app.py:169-171` — pętle backfill `if col not in df.columns: df[col] = 0`, które maskują problem.

**Mechanizm:** `get_dummies` tworzy kolumny dummy tylko dla wartości *obserwowanych*
w ramce. Przy jednym wierszu każda zmienna kategoryczna ma dokładnie jedną
obserwowaną wartość → powstaje dokładnie jedna kolumna dummy → `drop_first=True`
usuwa pierwszą (czyli jedyną) → **zostaje zero kolumn**. Backfill wstawia 0 do
wszystkich kolumn z `features_w3.pkl` (`EDUCATION_1..6`, `MARRIAGE_1..3`, `SEX_2`).

**Potwierdzenie empiryczne (pandas 2.3.3):**
```
pd.get_dummies(1-wiersz, columns=[EDUCATION,MARRIAGE,SEX], drop_first=True).columns  →  []
```

**Skutek:** każdy klient scorowany przez Flask (`/predict` i `/predict/timeseries`)
jest traktowany jak: mężczyzna (SEX_2=0), EDUCATION=0, MARRIAGE=0 — niezależnie
od danych, które przysłał. Kobieta z wyższym wykształceniem i klient-baseline
dostają identyczny wektor demograficzny.

**Kwantyfikacja (RF W3, 300 losowych realnych klientów, referencja = ścieżka
batchowa identyczna z treningiem/ewaluacją):**
- średnia |Δ PD| = **0.0086**, p95 = **0.039**, max = **0.086**;
- **9/300 klientów (3%) zmienia decyzję alertu** przy progu kosztowym 0.145;
- 206/300 predykcji identycznych (drzewa są odporne punktowo — to maskuje buga);
- dotyka i kobiet (54/186 w próbie), i mężczyzn (40/114 — przez EDUCATION/MARRIAGE).

**Konsekwencje dla pracy:** liczby z ewaluacji (`metrics_w3.csv`, fairness,
static-vs-dynamic — wszystkie liczone ścieżką batchową na pełnym zbiorze) są
**poprawne**, ale **system live pokazuje inne PD** niż raporty. Na obronie demo
na żywo może przeczyć tabelom z rozdz. 5. Dodatkowo SHAP (U10) wyjaśnia predykcje
policzone na wyzerowanych demografiach.

**Pewność:** pewne. **Waga:** krytyczna.

**Poprawka:** wymusić stały zbiór kategorii przed `get_dummies` (szczegóły
w prompcie O1): rzutować kolumny na `pd.Categorical` z pełnymi listami kategorii
z UCI (SEX: [1,2]; EDUCATION: [0..6]; MARRIAGE: [0..3]) — wtedy `drop_first=True`
zawsze zrzuca tę samą kategorię bazową, a pozostałe dummy powstają z poprawnymi
wartościami także dla jednego wiersza. Dodać test parytetu batch↔single-row (O2).

---

### U2 — WYSOKA: `get_dummies` zależny od kompozycji batcha (wspólny korzeń z U1)

**Lokalizacja:** `ml-learing-center/features.py:56` = `ml-service/features.py:56`
(pliki identyczne); analogicznie legacy w `ml-learing-center/main.py:59`
i `ml-service/app.py:118`.

**Obawa:** nawet dla ramek wielowierszowych zestaw i znaczenie kolumn dummy
zależą od tego, które wartości występują w danych. Przykład potwierdzony w teście:
batch bez `EDUCATION=0` → `drop_first` zrzuca `EDUCATION_1` zamiast `EDUCATION_0`
→ cała macierz kategorii przesunięta o jedną kolumnę względem treningu, a backfill
zerami cicho to maskuje. Dziś nie strzela tylko dlatego, że trening, `evaluation.py`
i `fairness_audit.py` wołają `engineer_features` na pełnym 30-tysięcznym zbiorze,
w którym wszystkie kategorie występują.

**Ryzyko:** każdy przyszły skrypt na podzbiorze (bootstrap, seed demo, appendix
fairness) może dostać cicho przekłamane cechy. `seed_demo_clients.py` — do
sprawdzenia w ramach naprawy.

**Pewność:** pewne (mechanizm zademonstrowany). **Waga:** wysoka (mina).
**Poprawka:** ta sama co U1 — stałe kategorie w JEDNYM miejscu (`features.py`),
skopiowane do obu katalogów lub współdzielone.

---

### U3 — ŚREDNIA: legacy `engineer_features` bez czyszczenia NaN/inf

**Lokalizacja:** `ml-service/app.py:110` (`utilization_rate = BILL_mean / LIMIT_BAL`),
`app.py:113` (`payment_ratio = PAY_AMT_mean / (BILL_mean + 1)`); brak odpowiednika
`X.fillna(0)` + `replace([inf,-inf], 0)`, które trening wykonuje w
`ml-learing-center/main.py:72-75`.

**Potwierdzone empirycznie:** `LIMIT_BAL=0` → `inf`; `BILL_mean=0, LIMIT_BAL=0`
→ `NaN`; `BILL_mean=-1` (ujemne BILL_AMT istnieją w UCI) → `inf` w payment_ratio.
`scaler.transform` propaguje inf, a model sklearn rzuca wyjątek → klient dostaje
HTTP 500 zamiast walidacji 400.

**Mitygacja istniejąca:** backend .NET waliduje `LIMIT_BAL` w zakresie 10 000–1 000 000,
więc przez normalny frontend przypadek nie zachodzi; Flask wołany bezpośrednio —
niezabezpieczony. Ścieżka W3 jest czysta (features.py:69 robi cleanup).

**Pewność:** pewne. **Waga:** średnia.
**Poprawka:** dodać identyczny cleanup jak w treningu przed `scaler.transform`
(prompt O3).

---

### U4 — ŚREDNIA (metodologia) / NISKA (liczby): skalery fitowane przed splitem

**Lokalizacja (wszystkie w treningu):**
- `ml-learing-center/main.py:77-78` — legacy `scaler.fit_transform(X)` na pełnych 30 000 wierszy, split dopiero w linii 80-82;
- `ml-learing-center/main.py:129-134` — legacy `lstm_scalers` fitowane na pełnym `X_seq`;
- `ml-learing-center/main.py:233-234` — `scaler_w3.fit_transform(X_w3)` na pełnym zbiorze, split 3-way w liniach 238-243;
- `ml-learing-center/main.py:312` — `prepare_lstm_sequences(df_w3, W3)` fituje `lstm_scalers_w3` na pełnym `df_w3`.

**Obawa:** statystyki skalera (mean/std) liczone z udziałem wierszy testowych =
wyciek preprocessingu. Liczbowo efekt znikomy (StandardScaler nie widzi etykiet,
a 30k wierszy stabilizuje statystyki), ale stoi w sprzeczności z deklaracją
w pracy (sekcja 4.1.1: test „zamrożony", niewidziany na żadnym etapie) — i komisja
może to wytknąć przy pytaniu o rygor.

**Ważne rozróżnienie:** przy **inferencji** wszystko jest poprawnie — wyłącznie
`transform` (patrz U6). Problem dotyczy tego, JAK artefakty powstały w treningu.

**Pewność:** pewne. **Waga:** średnia metodologicznie.
**Poprawka:** fit skalera po splicie, wyłącznie na części treningowej (lub
train+calib), transform pozostałych; wymaga retrenu i regeneracji artefaktów +
przeliczenia raportów (prompt O4). Alternatywa minimalna: jawnie opisać w pracy
jako świadome uproszczenie z uzasadnieniem znikomego wpływu.

---

### U5 — ZWERYFIKOWANE OK: kolejność sekwencji LSTM trening↔inferencja

Sprawdziłem oś po osi — zgodne, w tym najbardziej podatna na pomyłkę para:

- **Legacy 6-mies.:** trening `main.py:116-126` buduje krok t z
  `pay_seq_cols[t]`/`bill_seq_cols[t]`/`pay_amt_seq_cols[t]`, gdzie listy idą
  od kwietnia do września i **wrzesień = (PAY_0, BILL_AMT1, PAY_AMT1)** —
  numeracja UCI jest przesunięta (PAY_1 nie istnieje). Inferencja `app.py:130-137`
  odtwarza dokładnie to mapowanie wierszami: `[PAY_6,BILL_AMT6,PAY_AMT6] …
  [PAY_2,BILL_AMT2,PAY_AMT2], [PAY_0,BILL_AMT1,PAY_AMT1]`. ✓
- **W3:** trening `features.py:89-93` (kanały 0=PAY, 1=BILL, 2=AMT; czas
  oldest→newest wewnątrz okna) ↔ inferencja `app.py:178-181` (wiersz t =
  `[pay[t], bill[t], amt[t]]`). ✓
- **Reshape:** `sequence_scaled.reshape(1, 3, 3)` na tablicy (3,3) oraz
  `reshape(1, 6, 3)` na (6,3) — dokłada tylko oś batcha, bez transpozycji. ✓
- **Skalowanie per kanał:** trening skaluje kanał f po spłaszczeniu (N·T,1);
  inferencja transformuje kolumnę f sekwencji (T,1) tym samym skalerem. ✓
- **Mapowanie okien W0..W2** (`app.py:152-161` `map_to_w3_columns`): wartości
  okna wstawiane w sloty W3 zachowują porządek oldest→newest; `engineer_features`
  czyta wyłącznie sloty W3. ✓

**Wniosek:** brak błędu o jeden i błędu osi. To można na obronie powiedzieć
z pewnością — zweryfikowane odczytem obu stron i zgodnością definicji
`WINDOW_DEFS` (pliki `sliding_window.py` identyczne bajt w bajt).

---

### U6 — ZWERYFIKOWANE OK: skalery przy inferencji wyłącznie `transform`

- `app.py:125` — `scaler.transform(df)` (legacy statyczne); ✓
- `app.py:142` — `lstm_scalers[f].transform(...)` (legacy LSTM); ✓
- `app.py:173` — `scaler_w3.transform(X)` (W3 statyczne); ✓
- `app.py:186` — `lstm_scalers_w3[f].transform(...)` (W3 LSTM); ✓
- wszystkie artefakty ładowane raz przy starcie (`app.py:27-47`), żadnego
  `fit`/`fit_transform` w ścieżkach request-owych. ✓
- zgodność nazw/kolejności kolumn ze skalerem: inferencja wymusza porządek
  `df[feature_names]` / `X[features_w3]` przed transformem — listy pochodzą
  z tych samych plków .pkl, którymi trenowano; potwierdziłem assertem, że
  `engineer_features(pełny df, W3)` zwraca listę identyczną z `features_w3.pkl`. ✓

Zastrzeżenie: poprawność „transform-only" nie naprawia U4 (jak skalery były
fitowane) ani U1 (co jest transformowane).

---

### U7 — NISKA: walidacja wejścia tylko po obecności klucza

**Lokalizacja:** `app.py:88-93` (REQUIRED_FIELDS), `app.py:272-274`, `app.py:316-324`.

**Obawa:** `{"PAY_6": null}` przechodzi walidację. Dalej: w ścieżce statycznej
NaN → `fillna(0)` w features.py:69 → **cicha imputacja zerem** (PAY=0 znaczy
„płaci terminowo"!); w ścieżce LSTM `np.array([[None,...]], dtype=np.float32)`
→ TypeError → HTTP 500 `INTERNAL_ERROR` zamiast 400 `VALIDATION_FAILED`.
Niespójne zachowanie dwóch ścieżek na tych samych złych danych.

**Pewność:** pewne. **Waga:** niska (backend waliduje upstream).
**Poprawka:** walidacja typów/null we Flask (prompt O3).

---

### U8 — NISKA: legacy `/predict` — nieskalibrowane prawdopodobieństwa + próg 0.5

**Lokalizacja:** `app.py:276-295`. Modele legacy trenowane z
`class_weight="balanced"`/`scale_pos_weight` mają systematycznie zawyżone
prawdopodobieństwa (to koryguje dopiero kalibracja w W3), a etykieta
`DEFAULT if p >= 0.5` używa progu, który w ścieżce W3 zastąpiono progami
kosztowymi 0.130–0.185. Dwa endpointy dają nieporównywalne decyzje dla tego
samego klienta. Udokumentowane jako legacy — ale jeśli demo/praca gdziekolwiek
cytuje `/predict`, będzie niespójność.

**Pewność:** pewne. **Waga:** niska (świadoma decyzja architektoniczna).
**Poprawka:** nie dotykać przed obroną; ewentualnie adnotacja w pracy, że
`/predict` to zachowany baseline sprzed Wariantu B.

---

### U9 — INFO: SHAP w przestrzeni modelu bazowego, nie serwowanego PD

**Lokalizacja:** `app.py:50-58` (`_unwrap_calibrated`), `app.py:64-70`.
TreeExplainer działa na modelu sprzed kalibracji izotonicznej. Ranking cech
zachowany (kalibracja monotoniczna), ale wartości SHAP nie sumują się do
serwowanego, skalibrowanego PD (local accuracy nie zachodzi względem odpowiedzi
API) i są w różnych skalach dla różnych modeli (XGBoost: log-odds margin;
RF: prawdopodobieństwo). Docstring uczciwie to przyznaje. Do odnotowania
w sekcji 4.4.2 pracy — komisja może zapytać „czy suma SHAP = predykcja?".

**Pewność:** pewne. **Waga:** informacyjna.

### U10 — INFO (pochodna U1): SHAP liczony na wyzerowanych demografiach

**Lokalizacja:** `app.py:223` (`X_static = engineer_features_w3(data, W3)`).
Po naprawie U1 wyjaśnienia SHAP dla klientów z niebazowymi demografiami zmienią
wartości — trzeba będzie zaktualizować oczekiwania testów i ewentualne zrzuty
w pracy/prezentacji.

### U11 — NISKA: heurystyka kształtów SHAP bez testu kontraktowego

**Lokalizacja:** `app.py:194-209`. Obsługa trzech formatów zwrotki
(`list`, 3D, 2D) pokrywa znane wersje shap dla RF/XGB/LGBM/CatBoost, ale nie ma
testu przypinającego zachowanie per model — aktualizacja biblioteki shap może
cicho zmienić klasę, dla której zwracane są wartości (np. wziąć klasę 0 zamiast 1).
**Poprawka:** test jednostkowy: dla znanego klienta znak/top cechy per model (O2).

### U12 — INFO/ŚREDNIA: okna W0..W2 przez skaler i model W3 (przesunięcie rozkładu wpisane w projekt)

**Lokalizacja:** `app.py:149-173` + docstring w `sliding_window.py:14-16`.
Świadoma decyzja projektowa (jedna przestrzeń cech dla trajektorii), ale
oznacza, że PD na starszych oknach zawiera komponent przesunięcia rozkładu —
wiąże się wprost z dominacją okna W0 w histogramie lead time
(`reports/lead_time_report.md`: RF W0=352 z 661 wykryć) i z findingiem #14
z `Fable5_Task1.md`. Nie bug — ale musi być opisane w rozdz. 3 pracy jako
ograniczenie, bo inaczej „lead time ~2 okna" jest podważalny jednym pytaniem.

### U13 — NISKA: `fillna(0)` semantycznie znaczący

**Lokalizacja:** `features.py:69` (obie kopie). Zero to realna wartość statusu
PAY („płaci terminowo") i realna wartość BILL/AMT — imputacja braków zerem
przekłamuje znaczenie zamiast odrzucić rekord. W UCI braków nie ma (martwy kod
w treningu), ale w serwisie NaN może powstać z `null` w JSON (patrz U7).
**Poprawka:** walidacja null na wejściu (O3) czyni ten punkt czysto defensywnym.

### U14 — ZWERYFIKOWANE OK: parytet `utilization_rate` i `severe_late`

Trening `main.py:38` = inferencja legacy `app.py:110` (`BILL_mean / LIMIT_BAL`);
trening `main.py:53` = inferencja `app.py:115` (`(pay >= 2).any(axis=1).astype(int)`);
ścieżka W3 używa dosłownie wspólnego pliku. Historyczne bugi z CREDIT-102
(BILL_AMT1/LIMIT_BAL i `.sum()` zamiast `.any()`) — potwierdzam, że są naprawione
i obie strony są zgodne.

### U15 — NISKA: `features_w3.pkl` poprawny dziś, kruchy na regenerację

Assert `engineer_features(pełny df, W3)[1] == joblib.load("features_w3.pkl")`
przeszedł (kolejność: 13 pochodnych, 9 kolumn okna, EDUCATION_1..6,
MARRIAGE_1..3, SEX_2). Kruchosć: regeneracja na podzbiorze danych da inną listę
(U2). Legacy `features.pkl` ma ten sam zestaw kategorii — też zweryfikowane.

### U16 — ŚREDNIA (proces): testy nie łapią rozjazdu liczbowego

**Lokalizacja:** `ml-service/tests/test_timeseries.py` (211 linii),
`test_smoke.py` (17 linii). Testy weryfikują kontrakt JSON (obecność pól,
liczbę okien, typy) i kierunek trendu — **żaden nie porównuje PD z serwisu
z PD policzonym ścieżką batchową** dla tego samego klienta. Dlatego U1 przeszedł
przez CI. **Poprawka:** test parytetu (golden test) — prompt O2.

---

## 2. Instrukcje zmian — kolejność wykonania

1. **O1** — fix U1/U2 (stałe kategorie w features.py + app.py legacy). Najpierw,
   bo wszystko inne (testy, regeneracje) zależy od tego.
2. **O2** — test parytetu batch↔single-row + test kontraktu SHAP (domyka U1/U11/U16;
   od tej pory regresja niemożliwa cicho).
3. **O3** — hardening wejścia i legacy cleanup (U3/U7/U13).
4. **O4** — (decyzja świadoma, opcjonalne) naprawa protokołu fitowania skalerów
   (U4) — wymaga retrenu i przeliczenia WSZYSTKICH raportów; wykonać razem
   z ewentualnym B2 z `Fable5_Task1.md` (progi na splicie kalibracyjnym), żeby
   przeliczać raporty tylko raz.
5. **O5** — regeneracja artefaktów i raportów po fixach + aktualizacja liczb
   w dokumentach pracy.

**Uwaga o wpływie na pracę magisterską:** U1 NIE unieważnia wyników z rozdz. 5
(ewaluacja szła poprawną ścieżką batchową). Unieważnia zgodność live-demo
z raportami oraz każdy artefakt wygenerowany przez serwis Flask
(np. zrzuty ekranów SHAP/PD w prezentacji — do regeneracji po fixie).

---

## 3. Gotowe prompty dla Opusa 4.8

### O1 — Naprawa U1/U2: stałe kategorie w one-hot encodingu

```text
W tym repo jest potwierdzony bug train/serve skew: pd.get_dummies(...,
drop_first=True) na 1-wierszowej ramce zwraca ZERO kolumn dummy (jedyna
obserwowana kategoria jest jednocześnie "pierwszą" i zostaje zrzucona),
a pętle backfill w ml-service/app.py wstawiają 0 — przez co inferencja Flask
zeruje wszystkie cechy demograficzne każdego klienta. Napraw to tak:

1. W ml-learing-center/features.py (UWAGA: ml-service/features.py to jego
   bajt-w-bajt kopia — zmień OBA pliki identycznie) dodaj na początku modułu
   stałe: UCI_CATEGORIES = {"SEX": [1, 2], "EDUCATION": [0, 1, 2, 3, 4, 5, 6],
   "MARRIAGE": [0, 1, 2, 3]}. W engineer_features(), przed get_dummies,
   rzutuj: out[col] = pd.Categorical(out[col].astype(int),
   categories=UCI_CATEGORIES[col]) dla każdej z trzech kolumn. Dzięki temu
   get_dummies(drop_first=True) ZAWSZE produkuje ten sam zestaw kolumn
   (EDUCATION_1..6, MARRIAGE_1..3, SEX_2) z poprawnymi wartościami, niezależnie
   od liczby wierszy i kompozycji danych.
2. Ta sama poprawka w legacy ścieżce ml-service/app.py:118 (funkcja
   engineer_features) — rzutowanie na Categorical przed get_dummies.
3. ZWERYFIKUJ zgodność wsteczną: uruchom skrypt sprawdzający, że dla pełnego
   zbioru UCI nowa engineer_features zwraca kolumny w DOKŁADNIE tej samej
   kolejności i z tymi samymi wartościami co joblib.load("features_w3.pkl")
   i że scaler_w3.transform przechodzi bez błędu nazw cech. Jeśli kolejność
   kolumn się zmienia (get_dummies z Categorical sortuje po kategoriach, nie
   po obserwacjach) — nie zmieniaj features_w3.pkl, tylko dopasuj kod tak, by
   zwracał kolumny w porządku zapisanej listy (selekcja X = out[saved_features]
   już to robi w app.py; upewnij się, że features zwracane przez
   engineer_features na pełnych danych są identyczne z zapisanymi).
4. Po fixie porównaj predykcje: dla 300 losowych klientów (random_state=7)
   PD z ścieżki single-row (jak Flask) musi być IDENTYCZNE (atol=1e-12) z PD
   ze ścieżki batchowej dla wszystkich 5 modeli W3. Wypisz wynik porównania.
5. Sprawdź też ml-learing-center/seed_demo_clients.py — czy nie woła
   engineer_features na podzbiorze i nie jest dotknięty tym samym problemem.
NIE regeneruj modeli — one były trenowane na pełnym zbiorze i są poprawne;
naprawiamy wyłącznie ścieżkę inferencji.
```

### O2 — Testy parytetu i kontraktów (U1/U11/U16)

```text
W ml-service/tests/ dodaj plik test_train_serve_parity.py z testami, które
uniemożliwią cichy powrót train/serve skew:

1. test_single_row_dummies_match_batch: dla 20 klientów o zróżnicowanych
   demografiach (obie płcie, EDUCATION 0-6, MARRIAGE 0-3 — zbuduj syntetycznie,
   wartości płatności dowolne sensowne) porównaj wektor cech z
   engineer_features (features.py) wywołanej: (a) na ramce 20-wierszowej,
   (b) wiersz po wierszu z backfillem jak w app.py engineer_features_w3.
   Po selekcji do features_w3.pkl macierze muszą być identyczne.
   W szczególności: klientka SEX=2 MUSI mieć SEX_2=1 w ścieżce single-row.
2. test_predict_parity_static: przez Flask test client wyślij na
   /predict/timeseries klienta-kobietę z EDUCATION=3, MARRIAGE=2 i porównaj
   zwrócone PD W3 (randomForest) z PD policzonym bezpośrednio:
   rf_w3.predict_proba(scaler_w3.transform(X_batch))[0,1], gdzie X_batch
   pochodzi ze ścieżki batchowej. Tolerancja 1e-9.
3. test_lstm_axes: zbuduj klienta, którego 3 miesiące W3 mają jednoznacznie
   różne wartości (np. PAY_3=1, PAY_2=2, PAY_0=3); przechwyć tensor z
   prepare_lstm_input_w3 i sprawdź, że oś czasu idzie oldest->newest
   (tensor[0,0,0] odpowiada przeskalowanemu PAY_3, tensor[0,2,0] PAY_0)
   i że kanały to 0=PAY, 1=BILL, 2=AMT.
4. test_shap_positive_class_contract: dla każdego z 4 explainerów sprawdź, że
   _shap_values_positive_class zwraca wektor o długości len(features_w3)
   oraz że dla klienta o skrajnie złej historii płatniczej (PAY_max wysoki)
   wartość SHAP cechy PAY_max jest DODATNIA (pcha PD w górę) — to przypina
   wybór klasy pozytywnej niezależnie od wersji shap.
5. test_null_payload: wyślij poprawny payload z "PAY_6": null — endpoint ma
   zwrócić 400 VALIDATION_FAILED, nie 500 (ten test początkowo będzie czerwony,
   naprawa w osobnym zadaniu O3 — oznacz xfail z komentarzem, jeśli robisz O2
   przed O3).
Uruchom pytest i pokaż wyniki. Style testów dopasuj do istniejącego
test_timeseries.py (fixture client, stałe SAMPLE_*).
```

### O3 — Hardening wejścia i parytet czyszczenia (U3/U7/U13)

```text
W ml-service/app.py wykonaj trzy poprawki poprawnościowe:

1. (U3) W legacy engineer_features (app.py, funkcja z pd.DataFrame([data]))
   po zbudowaniu cech, PRZED scaler.transform, dodaj identyczny cleanup jak
   w treningu (ml-learing-center/main.py:72-75):
   df = df.fillna(0).replace([np.inf, -np.inf], 0). Komentarz: parity z
   treningiem; inf powstaje przy LIMIT_BAL=0 (utilization_rate) i
   BILL_mean=-1 (payment_ratio).
2. (U7) Rozszerz walidację obu endpointów: poza obecnością pola sprawdzaj,
   że wartość jest liczbą (int/float, nie None, nie string, nie bool) —
   w /predict zwracaj {"error": ...} 400 jak dotąd, w /predict/timeseries
   zwracaj envelope VALIDATION_FAILED z details.field. Wynieś wspólną
   funkcję _validate_payload(data) -> (ok, error_field).
3. (U13, defensywnie) Po walidacji z pkt 2 fillna(0) w features.py staje się
   martwy dla serwisu — zostaw go (trening go używa), ale dodaj w
   engineer_features_w3 w app.py komentarz, że null jest odrzucany na
   walidacji, a nie imputowany.
Przetestuj: (a) LIMIT_BAL=0 → poprawna odpowiedź 200 z sensownym PD (nie 500),
(b) PAY_6=null → 400 z VALIDATION_FAILED w obu endpointach, (c) istniejące
testy pytest zielone. Usuń xfail z test_null_payload, jeśli istnieje po O2.
```

### O4 — (opcjonalne, decyzja metodologiczna) fit skalerów po splicie (U4)

```text
Kontekst: w ml-learing-center/main.py wszystkie skalery są fitowane na pełnym
zbiorze PRZED train_test_split (linie 77-78 legacy static, 129-134 legacy LSTM,
233-234 scaler_w3, 312 lstm_scalers_w3 przez prepare_lstm_sequences), co jest
wyciekiem preprocessingu sprzecznym z deklaracją "zamrożonego" testu w pracy
magisterskiej. Przeprowadź naprawę WYŁĄCZNIE dla pipeline'u W3 (legacy zostaw —
jest opisany w pracy jako baseline historyczny):

1. Zmień protokół: najpierw split indeksów 60/20/20 (dokładnie ta sama
   sekwencja dwóch train_test_split z random_state=42 i stratify co obecnie —
   NIE zmieniaj przydziału wierszy!), potem scaler_w3.fit wyłącznie na części
   treningowej i transform pozostałych. Dla LSTM: rozszerz
   prepare_lstm_sequences w features.py o opcjonalny parametr
   scalers=None — gdy podane, transform zamiast fit_transform; fituj na
   części treningowej. Zmień OBA egzemplarze features.py identycznie.
2. Przetrenuj: python main.py. Porównaj stare i nowe artefakty: AUC/Brier
   per model przed i po zmianie (oczekiwanie: różnice < 0.001 — StandardScaler
   na 18k vs 30k wierszy daje niemal identyczne statystyki). Zapisz porównanie
   w reports/scaler_leakage_fix.md — to dowód na obronę, że wyciek nie zawyżał
   wyników.
3. Po retrenie uruchom ponownie: evaluation.py, fairness_audit.py,
   timeseries_eval.py, static_vs_dynamic.py i skopiuj artefakty modeli do
   ml-service/ (jak robi to main.py). Wypisz, które liczby w reports/ się
   zmieniły.
Jeśli różnice okażą się > 0.005 AUC dla któregokolwiek modelu — ZATRZYMAJ się
i zaraportuj przed nadpisaniem czegokolwiek.
```

### O5 — Regeneracja i spójność po fixach

```text
Po wykonaniu O1-O3 (i ewentualnie O4) doprowadź repo do spójności:

1. Uruchom pełny pytest w ml-service/ oraz istniejące skrypty ewaluacyjne
   w ml-learing-center/ (evaluation.py, fairness_audit.py) i potwierdź, że
   liczby w reports/ są niezmienione względem stanu sprzed O1 (fix U1 dotyczy
   tylko inferencji single-row; ewaluacja batchowa nie mogła się zmienić —
   jeśli COKOLWIEK w reports/ się zmieniło, zatrzymaj się i raportuj).
2. Zweryfikuj serwis end-to-end: uruchom Flask, wyślij /predict/timeseries
   dla klientki (SEX=2, EDUCATION=3) i potwierdź, że PD różni się od PD tego
   samego klienta z SEX=1 (przed fixem były identyczne — demografie były
   zerowane).
3. Sprawdź, czy w prezentacja_seminarium/ i thesis_figures/ nie ma zrzutów
   ekranu/liczb wygenerowanych przez serwis Flask przed fixem U1 (PD lub SHAP
   z live systemu) — wypisz listę materiałów do regeneracji.
4. Dopisz do Fable5_Task3.md sekcję "Status po naprawie" z datą, listą
   wykonanych promptów i wynikami weryfikacji 1-3.
5. Zaproponuj wpis do rozdz. 4.5 pracy (3-4 zdania po polsku) opisujący
   wykryty i naprawiony train/serve skew jako przykład rygoru inżynierskiego —
   analogicznie do opisanego już bug-fixa CREDIT-102.
```

---

## 4. Materiał dowodowy (wyniki weryfikacji empirycznych)

```
# pandas 2.3.3, sklearn 1.6.1
1-row get_dummies drop_first=True columns: []            # U1: zero kolumn dummy
multi-row columns: ['EDUCATION_2','EDUCATION_3','MARRIAGE_1','MARRIAGE_2','SEX_2']
                                                          # U2: zestaw zależny od batcha
util 5000/0 = [inf]; util 0/0 = [nan]                     # U3
payment_ratio at BILL_mean=-1: [inf]                      # U3

# Kwantyfikacja U1 — RF W3, 300 realnych klientów, referencja = ścieżka batchowa
#  (identyczna z treningiem; assert features == features_w3.pkl przeszedł):
mean|Δp|=0.0086  max=0.0857  p95=0.0394
identical: 206/300
alert flips @ threshold 0.145: 9/300 (3.0%)
affected by SEX: {female: 54/186, male: 40/114}

# Zgodność plików współdzielonych:
diff ml-learing-center/features.py ml-service/features.py        -> identyczne
diff ml-learing-center/sliding_window.py ml-service/sliding_window.py -> identyczne
features_w3.pkl categorical: EDUCATION_1..6, MARRIAGE_1..3, SEX_2
features.pkl (legacy) categorical: EDUCATION_1..6, MARRIAGE_1..3, SEX_2
```

---

## 5. Co to oznacza dla obrony (TL;DR dla autora)

1. **Napraw U1 przed jakimkolwiek demo na żywo** — dziś system live ocenia
   wszystkich jak klienta-baseline demograficznie; 3% klientów zmienia decyzję
   alertu, a SHAP wyjaśnia nie te dane, które klient wysłał.
2. **Wyniki w pracy (rozdz. 5) pozostają ważne** — ewaluacja szła poprawną
   ścieżką batchową; bug dotyczy wyłącznie serwisu Flask.
3. **Kolejność cech, osie LSTM i transform-only skalerów są poprawne** —
   zweryfikowane; można to na obronie powiedzieć bez asekuracji.
4. **U4 (skalery przed splitem) zdecyduj świadomie**: albo szybki retren (O4)
   z dowodem znikomej różnicy, albo jawny akapit w pracy. Nie zostawiać
   niezaadresowanego — przeczy zdaniu o „zamrożonym" teście z sekcji 4.1.1.
5. Po fixie U1 **naprawiony bug staje się atutem**: drugi (po CREDIT-102)
   udokumentowany przykład rygoru train/serve consistency — materiał na
   akapit w rozdz. 4.5 i dobrą odpowiedź na pytania o jakość inżynierską.
```