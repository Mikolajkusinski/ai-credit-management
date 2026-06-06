# WalidacjaPDFv7.md — czy v7 odpowiedziało na uwagi z DokumentRoznice.md

> Walidacja zmian między **`Praca Magisterska-6.pdf`** (45 stron, 2026-06-06 14:33) a
> **`Praca Magisterska-7.pdf`** (47 stron, 2026-06-06 20:12) w kontekście listy poprawek
> zaproponowanych w `DokumentRoznice.md`.
>
> **Diff:** +212 / −142 linii tekstu (+5%), +2 strony, **+2 pozycje bibliografii** ([30] LightGBM,
> [31] CatBoost).

---

## 1. Podsumowanie wykonawcze

Wersja 7 wprowadziła **dwie istotne zmiany strukturalne** (framing tytułu + dodanie LightGBM/CatBoost
do Roz. 2), ale **NIE napisała żadnego nowego tekstu w Roz. 3 ani Roz. 5** — oba kluczowe rozdziały
(metodologia + projekt systemu oraz analiza wyników) **nadal pozostają pustymi szkieletami**.
Aktualizacje w Roz. 4 ograniczają się do drobnych zmian whitespace.

| Status | Liczba | Co to znaczy |
|---|---|---|
| 🟢 **Pełne wdrożenie** | 3 | Punkt wdrożony tekstowo + bibliografią |
| 🟡 **Częściowe / forward-reference** | 3 | PDF zapowiada (Wstęp / Roz. 2), ale nie dostarcza (Roz. 4/5) |
| 🔴 **Brak wdrożenia** | ~13 | Konkretne luki techniczne pozostały |

**Wniosek nadrzędny:** v7 to **edycja framingu** (wstęp + krótkie wzmianki w Roz. 1.4, 2.2.2, 2.5),
nie merytoryczna aktualizacja Roz. 3/4/5. **Wszystkie problemy techniczne wskazane w
`DokumentRoznice.md` §2-§12 są wciąż otwarte** (poza listą modeli i framingiem tytułu).

---

## 2. Co zostało wdrożone w v7 (🟢 pełne)

### 2.1. Framing tytułu „dynamiczne" — DokumentRoznice §1.1 ✓

**v6 (Wstęp):**
> „Termin »dynamiczne« w tytule pracy odnosi się przy tym **nie do cyklicznej aktualizacji modelu,
> lecz do architektury sekwencyjnej**, która z założenia traktuje ocenę jako funkcję przebiegu zdarzeń"

**v7 (Wstęp):**
> „Termin »dynamiczne« w tytule pracy nie odnosi się przy tym do cyklicznego ponownego trenowania
> modelu, lecz **ma znaczenie dwojakie**: obejmuje zarówno sekwencyjną architekturę sieci LSTM
> (...) jak i **— przede wszystkim — wielokrotną, kalendarzową ocenę tej samej ekspozycji w czasie,
> dającą trajektorię PD oraz umożliwiającą wczesne ostrzeganie** o pogarszającej się sytuacji
> dłużnika."

To dokładnie ta zmiana, którą zaproponowałem w `DokumentRoznice §1.1`. Dwa poziomy „dynamiczne"
explicite wprowadzone. ✓

### 2.2. 3 modele → 5 modeli — DokumentRoznice §3 ✓

**Trzy miejsca zaktualizowane:**

a) **Wstęp v7:** „Przedmiotem badań uczyniono **pięć klasyfikatorów** reprezentujących odmienne
   rodziny algorytmiczne: metody zespołowe oparte na drzewach — las losowy oraz **trzy warianty
   wzmacniania gradientowego (XGBoost, LightGBM, CatBoost)** — operujące na zagregowanym
   wektorze cech (...) którym przeciwstawiono sieć z długą pamięcią krótkotrwałą (LSTM)".

b) **Roz. 2.3 v7:** dodano dwie nowe podsekcje:
   - **2.3.4. LightGBM — wzmacnianie gradientowe z rozrostem liść-po-liściu (leaf-wise)** —
     pełne ~12 zdań z opisem histogramowej dyskretyzacji, leaf-wise growth, GOSS, EFB +
     odnośnik do [30] (Ke et al. NeurIPS 2017).
   - **2.3.5. CatBoost — uporządkowane wzmacnianie (ordered boosting) i natywna obsługa
     cech kategorycznych** — ~10 zdań z opisem ordered boosting, prediction shift, ordered
     target statistics + odnośnik do [31] (Prokhorenkova et al. NeurIPS 2018).

c) **Roz. 2.3.3 closing v7:** „Rodzina ta obejmuje w części badawczej **cztery reprezentanty** —
   las losowy oraz trzy warianty wzmacniania gradientowego (XGBoost, LightGBM, CatBoost),
   omówione w kolejnych podrozdziałach".

d) **Wstęp roadmap v7:** „Rozdział 2 (...) charakterystykę **pięciu** badanych algorytmów".

To dokładnie sek. 2.3.4 + 2.3.5 zaproponowane w `DokumentRoznice §3 propozycja 1`. ✓

### 2.3. Bibliografia +[30] +[31] — DokumentRoznice §3 ✓

```
[30] Ke G., Meng Q., Finley T., Wang T., Chen W., Ma W., Ye Q., Liu T.-Y., „LightGBM: A highly
     efficient gradient boosting decision tree" w NeurIPS 30, 2017, s. 3146-3154.

[31] Prokhorenkova L., Gusev G., Vorobev A., Dorogush A. V., Gulin A., „CatBoost: unbiased
     boosting with categorical features" w NeurIPS 31, 2018, s. 6638-6648.
```

Solidne źródła oryginalne, zgodne z pattern'em bibliografii (NeurIPS, autorstwo, paginacja). ✓

---

## 3. Co zostało wdrożone *częściowo* (🟡 forward-reference, treści brak)

### 3.1. Sliding-window panel — DokumentRoznice §2.1 🟡

**v7 dodało wzmianki w Wstępie + Roz. 1.4 + 2.2.2:**
- Wstęp: „przesuwane okno obserwacji prowadzi do trajektorii prawdopodobieństwa niewykonania
  zobowiązania", „regułą statyczną, opartej na jednorazowej ocenie najnowszego okna, z regułą
  monitorującą".
- 1.4: „Połączenie scoringu behawioralnego z wczesnym ostrzeganiem przekłada się przy tym wprost
  na przyjęty w pracy schemat kalendarzowego monitorowania trajektorii prawdopodobieństwa
  niewykonania zobowiązania, w którym sytuacja tej samej ekspozycji obserwowana jest w
  przesuwanym oknie obserwacji".
- 2.2.2 (closing): „Nurt sekwencyjny i monitorujący [12], [21] motywuje przy tym bezpośrednio
  przyjęty w niniejszej pracy schemat kalendarzowego monitorowania trajektorii prawdopodobieństwa".

**Czego nadal brakuje:**
- **Pełna konstrukcja 4 okien (W0..W3)** — tabela kolumn UCI per okno (PAY_6/5/4 → PAY_3/2/0,
  itd.). To miałoby być w nowej sek. 3.3.4 lub 4.0 wg `DokumentRoznice §2.1 propozycja`.
  **Roz. 3 jest pusty → brak.**
- Uzasadnienie zgodności rozkładów trening (W3) vs inferencja (W0..W3).
- „Nie fabrykujemy danych" jako explicit zasada.

**Status:** v7 zna POJĘCIE „przesuwane okno obserwacji" na poziomie framingu, ale techniczna
implementacja CREDIT-101 nie jest opisana. **Wymaga napisania Roz. 3.**

### 3.2. Kalibracja prawdopodobieństw — DokumentRoznice §6 🟡

**v7 (Wstęp roadmap):** „Rozdział 4 dokumentuje (...) **a także kalibrację prawdopodobieństw**
oraz wyznaczenie progów alertu".

**Czego nadal brakuje:**
- W Roz. 4 (nadal zawiera tylko 4.1–4.5) **nie ma sek. 4.6 „Kalibracja izotoniczna"**.
- Brak opisu CREDIT-105: `CalibratedClassifierCV(FrozenEstimator, isotonic)`, 3-way split, Brier
  −19/−24/−23%.

**Status:** v7 ZAPOWIADA kalibrację w roadmapie, ale **rozdział, w którym miałaby być, jest
niezaktualizowany**.

### 3.3. Cost-optimized thresholds — DokumentRoznice §2.3 🟡

**v7 (Wstęp roadmap):** „...oraz **wyznaczenie progów alertu**".

**Czego nadal brakuje:**
- Brak sek. 4.7 / opisu CREDIT-106: `cost = 5·FN + 1·FP`, per-model progi 0.130–0.185,
  `alert_thresholds.json`.

**Status:** zapowiedziane w roadmapie, niezaimplementowane w treści.

### 3.4. Static vs dynamic (dowód tezy) — DokumentRoznice §7 🟡

**v7 (Wstęp + roadmap):**
- Drugie pytanie badawcze: „czy kalendarzowe monitorowanie trajektorii prawdopodobieństwa
  niewykonania zobowiązania pozwala wykryć pogorszenie sytuacji dłużnika wcześniej niż
  pojedyncza ocena statyczna".
- Roadmap: „Rozdział 5 zawiera (...) **porównanie reguły statycznej z regułą monitorującą**".

**Czego nadal brakuje:**
- CREDIT-110/111 wyniki (catch_rate, lead_time, slope_auc) — nigdzie nie ma liczb.
- Honest verdict @FA=10% (monitoring traci 2-6pp catch ale wygrywa lead time).
- Static-vs-dynamic ROC overlay plots.

**Status:** zapowiedziane (drugi research question + roadmap), ale Roz. 5 pusty ⇒ brak dowodu
liczbowego. **Wymaga napisania Roz. 5.**

### 3.5. Fairness audit — DokumentRoznice §8 🟡

**v7 (sek. 2.5):** „**W części empirycznej** niniejszej pracy dyskryminacja pośrednia względem
atrybutu chronionego zostanie skwantyfikowana, między innymi poprzez **porównanie wskaźników
selekcji oraz wyrównanych szans** pomiędzy grupami, przy czym pełne definicje przyjętych metryk
oraz wyniki audytu należą do rozdziału 5".

**v7 (Wstęp roadmap):** „Rozdział 5 zawiera (...) **oraz audyt fairness**".

**Czego nadal brakuje:**
- Pełne definicje DPD / EOD.
- Tabela wyników CREDIT-112: 5 modeli, |DPD| max 0.039 (CatBoost), min 0.007 (LSTM), wszystkie
  ≤ 0.04 vs DoD 0.10.
- Per-group breakdown (sel_rate, TPR, FPR per SEX).
- 2 PNG (`fairness_selection_rate_w3.png`, `fairness_tpr_fpr_w3.png`).

**Status:** zapowiedziane, niezaimplementowane. **Wymaga sek. 5.5b.**

### 3.6. Roadmap rozdziałów — DokumentRoznice §11 🟡

**v7 (Wstęp):** zaktualizowana zapowiedź Roz. 5 wymienia *cztery* nowe wątki w stosunku do v6:
„analiza wyników, wzajemne porównanie modeli, zestawienie z metodami klasycznymi, **porównanie
reguły statycznej z regułą monitorującą oraz audyt fairness**, a także dyskusję w świetle
postawionych hipotez".

Punkt 3.4 i 3.5 wyżej już to pokrywają — to ta sama zapowiedź. ✓ (na poziomie roadmap'u), ✗ na
poziomie treści.

---

## 4. Co NIE zostało wdrożone (🔴 brak zmian merytorycznych)

### 4.1. Rozdział 3 — CAŁY ROZDZIAŁ NADAL PUSTY 🔴🔴🔴

**Empiryczna weryfikacja:** `grep -n "^Rozdział 3" /tmp/praca_mag_v7.txt` → **brak wyniku w body**
(tylko TOC). Wszystkie sekcje 3.1–3.6 mają w TOC tę samą stronę 23, bo Rozdział 4 zaczyna się też
od strony 23.

**Stan 3.1 Cel i zakres badań** — pusty.

**Stan 3.2 Hipotezy badawcze** — pusty. **TO JEST KRYTYCZNE** — H1/H2/H3 z `DokumentRoznice §1.2`
nie zostały sformalizowane:
- H1: sliding-window 3-mies. zachowuje AUC.
- H2: monitoring W0..W3 oferuje wcześniejszą detekcję.
- H3: modele są fair względem SEX.

**Stan 3.3 Dane** (3.3.1 źródła, 3.3.2 zmienne, 3.3.3 preprocessing/inżynieria cech) — pusty.

**Stan 3.4 Projekt architektury systemu** (3.4.1 ogólna, 3.4.2 backend, 3.4.3 integracja modeli,
3.4.4 frontend) — pusty. **Cała architektura React+/.NET+/Flask+/PostgreSQL nie jest opisana.**

**Stan 3.5 Obsługa wyjątków** — pusty.

**Stan 3.6 Narzędzia** — pusty.

**Powiązane uwagi z `DokumentRoznice`:** §10 (architektura systemu) — wciąż całkowicie nieopisana.
Plan poprawy P0 #2 z `DokumentRoznice §13` (Roz. 3.3 + Roz. 3.4) niewdrożony.

### 4.2. Rozdział 5 — CAŁY ROZDZIAŁ NADAL PUSTY 🔴🔴🔴

**Empiryczna weryfikacja:** `grep -n "^Rozdział 5" /tmp/praca_mag_v7.txt` → **brak w body**.
Wszystkie 5.x w TOC pokazują str. 42, Zakończenie też 42.

**Stan 5.1 Metryki** (dokładność/precyzja/czułość/F1, ROC/AUC, macierz pomyłek) — puste.
**Stan 5.2 Wyniki per model** (LSTM, RF, XGB) — puste.
**Stan 5.3 Wzajemne porównanie** (LSTM/RF/XGB) — puste; nawet w TOC nadal „LSTM, Random Forest i XGBoost" (3 modele, nie 5).
**Stan 5.4 Porównanie z klasycznymi metodami** — puste.
**Stan 5.5 Interpretowalność + przydatność decyzyjna** — puste.
**Stan 5.6 Dyskusja hipotez** — puste.
**Zakończenie** — puste.

**Powiązane uwagi:** §11, §7, §8 (większość ścieżki krytycznej tezy nie jest opisana). Plan poprawy
P0 #5 z `DokumentRoznice §13` (Roz. 5 napisać od zera) niewdrożony.

**Uwaga sekundarna:** TOC sek. 5.3 nadal mówi „LSTM, Random Forest i XGBoost" (3 modele) — sprzeczne
z deklaracją 5-modelową we Wstępie i Roz. 2. **Niespójność TOC vs framing.**

### 4.3. Podział 70/30 — DokumentRoznice §2.2 🔴

Sek. 4.1.1 (s. 24) **niezmieniona** — nadal:
- „wydzielono z niego zbiór testowy o udziale **30%**, co odpowiada **9 000** obserwacji"
- „Pozostałe **70%** (**21 000** rekordów)"
- „W efekcie otrzymano proporcje (...) **56% trenowanie, 14% walidacja, 30% test**"
- Code snippet: `train_test_split(X_scaled, y, test_size=0.3, ...)`

Projekt używa **80/20** (test=6 000, train=24 000) w CREDIT-103, 105, 110, 111, 112. **Liczbowy
rozjazd niezaadresowany.**

### 4.4. class_weight / SMOTE / scale_pos_weight — DokumentRoznice §2.3 🔴

Sek. 4.1.2 (s. 26) **niezmieniona** — nadal opisuje:
- SMOTE testowany, Rysunek 4.2 (efekt SMOTE, brak pliku w `reports/`).
- Finalna decyzja: `class_weight="balanced"` (RF, LSTM), `scale_pos_weight` (XGB).
- Code snippets `compute_class_weight(...)`, `scale_pos_weight=(len(y) - sum(y)) / sum(y)`.

Projekt **NIE używa** class_weight ani scale_pos_weight w modelach W3 — operuje kalibracją izotoniczną
(CREDIT-105) + cost-opt thresholds (CREDIT-106). **Zasadniczy rozjazd metodologiczny pozostał.**

### 4.5. LSTM input shape (6, 3) — DokumentRoznice §2.1 🔴

Sek. 4.2.1 (s. 28) **niezmieniona** — nadal:
- „Wejście sieci ma wymiar **(6, 3)**: **sześć kroków czasowych** reprezentujących kolejne
  miesiące oraz trzy cechy na każdy krok"
- `model = Sequential([Input(shape=(6, 3)), LSTM(32), ...])`
- Code: `pay_seq_cols = ["PAY_6", "PAY_5", "PAY_4", "PAY_3", "PAY_2", "PAY_0"]` (6 mies.)
- `bill_seq_cols = ["BILL_AMT6", ..., "BILL_AMT1"]`
- `pay_amt_seq_cols = ["PAY_AMT6", ..., "PAY_AMT1"]`

Projekt używa **(3, 3)** od CREDIT-102 (W3 = 3 mies., najnowsze 3). **Rozjazd architektury LSTM
pozostał.**

### 4.6. Lista cech (6-mies. agregaty) — DokumentRoznice §4.1 🔴

Sek. 4.3.2 (s. 34) **niezmieniona** — nadal:
- „PAY_max reprezentuje najgorszy status płatności **w sześciomiesięcznym oknie**"
- „late_count zlicza, w ilu z **sześciu miesięcy** klient był w jakimkolwiek opóźnieniu"
- „BILL_trend (zmiana salda między **kwietniem a wrześniem**)"

Projekt liczy te same cechy ale na **3-miesięcznych oknach** (window-parametryzowane
`engineer_features(df, window)`). **Liczbowy rozjazd cech pozostał.**

### 4.7. Bug-fix utilization_rate / severe_late — DokumentRoznice §4.2 🔴

**v7:** brak wzmianki.

### 4.8. Cross-validation: schematyczne vs Optuna — DokumentRoznice §5.1 🔴

Sek. 4.4.1 + 4.5 **niezmienione** — nadal:
- „walidację krzyżową 5-fold zaprezentowano **schematycznie**, natomiast do właściwej oceny modeli
  przyjęto pojedynczy, stratyfikowany podział 70/30"
- Brak wzmianki Optuna / TPESampler.

Projekt zrobił prawdziwe 5-fold StratifiedKFold + Optuna 30 trials w CREDIT-108.

### 4.9. Grid Search XGBoost — DokumentRoznice §5.2 🔴

Sek. 4.4.1 **niezmieniona** — opis grid search heatmap (Rysunek 4.7) jako jedyne strojenie XGB.
Brak Optuna jako post-hoc weryfikacja.

### 4.10. Bootstrap 40-powtórzeń — DokumentRoznice §5.3 🔴

Sek. 4.5 **niezmieniona** — nadal: „raportowana w rozdziale 5 wariancja AUC, **obliczona na podstawie
40 bootstrapowanych powtórzeń** zbioru testowego". Projekt nie ma bootstrapu — **niezgodność
zostanie zauważona, jeśli Roz. 5 zostanie napisany bez 40-bootstrap'u**.

### 4.11. SHAP dla 4 modeli tree-based — DokumentRoznice §9 🔴

Sek. 4.4.2 (s. 38) **niezmieniona** — SHAP opisany tylko dla XGBoost. Projekt liczy SHAP dla 4
modeli tree-based (RF, XGB, LightGBM, CatBoost) per CREDIT-107.

### 4.12. Bibliografia poza [30][31] — bez zmian 🔴

Brak innych źródeł dla nowych technik (np. fairlearn paper, isotonic calibration paper Zadrozny &
Elkan). Mogą trafić do bibliografii w trakcie pisania Roz. 5.

### 4.13. Rysunki — DokumentRoznice §12 🔴

Spis rysunków v7 **identyczny** jak v6 — 14 rysunków (1.1-1.2, 2.1-2.3, 4.1-4.9). **Żaden nowy
rysunek nie został dodany.** Wszystkie problemy z §12 pozostają:
- Rys. 4.1 (podział train/val/test) — musi pokazywać 80/20.
- Rys. 4.2 (SMOTE) — odrzucone w projekcie, brak pliku.
- Rys. 4.3 (krzywe uczenia LSTM) — brak pliku.
- Rys. 4.4–4.9 — większość bez plików.
- **Brak** Rysunków dla: LightGBM, CatBoost, calibration curve, static-vs-dynamic, lead time,
  slope distribution, fairness selection rate, fairness TPR/FPR.

---

## 5. Zestawienie pełne — mapowanie każdego punktu z DokumentRoznice na status v7

| Sek. DokumentRoznice | Tytuł | Status w v7 | Notatka |
|---|---|---|---|
| §0 | Roz. 3 + Roz. 5 puste | 🔴 brak zmian | Nadal puste, krytyczne |
| §1.1 | Framing „dynamiczne" | 🟢 wdrożone | Wstęp przepisany |
| §1.2 | Hipotezy H1/H2/H3 | 🔴 brak (Roz. 3 pusty) | Drugie pytanie research dodane do Wstępu, ale formalnych hipotez brak |
| §2.1 | Sliding-window panel | 🟡 framing tak, technicznie nie | Wzmianki w Wstęp/1.4/2.2.2, ale tabela W0..W3 wymaga Roz. 3 |
| §2.2 | 70/30 vs 80/20 | 🔴 brak zmian | Sek. 4.1.1 niezmieniona |
| §2.3 | class_weight vs isotonic + cost | 🔴 brak zmian | Sek. 4.1.2 niezmieniona |
| §3 | 3 modele → 5 modeli | 🟢 wdrożone | Wstęp + Roz. 2.3.4/2.3.5 + [30]/[31] |
| §4.1 | Lista cech 6-mies. → 3-mies. | 🔴 brak zmian | Sek. 4.3.2 niezmieniona |
| §4.2 | Bug-fix utilization_rate/severe_late | 🔴 brak | Nie wzmiankowane |
| §5.1 | CV schematyczny → Optuna 5-fold | 🔴 brak zmian | Sek. 4.4.1 / 4.5 niezmienione |
| §5.2 | Grid Search XGB | 🔴 brak zmian | Sek. 4.4.1 niezmieniona |
| §5.3 | Bootstrap 40 — usunąć/dorobić | 🔴 brak zmian | Sek. 4.5 niezmieniona |
| §6 | Kalibracja izotoniczna | 🟡 zapowiedziana | Wstęp roadmap, brak sek. 4.6 w Roz. 4 |
| §7 | Static vs dynamic (dowód tezy) | 🟡 zapowiedziane | Drugie research question + roadmap, Roz. 5 pusty |
| §8 | Fairness audit | 🟡 zapowiedzione | Sek. 2.5 + roadmap, Roz. 5 pusty |
| §9 | SHAP 1 model → 4 modele | 🔴 brak zmian | Sek. 4.4.2 niezmieniona |
| §10 | Architektura systemu (Roz. 3.4) | 🔴 brak zmian | Roz. 3 pusty |
| §11 | Wyniki (Roz. 5) | 🔴 brak zmian | Roz. 5 pusty |
| §12 | Rysunki | 🔴 brak zmian | Spis rysunków identyczny |
| §13 P0 #1 | Hipotezy w Roz. 3.2 | 🔴 brak | Roz. 3 pusty |
| §13 P0 #2 | Roz. 3.3 + 3.4 (dane + architektura) | 🔴 brak | Roz. 3 pusty |
| §13 P0 #3 | Wstęp framing | 🟢 wdrożone | ✓ |
| §13 P0 #4 | Roz. 4 sek. 4.6/4.7/4.8 + aktualizacje 4.1/4.2 | 🔴 brak | Roz. 4 sek. 4.1/4.2 niezmienione, 4.6/4.7/4.8 nie dodane |
| §13 P0 #5 | Roz. 5 napisać od zera | 🔴 brak | Roz. 5 pusty |
| §13 P0 #6 | LightGBM + CatBoost | 🟢 wdrożone | ✓ (sek. 2.3.4/2.3.5) |
| §13 P1 #7–#12 | reframing 5.4, fairness 5.5b, SHAP 4 modele, Roz. 4.5 Optuna, rysunki, Roz. 3.6 | 🔴 brak | Wszystko otwarte |
| §13 P2 #13–#16 | imbalance dyskusja, Optuna post-hoc, bootstrap, bug-fix | 🔴 brak | Wszystko otwarte |

**Wynik liczbowy:**
- 🟢 Pełne: **3** punkty (framing, 5 modeli, biblio)
- 🟡 Częściowe (forward-reference, treści brak): **5** punktów (sliding-window, kalibracja, cost
  thresholds, static-vs-dynamic, fairness)
- 🔴 Brak: **~13** punktów (Roz. 3, Roz. 5, 80/20, class_weight, LSTM shape, cechy, bug-fix, CV,
  grid search, bootstrap, SHAP, rysunki, architektura)

---

## 6. Nowe niespójności wprowadzone przez v7

### 6.1. „Pięć klasyfikatorów" we Wstępie + Roz. 2 vs „LSTM, RF, XGBoost" w TOC Roz. 5

TOC sek. 5.2 (Wyniki modeli per model):
- 5.2.1 LSTM
- 5.2.2 Random Forest
- 5.2.3 XGBoost

TOC sek. 5.3: „Wzajemne porównanie modeli LSTM, Random Forest i XGBoost".

**Niespójność:** Wstęp + Roz. 2 mówią **5 modeli**, TOC Roz. 5 wymienia **3 modele**. Po napisaniu
Roz. 5 trzeba **zaktualizować TOC** (5.2 dorzucić 5.2.4 LightGBM + 5.2.5 CatBoost; 5.3 zmienić
tytuł na „...LSTM, Random Forest, XGBoost, LightGBM i CatBoost" lub „pięciu modeli").

### 6.2. „Drugi research question" we Wstępie ⇄ pusty Roz. 3.2 hipotezy

Wstęp v7 explicite formułuje drugie pytanie badawcze („czy kalendarzowe monitorowanie...
pozwala wykryć pogorszenie sytuacji dłużnika wcześniej niż pojedyncza ocena statyczna").
Roz. 3.2 (Hipotezy) jest pusty. **Drugie pytanie nie jest sformalizowane jako H2.**

### 6.3. „Audyt fairness" zapowiedziany w 2.5 + roadmap ⇄ brak treści

Sek. 2.5 wprost zapowiada: „w części empirycznej (...) dyskryminacja pośrednia (...) zostanie
skwantyfikowana, między innymi poprzez porównanie wskaźników selekcji oraz wyrównanych szans
pomiędzy grupami". Roz. 5.5 pusty ⇒ obietnica niedotrzymana w v7.

### 6.4. „Kalibrację prawdopodobieństw oraz wyznaczenie progów alertu" w roadmap ⇄ brak sek. 4.6/4.7

Roadmap w Wstępie: Roz. 4 dokumentuje „kalibrację prawdopodobieństw oraz wyznaczenie progów
alertu". Roz. 4 ma sekcje 4.1–4.5 — **żadnej z dwóch zapowiedzianych nie ma w treści.**

---

## 7. Priorytety dalszych prac (zaktualizowane po v7)

### P0 (przed v8) — KRYTYCZNE

1. **Napisać Roz. 3** w całości (kontent, nie tylko śródtytuły):
   - 3.1 Cel i zakres (rozszerzenie Wstępu).
   - 3.2 Hipotezy H1/H2/H3 (formalne sformułowanie).
   - 3.3 Dane (UCI + sliding-window — **TUTAJ tabela W0..W3**).
   - 3.4 Architektura systemu (React+.NET+Flask+Postgres — szczegółowo).
   - 3.5 Obsługa wyjątków.
   - 3.6 Narzędzia (tech stack + GitHub Flow + CI).

2. **Napisać Roz. 5** w całości na bazie CREDIT-114 (final report — Sprint 6):
   - 5.1 metryki (defining), 5.2 per-model wyniki (5 modeli), 5.3 porównanie 5 modeli.
   - 5.4 **static vs monitoring** (reframing!).
   - 5.5 + 5.5b interpretowalność (SHAP 4 modeli) **+ fairness audit**.
   - 5.6 dyskusja H1/H2/H3.

3. **Dodać do Roz. 4 trzy nowe sekcje:**
   - 4.6 Kalibracja izotoniczna (CREDIT-105).
   - 4.7 Cost-opt thresholds (CREDIT-106).
   - 4.8 Sliding-window pipeline (jeśli nie w Roz. 3.3).

4. **Zaktualizować Roz. 4 istniejące:**
   - 4.1.1: 80/20 (nie 70/30).
   - 4.1.2: nowe podejście do imbalance (kalibracja + progi, nie class_weight).
   - 4.2.1: LSTM (3, 3) (nie (6, 3)) — albo wprost wskazać dwie wersje (legacy 6-mies. testowane,
     finalna 3-mies. W3).
   - 4.3.2 / 4.4.2: cechy 3-miesięczne + SHAP dla 4 tree models.
   - 4.4.1: dodać Optuna 5-fold CV jako post-hoc weryfikację.
   - 4.5: usunąć obietnicę 40-bootstrap LUB dorobić bootstrap.

5. **Naprawić TOC sek. 5.2/5.3:** dodać LightGBM + CatBoost.

### P1 (paralelne z pisaniem)

6. **Dorobić rysunki** wg `DokumentRoznice §15`:
   - Rys. 4.1 (80/20 train/val/test).
   - Rys. 4.6 (RF top-20 features).
   - Globalny SHAP summary per model (4×).
   - Static-vs-dynamic ROC dla LightGBM + CatBoost (CSV → PNG).
   - Reliability diagram przed/po kalibracji.
   - Fairness PNG (już są: `fairness_selection_rate_w3.png`, `fairness_tpr_fpr_w3.png`).

### P2

7. Bibliografia: rozważyć dodanie [32] Zadrozny & Elkan (isotonic calibration), [33] fairlearn paper,
   [34] Bird et al. „Fairlearn: A toolkit for assessing and improving fairness in AI".

---

## 8. Wniosek

**v7 to dobry początek** — pokazuje, że framing tytułu i lista modeli zostały zaktualizowane zgodnie
z `DokumentRoznice §1.1` i §3. **Ale 80% pracy redakcyjnej pozostało.** Roz. 3 i Roz. 5 są wciąż
puste; Roz. 4 sek. 4.1–4.5 nie zostały zaktualizowane; obietnice (kalibracja, progi alertu, fairness)
zapowiedziane są w roadmapie, ale niezaspełnione w treści.

**Zalecana sekwencja v8:**
1. CREDIT-114 (Sprint 6 — final report) — domknięcie liczbowej bazy.
2. Roz. 3 (można pisać dziś, projekt strony technicznej gotowy).
3. Aktualizacja Roz. 4 (sek. 4.1, 4.2, dodanie 4.6/4.7/4.8).
4. Roz. 5 + Zakończenie (na bazie CREDIT-114).
5. Rysunki + naprawienie TOC sek. 5.2/5.3.

Po tym v8 powinno odpowiadać stanowi projektu **end-to-end**, jak to opisano w `DokumentRoznice §13`.
