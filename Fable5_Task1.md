# Fable5_Task1.md — Recenzja sceptyczna pracy magisterskiej (v8) + plan naprawczy

> **Autor recenzji:** Claude Fable 5 (rola: sceptyczny recenzent / członek komisji)
> **Data:** 2026-07-06
> **Przedmiot:** `Praca Magisterska-8.pdf` (47 stron) vs stan projektu w repo
> (`ml-learing-center/`, `ml-service/`, `reports/`, dokumenty sprintów)
> **Metoda:** pełna lektura PDF v8, diff tekstowy v7↔v8, weryfikacja
> `DokumentRoznice.md` / `WalidacjaPDFv7.md` przeciwko faktycznemu kodowi
> (`main.py`, `sliding_window.py`, `features.py`, `fairness_audit.py`,
> `evaluation.py`) i raportom (`metrics_w3.csv`, `fairness_metrics_w3.csv`,
> `static_vs_dynamic_report.md`, `lead_time_report.md`).

---

## 1. Werdykt ogólny

**Praca w wersji 8 nie nadaje się do złożenia ani obrony.** Diff tekstu v7→v8 to
wyłącznie typografia (zamiana półpauz „—" na dywizy „-" i przełamania wierszy;
114 zmienionych linii, wszystkie tego typu). Merytorycznie v8 = v7, więc cała
lista braków z `WalidacjaPDFv7.md` obowiązuje w 100%.

Stan strukturalny:

- **Rozdział 3** (metodologia badań + projekt systemu) — same nagłówki, zero treści.
- **Rozdział 5** (analiza wyników + weryfikacja hipotez) — same nagłówki, zero treści.
- **Zakończenie** — puste. **Spis tabel** — pusty (praca nie zawiera ani jednej tabeli).
- Teza pracy **nie jest nigdzie liczbowo udowodniona** — jedyne liczby to figury
  w rozdz. 4 dotyczące porzuconej wersji projektu (3 modele, okno 6-mies., split 70/30).

Trzy klasy problemów:

1. **Strukturalne** — brak rozdz. 3, 5 i zakończenia = brak metodologii i dowodu tezy.
2. **Dokumentacyjne** — rozdz. 4 opisuje porzucony pipeline i przeczy sam sobie
   (3 vs 5 modeli, 70/30 vs 60/20/20, LSTM (6,3) vs (3,3), grid search vs Optuna,
   bootstrap-widmo, zamienione podpisy figur).
3. **Merytoryczne (przetrwają nawet po dopisaniu rozdziałów)** — strojenie/progi
   dotknięte zbiorem testowym, SEX jako cecha wejściowa przy jednoczesnym audycie
   fairness po SEX, monitoring przegrywający ze statyką przy FA=10% dla wszystkich
   5 modeli, lead time o niejasnej genezie (dominacja okna W0).

Fundament teoretyczny (rozdz. 1–2) jest solidny, dobrze cytowany i do zachowania.

---

## 2. Tabela ustaleń (teza z pracy → kod → rozbieżność → waga → linia obrony)

| # | Teza z pracy | Co pokazuje kod/raporty | Rozbieżność | Waga | Jak odpowiadać na obronie |
|---|---|---|---|---|---|
| 1 | Wstęp: „pięć klasyfikatorów"; Rozdz. 4: „zaimplementowano **trzy** różne klasyfikatory"; spis treści rozdz. 5: 3 modele | Kod: 5 modeli W3 (RF, XGB, LightGBM, CatBoost, LSTM), serwowane end-to-end | Praca przeczy sama sobie w trzech miejscach | **Wysoka** | Nie do obrony — naprawić przed złożeniem. Awaryjnie: „rozdz. 4 opisuje pierwotny pipeline 3-modelowy; finalny system ma 5" |
| 2 | 4.1.1: podział 70/30 (test 9 000); rys. 4.1 pokazuje 56/14/30 | Finalny pipeline W3: **3-way split 60/20/20** (test 6 000, osobny split kalibracyjny); 70/30 tylko w legacy sekcji `main.py` | Praca dokumentuje porzucony pipeline; rys. 4.1 narysowany pod złe liczby | **Wysoka** | „Praca opisuje pipeline bazowy; finalny protokół to 60/20/20 z wydzielonym zbiorem kalibracyjnym" — wymaga wcześniejszej poprawki tekstu |
| 3 | 4.2.1: LSTM input `(6, 3)`; cechy liczone na 6 mies. | Finalny LSTM W3: `(3, 3)`; cechy na 3-mies. oknie (`engineer_features(df, window)`) | Architektura opisana ≠ wdrożona | **Wysoka** | „Wersja 6-mies. była baseline'em; finalna praca porównuje ją z W3 (H1: strata AUC < 1 pp)" |
| 4 | Wstęp: sliding-window i trajektoria PD to „właściwy przedmiot pracy" | `sliding_window.py` (W0..W3), `timeseries_eval.py`, `static_vs_dynamic.py` — rdzeń projektu | **Rdzeń tezy nieopisany technicznie** (miał być w pustym rozdz. 3) | **Wysoka** | Brak obrony — sekcja o konstrukcji okien W0..W3 musi powstać |
| 5 | Wstęp-roadmapa: „Rozdz. 4 dokumentuje … kalibrację prawdopodobieństw oraz wyznaczenie progów alertu" | Kalibracja izotoniczna (CREDIT-105) i progi kosztowe FN=5×FP (CREDIT-106) istnieją w kodzie | Rozdz. 4 kończy się na 4.5 — obiecanych sekcji nie ma | **Wysoka** | Dopisać 4.6/4.7; znać liczby: Brier −19/−24/−23%, progi 0.130–0.185 |
| 6 | 4.5: „wariancja AUC z 40 bootstrapowanych powtórzeń zbioru testowego" | **Bootstrap nie istnieje** — ani skrypt, ani raport | Obietnica bez pokrycia | **Wysoka** | Dorobić (~50 LoC) albo usunąć zdanie. Nie zostawiać |
| 7 | Rys. 4.5/4.7: heatmapy strojenia podpisane „**AUC (test)**", ramka = wybrana konfiguracja | 4.1.1 dwie strony wcześniej: test „zamrożony", wybór na teście = wyciek | **Praca dokumentuje strojenie hiperparametrów na zbiorze testowym**, łamiąc własną deklarację | **Wysoka** | Przerobić figury na CV-AUC (Optuna CREDIT-108 robi uczciwe 5-fold CV). Awaryjnie: „selekcja na CV, heatmapa testowa to ilustracja post-hoc" (słaba obrona) |
| 8 | 4.3.1: przyjęto `max_depth=10` | Heatmapa rys. 4.5: czerwona ramka na **max_depth=8** | Tekst i figura wskazują różne konfiguracje | Średnia | Poprawić figurę; kod używa depth=10, ramka jest błędna |
| 9 | 4.2.2: `batch_size=256`; tekst: „batch < 128 wprowadza szum" | Panel „Batch size" rys. 4.3: **max AUC przy najmniejszym batchu (~64–100)**, AUC spada z rosnącym batchem | Figura przeczy tekstowi i wybranej wartości | Średnia | Uzgodnić: pokazać, że różnice to 3. miejsce po przecinku (kompromis czas/jakość), albo zmienić opis |
| 10 | Podpisy rys. 4.3 („Krzywe uczenia") i 4.4 („Wpływ hiperparametrów") | Zawartość **zamieniona miejscami** | Błąd redakcyjny widoczny gołym okiem | Średnia | Zamienić podpisy |
| 11 | 4.4.1: strojenie XGB = grid search; „CV tylko schematycznie (rys. 4.9), zbyt kosztowna" | CREDIT-108: **prawdziwe 5-fold StratifiedKFold + Optuna 30 trials/model**; w repo **nie ma kodu grid search** | Praca opisuje strojenie, którego nie ma, i przemilcza to, które jest | Średnia | „Defaulty wybrano heurystycznie; Optuna zweryfikowała post-hoc (uplift < 0.5 pp, tuned nie promowane)" — dopisać do 4.4.1. Figury 4.5/4.7 mogą być **niereprodukowalne** |
| 12 | 4.1.2: finalna decyzja = `class_weight="balanced"` / `scale_pos_weight` | Kod W3 **faktycznie ich używa** we wszystkich 5 modelach — **`DokumentRoznice.md` §2.3 twierdzi błędnie, że nie!** | PDF zgodny z kodem; to dokument pomocniczy się myli. Ale tandem „ważenie klas + kalibracja izotoniczna" nie jest nigdzie uzasadniony | Średnia | **Nie usuwać 4.1.2** (wbrew DokumentRoznice). Odpowiedź: „ważenie poprawia ranking; deformację skali PD korygujemy kalibracją na osobnym splicie" |
| 13 | (planowany rozdz. 5) H2: „monitoring wcześniej wykrywa przy porównywalnej dyskryminacji" | `static_vs_dynamic_report.md`: przy FA=10% **statyka wygrywa dla WSZYSTKICH 5 modeli** (od −1.3 do −7.7 pp catch rate) | „Porównywalna dyskryminacja" = eufemizm dla „systematycznie gorsza przy kanonicznym budżecie FA" | **Wysoka** | Patrz pytanie Q2 (sekcja 3) — przeformułować H2 na wczesność + unikalne wykrycia, nie skuteczność |
| 14 | (planowany rozdz. 5) lead time ~2 okna jako dowód wczesnego ostrzegania | `lead_time_report.md`: rozkład pierwszego alertu RF: **W0=352, W1=101, W2=100, W3=108** — dominuje najstarsze okno | Lead time w dużej mierze artefakt statystyki pierwszego przekroczenia + podwyższonych PD na W0 (model trenowany na W3 aplikowany na dane W0 = przesunięcie rozkładu) | **Wysoka** | Przed obroną policzyć rozkład PD per okno osobno dla klas 0 i 1; bez tego jedno pytanie o histogram rozbija narrację |
| 15 | Progi alertu „produkcyjne" (CREDIT-106) | `main.py:406-413`: progi optymalizowane **na zbiorze testowym** (`y_te_w3`); fairness audit i ewaluacje używają **tego samego** zbioru | Wybór progu na teście = dokładnie wyciek, przed którym praca ostrzega w 4.1.1 | **Wysoka** | Najczystiej: przeliczyć progi na splicie kalibracyjnym. Awaryjnie: „metryki rankingowe (AUC/Gini/KS) są progoniezależne" — ale fairness i static-vs-dynamic są progowe |
| 16 | 4.3.2: „ograniczona waga zmiennych chronionych zmniejsza ryzyko dyskryminacji pośredniej" | `features.py`: **SEX (one-hot) jest cechą wejściową wszystkich modeli statycznych** | Praca mówi o dyskryminacji *pośredniej*, a model używa płci *bezpośrednio* | **Wysoka** | Patrz pytanie Q4 — najpoważniejszy zarzut prawno-metodologiczny |
| 17 | (planowany rozdz. 5) H3: fairness OK, \|DPD/EOD\| ≤ 0.04 | `fairness_metrics_w3.csv` potwierdza liczby | Audyt tylko po SEX; na progach dobranych na tym samym teście; interpretacja „DPD odzwierciedla base rate, nie bias" to **definicja disparate impact** | Średnia | Argumentować przez equalized odds (EOD ≤ 0.033), nie przez negowanie DPD; przyznać ograniczenie do jednego atrybutu |
| 18 | (planowany rozdz. 5) porównanie 5 modeli | `metrics_w3.csv`: CatBoost 0.780, XGB 0.776, LGBM 0.776, RF 0.774, **LSTM 0.761 — ostatni** | Model będący „głównym nośnikiem dynamicznego ujęcia" ma najgorsze AUC i Briera | **Wysoka** | Patrz pytanie Q5 — sprzedać jako ustalenie zgodne z literaturą (drzewa > sieci na danych tabelarycznych) |
| 19 | `DokumentRoznice.md` H1: „RF 0.7779 vs 0.7792" | `metrics_w3.csv`: RF 0.7741 | Liczby w dokumentach pomocniczych z innych runów niż aktualne raporty | Niska | Ujednolicić przed pisaniem rozdz. 5 |
| 20 | Sekcja 2.3.4 (LightGBM) | — | Rozjechane formatowanie: inne wyrównanie, nagłówek „2.4" pojawia się na stronie **przed** 2.3.5 — ślad pospiesznego wklejania | Niska | Poprawić skład |
| 21 | Cały eksperyment | Jeden dataset (UCI 2005, Tajwan), jeden podział, brak testów istotności; różnice AUC między modelami ~0.002–0.006 | Ranking modeli może być szumem pojedynczego splitu | Średnia | Dorobić bootstrap CI (i tak obiecany — #6); różnice opisywać jako „porównywalne" |
| 22 | „Kalendarzowe monitorowanie ekspozycji" | Okna W0..W3 = **retrospektywne pocięcie tej samej 6-mies. historii jednego wiersza UCI**; wszystkie 4 okna przewidują tę samą październikową etykietę; nakładanie 2/3 | To symulacja monitoringu, nie monitoring; W0 przewiduje default z 4-mies. wyprzedzeniem, W3 z 1-mies. — **różne horyzonty predykcji** nierozdzielone w analizie | **Wysoka** | Patrz pytanie Q3 — opisać jako świadome ograniczenie w rozdz. 3 |

### Wątpliwości dodatkowe (mniejsze, zgłaszam wszystkie)

- **`DokumentRoznice.md` §2.3 zawiera błąd faktograficzny** — twierdzi, że finalne
  modele W3 nie używają class_weight/scale_pos_weight; kod używa ich we wszystkich
  pięciu. Poprawianie pracy według tego punktu popsułoby ją.
- Figury 4.1–4.9 nie mają plików źródłowych w `reports/` ani skryptów generujących
  w repo — pytanie o reprodukowalność którejkolwiek z nich jest zasadne.
- `evaluation.py` liczy confusion matrix przy progu 0.5, choć progi „produkcyjne"
  to 0.130–0.185 — macierze pomyłek nie odpowiadają faktycznej regule decyzyjnej.
- F1/precision/recall zapowiedziane w 4.5 i strukturze 5.1.1 nie są liczone nigdzie
  (`metrics_w3.csv` ma tylko AUC/Gini/KS/Brier).
- CREDIT-113 (stacking) i CREDIT-114 (final report) wciąż otwarte — baza liczbowa
  rozdz. 5 formalnie nie istnieje.
- Bibliografia nie zawiera źródeł dla faktycznie użytych metod: kalibracja
  izotoniczna (Zadrozny & Elkan), fairlearn (Bird et al.), Optuna (Akiba et al.).
- Rys. 2.3 podpisany „Źródło: [28], [29]" — dwa oddzielne SVG z Wikimedia sklejone
  w jedno „zestawienie"; formalnie OK, ale komisja lubi pytać o źródła grafik.

---

## 3. Pięć najtrudniejszych pytań komisji + sugerowane odpowiedzi

### Q1. Strojenie na zbiorze testowym

> „Na rysunkach 4.5 i 4.7 stroi Pan hiperparametry po AUC *testowym*, a dwie strony
> wcześniej deklaruje Pan, że zbiór testowy jest zamrożony i że wybór czegokolwiek
> na jego podstawie to wyciek informacji. Które metryki w tej pracy są wiarygodne?"

**Odpowiedź:** przyznać wprost, że pierwotne heatmapy raportowały metrykę testową
i że to błąd prezentacji, po czym przenieść ciężar na to, co czyste: „Finalna
selekcja hiperparametrów została zweryfikowana niezależnie 5-krotną walidacją
krzyżową z Optuną (30 prób na model); różnica między konfiguracją domyślną
a strojoną wyniosła poniżej 0.5 pp AUC, co pokazuje płaskość powierzchni
hiperparametrów — wybór w obrębie tego plateau nie zawyża istotnie wyniku
testowego. Ostateczne wnioski opierają się na metrykach rankingowych liczonych
raz, na końcu, na nietkniętym splicie."
*Warunek: przed obroną przerobić figury na CV-AUC albo jawnie opisać je jako
ilustrację post-hoc.*

### Q2. Monitoring przegrywa ze statyką

> „Pana własny raport pokazuje, że przy budżecie fałszywych alarmów 10% reguła
> statyczna wygrywa z monitoringiem dla wszystkich pięciu modeli, do −7.7 pp.
> Jak Pan broni tezy, że dynamiczne monitorowanie jest lepsze?"

**Odpowiedź:** nie bronić wyższości catch rate — przeformułować kryterium:
„Teza nie brzmi »monitoring dominuje w każdej metryce«, lecz »monitoring wnosi
wartość niedostępną dla oceny statycznej«. Empirycznie: (a) monitoring wykrywa
36–72 defaultujących na model, których reguła statyczna nie wykrywa w ogóle,
(b) wśród wykrytych alarm pada średnio 2 okna wcześniej, co w praktyce bankowej
oznacza czas na działania miękkie (restrukturyzacja, obniżenie limitu), których
wartość nie jest ujęta w catch rate, (c) spadek catch rate przy stałym budżecie
FA to znany koszt agregatora max() po skorelowanych oknach — pokazuję go uczciwie
zamiast dobierać korzystny punkt pracy. Wniosek: reguła monitorująca jest
komplementarna, nie substytucyjna."
*Warunek: rozdz. 5 musi dokładnie tak stawiać H2 (wczesność + unikalne wykrycia,
nie skuteczność), zanim komisja przeczyta liczby.*

### Q3. Symulacja monitoringu vs zmiana horyzontu predykcji

> „Wszystkie cztery okna przewidują tę samą etykietę z października. Okno W0 to
> predykcja na 4 miesiące naprzód, W3 na miesiąc. Czym Pana »monitoring
> kalendarzowy« różni się od zwykłej zmiany horyzontu predykcji? I czy średni
> lead time ~2 okna nie jest artefaktem tego, że model trenowany na W3
> systematycznie zawyża PD na starszych oknach?"

**Odpowiedź:** uprzedzić to pytanie w rozdz. 3 jako świadome ograniczenie:
„Zbiór UCI jest przekrojowy — nie zawiera prawdziwego panelu podłużnego, więc
monitoring kalendarzowy symuluję przesuwanym oknem w obrębie dostępnej
6-miesięcznej historii. Okna różnią się horyzontem względem etykiety; dlatego
interpretuję trajektorię jako przybliżenie scenariusza produkcyjnego, a nie jego
pełną replikę, i wskazuję walidację na danych panelowych jako kierunek dalszych
badań."
*Warunek: przed obroną policzyć rozkład PD per okno osobno dla klas 0 i 1 —
jeśli PD rośnie na W0 także dla niedefaultujących, dominacja W0 w histogramie
lead time (352 z 661 wykryć RF) to przesunięcie rozkładu i lepiej wiedzieć to
pierwszemu.*

### Q4. SEX jako cecha wejściowa + audyt fairness

> „Modele dostają płeć jako cechę wejściową, a potem audytuje Pan fairness
> względem płci i pisze, że dodatnie DPD »to nie bias, tylko base rate«.
> Po pierwsze: dlaczego zmienna chroniona w ogóle jest w modelu — to dyskryminacja
> bezpośrednia, nie pośrednia. Po drugie: disparate impact z definicji nie pyta
> o base rate."

**Odpowiedź (warstwowo):** „(1) UCI zawiera SEX i celem badawczym było
skwantyfikowanie jego wpływu, a nie zbudowanie systemu produkcyjnego —
we wdrożeniu zmienna zostałaby usunięta zgodnie z praktyką i orzecznictwem UE;
(2) audyt pokazuje, że nawet przy jawnej obecności SEX modele spełniają equalized
odds z marginesem (EOD ≤ 0.033), co jest silniejszym wynikiem niż audyt modelu
»ślepego na płeć«, w którym płeć i tak wycieka przez korelaty; (3) zgadzam się,
że demographic parity nie uwzględnia base rate — dlatego raportuję obie metryki
i wnioskuję z EOD (równość błędów), a DPD interpretuję opisowo."
*Najlepsze wzmocnienie: dotrenować wariant bez SEX i pokazać, że DPD/EOD prawie
się nie zmieniają — zamyka temat jednym slajdem. Linia z `PodsumowanieSprintu5`
(„modele trafnie odzwierciedlają strukturę danych") na obronie by nie przetrwała.*

### Q5. LSTM najsłabszy z piątki

> „LSTM — który w pracy nazywa Pan głównym nośnikiem ujęcia dynamicznego — ma
> najgorsze AUC i najgorszy Brier z całej piątki. Sekwencja ma 3 kroki czasowe.
> Po co sieć rekurencyjna na trzech krokach i co z tego wynika dla tezy pracy?"

**Odpowiedź:** nie ratować LSTM — sprzedać wynik jako ustalenie: „To jeden
z głównych wyników empirycznych pracy: na tabelarycznych danych kredytowych
o krótkiej historii metody zespołowe na drzewach pozostają nie do pobicia,
zgodnie z literaturą benchmarkową [10], [11]. Różnica jest jednak mała
(0.761 vs 0.780), a LSTM wnosi dwie unikalne własności: brak ręcznej inżynierii
cech (surowy tensor 3×3) oraz najbliższy parytet w audycie fairness (DPD 0.007).
Kluczowe jest rozdzielenie pojęć: dynamika w tej pracy to przede wszystkim
*schemat oceny* (trajektoria W0..W3), który działa z każdym z pięciu modeli,
a nie architektura LSTM."
*Warunek: osłabić w 4.2 sformułowanie „główny nośnik dynamicznego ujęcia" —
obecny tekst wiąże tezę z najsłabszym modelem.*

---

## 4. Lista błędów do poprawy + prompty dla Opusa 4.8

Każdy punkt = jeden błąd + gotowy prompt do wklejenia w Claude Code (model:
Opus 4.8) w katalogu repo. Prompty zakładają, że tekst pracy jest edytowany
w źródle (np. DOCX/Google Docs) — tam, gdzie zmiana dotyczy wyłącznie tekstu
pracy, prompt każe wygenerować gotowy tekst do wklejenia; tam, gdzie trzeba
dorobić kod/wykresy — pracuje w repo.

**Kolejność wykonywania: E1 → E2 → B1..B4 → E3..E10 → R1..R3.**
(Najpierw treść nośna — rozdz. 3 i 5; równolegle kod; na końcu spójność i skład.)

### P0 — blokujące złożenie pracy

**E1. Napisać Rozdział 3 od zera (metodologia + architektura + sliding-window)**

```text
Napisz kompletny Rozdział 3 mojej pracy magisterskiej „Metodologia badań i projekt
systemu" (sekcje 3.1–3.6) po polsku, w stylu akademickim zgodnym z rozdz. 1–2
z pliku „Praca Magisterska-8.pdf" (przeczytaj go najpierw, żeby przejąć styl,
terminologię i sposób cytowania [n]).

Wymagana zawartość per sekcja:
- 3.1 Cel i zakres badań — rozszerzenie Wstępu: porównanie ujęcia statycznego
  (W3) i dynamicznego (monitoring trajektorii W0..W3) na 5 klasyfikatorach.
- 3.2 Hipotezy badawcze — sformalizuj DOKŁADNIE trzy hipotezy:
  H1: sliding-window 3-mies. (W3) zachowuje AUC blisko okna 6-mies. (strata < 1 pp);
  H2: monitoring W0..W3 oferuje wcześniejszą detekcję pogorszenia sytuacji dłużnika
  oraz wykrycia niedostępne regule statycznej, przy porównywalnej dyskryminacji;
  H3: modele zachowują parytet względem atrybutu chronionego SEX (|DPD|, |EOD| ≤ 0.10).
  UWAGA do H2: sformułuj ją ostrożnie wokół WCZESNOŚCI i UNIKALNYCH WYKRYĆ, nie
  wokół wyższego catch rate — raport reports/static_vs_dynamic_report.md pokazuje,
  że przy FA=10% statyka wygrywa dla wszystkich 5 modeli.
- 3.3 Dane — UCI „default of credit card clients" (30 000 rekordów, 78/22),
  opis 23 zmiennych, mapowanie kolumn na miesiące (PAY_0=wrzesień … PAY_6=kwiecień,
  PAY_1 nie istnieje), preprocessing. NOWA PODSEKCJA 3.3.4 „Konstrukcja panelu
  sliding-window": tabela 4 okien W0..W3 dokładnie wg ml-learing-center/sliding_window.py
  (przeczytaj plik), uzasadnienie treningu na W3 (zgodność z etykietą październikową),
  zasada „nie fabrykujemy danych" (każde okno to realny wycinek historii), oraz
  UCZCIWY akapit o ograniczeniu: okna nakładają się w 2/3, wszystkie przewidują
  tę samą etykietę (różne horyzonty predykcji), a monitoring jest symulowany
  retrospektywnie na zbiorze przekrojowym, nie na prawdziwym panelu podłużnym.
- 3.4 Architektura systemu — opisz na podstawie: docs/api-contracts/monitoring.md,
  DokumentRoznice.md §10 (diagram ASCII), CLAUDE.md. React 19+Vite (5173) → .NET 8
  (5120, MonitoringController, walidacja, EF Core) → Flask (5001, 5 modeli W3 +
  scalery + alert_thresholds.json + SHAP) → PostgreSQL 16.
- 3.5 Obsługa wyjątków — mapowanie błędów Flask↔.NET (400/409/502/503, ErrorEnvelope).
- 3.6 Narzędzia — tech stack + GitHub Flow z PR-review i CI + struktura zadań
  CREDIT-XXX w 6 sprintach.

Liczby weryfikuj wyłącznie w kodzie i raportach repo (ml-learing-center/,
reports/, PodsumowanieSprintu*.md) — NIE ufaj DokumentRoznice.md §2.3 (zawiera
błąd: modele W3 UŻYWAJĄ class_weight/scale_pos_weight — sprawdź main.py:246-333).
Wynik zapisz jako docs/thesis/Rozdzial3.md z zaznaczeniem miejsc na rysunki
(np. [RYS: diagram architektury]).
```

**E2. Napisać Rozdział 5 od zera (wyniki + weryfikacja hipotez) + Zakończenie**

```text
Napisz kompletny Rozdział 5 „Analiza wyników i ocena modeli" (sekcje 5.1–5.6)
oraz Zakończenie mojej pracy magisterskiej, po polsku, styl jak w rozdz. 1–2
„Praca Magisterska-8.pdf" (przeczytaj PDF). Wszystkie liczby bierz WYŁĄCZNIE
z plików repo — przeczytaj: reports/metrics_w3.csv, reports/fairness_metrics_w3.csv,
reports/fairness_report.md, reports/static_vs_dynamic_report.md,
reports/lead_time_report.md, reports/optuna_study.md, PodsumowanieSprintu{3,4,5}_GF.md.

Struktura:
- 5.1 Metryki: definicje AUC-ROC, Gini, KS, Brier + uzasadnienie, dlaczego Brier
  i metryki progoniezależne > accuracy/F1 przy niezbalansowaniu 78/22.
- 5.2 Wyniki per model — PIĘĆ podsekcji (LSTM, RF, XGBoost, LightGBM, CatBoost),
  każda z liczbami z metrics_w3.csv (AUC/Gini/KS/Brier) + efekt kalibracji.
- 5.3 Porównanie 5 modeli — tabela 5×4 z metrics_w3.csv; CatBoost najlepszy
  (AUC 0.7802), LSTM najsłabszy (0.7610); zinterpretuj zgodnie z literaturą
  benchmarkową [10][11] (drzewa > sieci na danych tabelarycznych); różnice
  0.002–0.006 AUC opisuj jako „porównywalne" (jeden split, bez testu istotności —
  chyba że do tego czasu powstanie bootstrap z zadania B3, wtedy podaj CI).
- 5.4 PRZEFORMUŁOWANA: „Reguła statyczna (W3) vs reguła monitorująca (W0..W3)" —
  to jest dowód tezy. Przedstaw UCZCIWIE dane ze static_vs_dynamic_report.md:
  przy FA=10% statyka wygrywa u wszystkich 5 modeli (−1.3 do −7.7 pp catch),
  ale monitoring daje 36–72 unikalnych wykryć per model i średni lead time ~2 okna.
  Wniosek: komplementarność, wartość = wczesność, nie wyższy catch rate.
  Dodaj akapit o ograniczeniu: dominacja pierwszych alertów w oknie W0
  (lead_time_report.md) może częściowo wynikać z przesunięcia rozkładu
  (model trenowany na W3 aplikowany do W0), nie tylko z narastania ryzyka.
- 5.5 Interpretowalność (SHAP dla 4 modeli drzewiastych per CREDIT-107, zbieżność
  rankingu cech z feature importance RF) + 5.5b Audyt fairness: definicje DPD/EOD
  (fairlearn), tabela 5 modeli z fairness_metrics_w3.csv, binaryzacja przy progach
  kosztowych, wnioskowanie PRZEZ EOD (≤0.033), DPD opisowo; ogranicz. do SEX.
- 5.6 Dyskusja — literalna weryfikacja H1/H2/H3 z rozdz. 3.2: H1 potwierdzona,
  H2 potwierdzona CZĘŚCIOWO (wczesność tak, catch rate przy FA=10% nie — napisz
  to wprost), H3 potwierdzona. Ograniczenia: jeden zbiór, symulowany monitoring,
  SEX jako cecha wejściowa, progi optymalizowane na teście (jeśli do tego czasu
  nie wykonano zadania B2).
- Zakończenie: synteza + kierunki (dane panelowe, mitigacja fairness, stacking).

Wynik zapisz jako docs/thesis/Rozdzial5.md z miejscami na rysunki wskazującymi
konkretne pliki PNG z reports/ (np. [RYS: reports/roc_comparison_w3.png]).
```

### P0 — kod/eksperymenty do dorobienia PRZED pisaniem rozdz. 5

**B1. Diagnoza rozkładu PD per okno (amunicja na pytanie Q3)**

```text
W ml-learing-center/ napisz skrypt diagnostic_pd_per_window.py: załaduj 5
skalibrowanych modeli W3 (jak w fairness_audit.py — skopiuj stamtąd logikę
load_test_split), policz PD dla każdego z okien W0..W3 (WINDOW_DEFS z
sliding_window.py; UWAGA: scaler_w3 i features_w3 były fitowane na W3 —
transformuj cechy każdego okna tym samym scalerem, tak jak robi to inferencja
w ml-service/app.py) na zbiorze testowym (test_size=0.2, random_state=42,
stratify=y). Dla każdego modelu i okna raportuj średnie/mediany PD OSOBNO dla
y=0 i y=1 oraz odsetek przekroczeń progu z alert_thresholds.json. Wyjście:
reports/pd_per_window_diagnostic.csv + reports/pd_per_window_{model}.png
(boxploty per okno, rozdzielone klasy) + reports/pd_per_window_report.md
z wnioskiem: czy podwyższone PD na W0 dotyczy obu klas (przesunięcie rozkładu),
czy tylko defaultujących (realne narastanie ryzyka). Nie zmieniaj istniejących
artefaktów modeli.
```

**B2. Usunięcie wycieku: progi kosztowe liczone na splicie kalibracyjnym**

```text
W ml-learing-center/main.py sekcja CREDIT-106 optymalizuje progi alertu na
zbiorze TESTOWYM (_y_te_arr = y_te_w3) — to wyciek: te same dane służą potem do
ewaluacji, fairness auditu i porównania static-vs-dynamic. Przenieś optymalizację
progów na split kalibracyjny (X_cal_w3/y_cal_w3 dla modeli statycznych,
Xs_cal_w3/ys_cal_w3 dla LSTM — te same, na których fitowana jest kalibracja
izotoniczna; to akceptowalny kompromis, odnotuj go w komentarzu). Po zmianie:
przetrenuj pipeline (python main.py), zregeneruj alert_thresholds.json, uruchom
ponownie fairness_audit.py, timeseries_eval.py i static_vs_dynamic.py, i wypisz
tabelę porównawczą starych i nowych progów oraz starych i nowych DPD/EOD.
Jeśli wyniki zmieniają się kosmetycznie (oczekiwane), zanotuj to w
reports/threshold_leakage_fix.md — to będzie argument na obronę, że wyciek nie
zawyżył wniosków.
```

**B3. Bootstrap 40 powtórzeń (dotrzymanie obietnicy z sekcji 4.5)**

```text
W ml-learing-center/ napisz skrypt bootstrap_auc.py: załaduj predykcje 5
skalibrowanych modeli W3 na zbiorze testowym (reużyj load_test_split z
fairness_audit.py), wykonaj 40 bootstrapowych repróbkowań zbioru testowego
(ze zwracaniem, seed=42) i policz AUC per model per powtórzenie. Wyjście:
reports/bootstrap_auc_w3.csv (40 wierszy × 5 modeli), reports/bootstrap_auc_report.md
ze średnią, odchyleniem std i 95% CI percentylowym per model oraz wnioskiem,
które różnice między modelami mieszczą się w CI (spodziewane: CatBoost > LSTM
istotne, różnice XGB/LGBM/RF w szumie). Dodaj boxplot reports/bootstrap_auc_w3.png.
```

**B4. Kontr-eksperyment fairness: modele bez SEX (amunicja na pytanie Q4)**

```text
W ml-learing-center/ napisz skrypt fairness_no_sex.py: powtórz protokół z
main.py (W3, split 60/20/20, random_state=42, kalibracja izotoniczna) dla
WARIANTU cech bez SEX — zmodyfikuj listę cech tak, by wykluczyć kolumny
SEX_* (zostaw EDUCATION/MARRIAGE), przetrenuj RF, XGBoost, LightGBM i CatBoost
(LSTM pomiń — jego tensor (3,3) i tak nie zawiera SEX), policz AUC/Brier oraz
DPD/EOD po SEX (logika z fairness_audit.py; SEX bierzemy z danych do slicingu,
nie do modelu) przy progach kosztowych liczonych tym samym protokołem co
CREDIT-106. NICZEGO nie nadpisuj — nowe artefakty tylko do reports/:
fairness_no_sex_metrics.csv + fairness_no_sex_report.md z tabelą porównawczą
(z SEX vs bez SEX: AUC, DPD, EOD per model) i wnioskiem, czy usunięcie zmiennej
chronionej zmienia parytet (oczekiwanie: minimalnie, bo sygnał wycieka przez
korelaty — to teza do obrony).
```

### P1 — aktualizacja Rozdziału 4 (tekst)

**E3. Rozdział 4 — przepisanie sekcji 4.1 i intro (3→5 modeli, 60/20/20)**

```text
Przygotuj poprawki do Rozdziału 4 pracy „Praca Magisterska-8.pdf" (przeczytaj
najpierw strony 26–40 PDF i ml-learing-center/main.py). Wygeneruj gotowy tekst
zamienny po polsku (docs/thesis/Rozdzial4_poprawki.md), zachowując styl pracy:

1. Intro rozdz. 4: zamień „zaimplementowano trzy różne klasyfikatory" na opis
   PIĘCIU (RF + XGBoost/LightGBM/CatBoost jako statyczne + LSTM jako sekwencyjny),
   spójnie ze Wstępem i rozdz. 2.3.
2. Sekcja 4.1.1: zastąp podział 70/30 (test 9 000) FAKTYCZNYM protokołem finalnym
   z main.py:238-243 — 3-way split 60/20/20 (train/calib/test; test 6 000,
   random_state=42, stratify=y), z uzasadnieniem: zbiór kalibracyjny jest
   potrzebny, żeby kalibrator izotoniczny nie widział danych treningowych.
   Możesz zachować akapit o 70/30 jako opis wcześniejszego pipeline'u bazowego,
   wyraźnie oznaczony jako historyczny.
3. Sekcja 4.1.2: ZACHOWAJ opis class_weight/scale_pos_weight (kod ich używa —
   main.py:246-333), ale dopisz akapit uzasadniający tandem z kalibracją:
   ważenie klas poprawia ranking, lecz deformuje skalę prawdopodobieństw;
   deformację koryguje kalibracja izotoniczna na osobnym splicie (sekcja 4.6).
4. Sekcja 4.2.1: zmień opis LSTM z (6,3) na dwie wersje: baseline 6-mies. (6,3)
   oraz finalny W3 (3,3) zgodny z features.py:prepare_lstm_sequences; analogicznie
   opisy cech w 4.3.2 z „sześciomiesięcznego okna" na „okna 3-miesięcznego W3"
   (parametryzacja engineer_features(df, window)).
5. Osłab w 4.2 sformułowanie „LSTM jest głównym nośnikiem dynamicznego ujęcia" —
   dynamika = przede wszystkim schemat oceny W0..W3 działający z każdym modelem.
```

**E4. Rozdział 4 — nowe sekcje 4.6 (kalibracja), 4.7 (progi), 4.8 (LightGBM/CatBoost impl.)**

```text
Napisz trzy nowe sekcje Rozdziału 4 pracy magisterskiej po polsku (styl jak
rozdz. 4 w „Praca Magisterska-8.pdf"), na podstawie kodu ml-learing-center/main.py
(sekcje CREDIT-105/106/109) i PodsumowanieSprintu{2,3,4}_GF.md:

- 4.6 „Kalibracja prawdopodobieństw (regresja izotoniczna)": motywacja (trajektoria
  PD W0..W3 ma sens tylko przy skalibrowanych wartościach bezwzględnych),
  CalibratedClassifierCV(FrozenEstimator(base), method='isotonic') dla 4 modeli
  drzewiastych + IsotonicRegression na surowym wyjściu LSTM, 3-way split,
  wyniki Brier przed/po (weź z PodsumowanieSprintu-ów lub przelicz), dlaczego
  isotonic a nie Platt.
- 4.7 „Progi alertu optymalne kosztowo": model kosztu FN=5×FP, przeszukanie
  [0.1, 0.9] co 0.005, wynikowe progi per model z ml-service/alert_thresholds.json
  (0.130–0.185), interpretacja niskich progów przez asymetrię kosztów,
  plik alert_thresholds.json jako artefakt produkcyjny. Jeśli wykonano już fix
  wycieku (zadanie B2) — opisz progi liczone na splicie kalibracyjnym.
- 4.8 „Implementacja LightGBM i CatBoost": hiperparametry z main.py:277-301,
  wspólny protokół treningu/kalibracji z RF/XGB, nawiązanie do sekcji
  teoretycznych 2.3.4/2.3.5.

Dodatkowo zamień w 4.4.1 opis „CV tylko schematycznie" na akapit o faktycznym
strojeniu Optuna (TPESampler, 30 prób/model, 5-fold StratifiedKFold — dane
z reports/optuna_study.md): defaulty wybrane heurystycznie, Optuna potwierdziła
bliskość optimum (uplift < 0.5 pp), tuned modele świadomie nie promowane.
W 4.5 zamień obietnicę „40 bootstrapowanych powtórzeń" na odwołanie do faktycznego
bootstrapu z reports/bootstrap_auc_report.md (po wykonaniu zadania B3) — albo,
jeśli B3 nie zostało wykonane, usuń zdanie o bootstrapie.
Wynik: docs/thesis/Rozdzial4_nowe_sekcje.md.
```

**E5. Rozdział 4 — rozszerzenie SHAP na 4 modele (sekcja 4.4.2)**

```text
Zaktualizuj tekst sekcji 4.4.2 pracy (SHAP): obecnie opisuje wyłącznie XGBoost.
Przeczytaj ml-service/app.py (funkcja compute_shap_top_features, _unwrap_calibrated)
i PodsumowanieSprintu3_GF.md (CREDIT-107). Dopisz po polsku: SHAP liczony dla
4 modeli drzewiastych (RF/XGB/LightGBM/CatBoost) per predykcja (top-5 cech,
konwencja znaku: wartość > 0 pcha PD w górę), TreeExplainer na modelu bazowym
wyciąganym z CalibratedClassifierCV (kalibracja monotoniczna nie zmienia rankingu
cech — uzasadnij), LSTM pominięty (TreeExplainer nie dotyczy, KernelExplainer
przekracza budżet czasowy 2 s), zgodność rankingów między modelami. Wynik:
docs/thesis/Rozdzial4_shap_poprawka.md.
```

### P1 — figury

**R1. Naprawa figur rozdziału 4**

```text
W ml-learing-center/ stwórz skrypt thesis_figures/generate_ch4_figures.py
odtwarzający figury rozdz. 4 pracy w wersji zgodnej z finalnym pipeline'em W3
(styl matplotlib jak istniejące PNG w reports/):
1. fig_4_1_split.png — podział 60/20/20 (train/calib/test; 18000/6000/6000),
   pierścień + pasek proporcji (zamiast błędnego 56/14/30).
2. fig_4_5_rf_heatmap.png i fig_4_7_xgb_heatmap.png — heatmapy n_estimators×max_depth
   (RF) i learning_rate×max_depth (XGB) liczone po 5-fold CV-AUC NA ZBIORZE
   TRENINGOWYM W3 (nie na teście!), z ramką na konfiguracji faktycznie użytej
   w main.py (RF: 500/10, XGB: 0.02/4). To kosztowne obliczeniowo — ogranicz
   siatkę do 5×5 i wypisz czas.
3. fig_4_3_lstm_curves.png — krzywe uczenia LSTM W3 (retrain z zapisem history;
   accuracy + loss, train/val).
4. fig_4_6_rf_importance.png — top-20 feature importance RF W3 (nazwy cech
   z features_w3.pkl).
5. fig_4_8_shap_summary.png — beeswarm + bar SHAP dla XGBoost W3 na próbce 1000
   z testu (shap.TreeExplainer na modelu bazowym z _unwrap_calibrated jak w
   ml-service/app.py).
Zapisuj do ml-learing-center/thesis_figures/. Nie nadpisuj niczego w reports/.
Na końcu wypisz mapę: numer figury w pracy → plik → co się zmieniło vs wersja w PDF
(w tym: poprawiona ramka max_depth=10 na heatmapie RF, zamienione podpisy 4.3/4.4).
```

**R2. Brakujące figury static-vs-dynamic + fairness do rozdz. 5**

```text
Sprawdź w ml-learing-center/reports/, które PNG potrzebne do rozdz. 5 istnieją:
roc_comparison_w3.png, pr_comparison_w3.png, calibration_comparison_w3.png,
static_vs_dynamic_{random_forest,xgboost,lightgbm,catboost,lstm}_w3.png,
slope_boxplot_*_w3.png, trajectory_examples_*_w3.png, fairness_*.png.
Dorób brakujące: histogram lead time per model (dane z logiki timeseries_eval.py)
oraz — po wykonaniu zadania B1 — wykresy pd_per_window. Wypisz finalną listę
plik→sekcja rozdz. 5, do wykorzystania przy składzie.
```

### P2 — spójność i skład

**E6. Spis treści i nagłówki — usunięcie sprzeczności 3 vs 5 modeli**

```text
Wypisz kompletną listę poprawek redakcyjnych do „Praca Magisterska-8.pdf"
dotyczących spójności liczby modeli (przeczytaj PDF): (1) TOC 5.2 — dodać
podsekcje 5.2.4 LightGBM i 5.2.5 CatBoost; (2) TOC/nagłówek 5.3 — zmienić
„modeli LSTM, Random Forest i XGBoost" na „pięciu badanych modeli"; (3) intro
rozdz. 4 — trzy → pięć klasyfikatorów; (4) podsumowanie sekcji 4.5 („trzy
modele...") — pięć; (5) sekcja 2.1.1 — sprawdź frazę „trzy badane algorytmy"
i zamień na „pięć badanych algorytmów"; (6) naprawić kolejność nagłówków na
stronie z 2.3.4/2.3.5 (nagłówek „2.4" pojawia się przed 2.3.5) i wyrównać
formatowanie sekcji 2.3.4 do reszty tekstu; (7) podpisy rys. 4.3 i 4.4 —
zamienione miejscami; (8) TOC strony rozdz. 3 (wszystkie „23") — odświeżyć po
napisaniu rozdziału. Wynik: docs/thesis/poprawki_redakcyjne.md jako checklista.
```

**E7. Bibliografia — uzupełnienie źródeł faktycznie użytych metod**

```text
Przygotuj wpisy bibliograficzne (format identyczny jak [1]–[31] w „Praca
Magisterska-8.pdf" — przeczytaj wzorzec) dla: (1) Zadrozny B., Elkan C.,
„Transforming classifier scores into accurate multiclass probability estimates",
KDD 2002 (kalibracja izotoniczna); (2) Bird S. i in., „Fairlearn: A toolkit for
assessing and improving fairness in AI", Microsoft Tech Report 2020;
(3) Akiba T. i in., „Optuna: A next-generation hyperparameter optimization
framework", KDD 2019; (4) Hardt M., Price E., Srebro N., „Equality of opportunity
in supervised learning", NeurIPS 2016 (equalized odds); (5) opcjonalnie
Grinsztajn L. i in., „Why do tree-based models still outperform deep learning
on tabular data?", NeurIPS 2022 (kontekst wyniku LSTM). Wskaż, w których
sekcjach (4.6, 4.4.1, 5.5b, 5.3) każde źródło powinno być cytowane.
```

**E8. Korekta błędu w DokumentRoznice.md**

```text
W DokumentRoznice.md sekcja §2.3 twierdzi, że projekt „NIE używa class_weight
ani scale_pos_weight w finalnych modelach W3". To nieprawda — sprawdź
ml-learing-center/main.py:246-333 (rf_base: class_weight="balanced", xgb_base:
scale_pos_weight, lgbm_base: class_weight="balanced", cat_base:
auto_class_weights="Balanced", LSTM: class_weight dict). Popraw §2.3 tak, żeby
opisywał stan faktyczny: ważenie klas POZOSTAŁO, a kalibracja + progi kosztowe
są warstwą DODATKOWĄ, nie zamiennikiem. Zaktualizuj też §13 P2 #13, który
zaleca usunięcie opisu class_weight z pracy — to zalecenie jest błędne.
```

**E9. Ujednolicenie liczb między dokumentami**

```text
Zweryfikuj i ujednolić liczby AUC cytowane w dokumentach repo: DokumentRoznice.md
§1.2 podaje dla H1 „RF 0.7779 vs 0.7792, XGB 0.7794 vs 0.7818, LSTM 0.7637 vs
0.7686", a reports/metrics_w3.csv zawiera RF 0.7741, XGB 0.7760, LSTM 0.7610.
Ustal źródło rozbieżności (inne runy? wersje przed/po kalibracji? inny split?) —
przejrzyj PodsumowanieSprintu1.md (CREDIT-102) i historię gita dla metrics_w3.csv.
Zdecyduj, który zestaw jest kanoniczny dla pracy (rekomendacja: aktualny
metrics_w3.csv po ostatnim retreningu), zaktualizuj DokumentRoznice.md i wypisz
tabelę „liczba w dokumencie → liczba kanoniczna" do użycia w rozdz. 5.
```

**E10. Macierze pomyłek przy progach produkcyjnych**

```text
W ml-learing-center/evaluation.py macierze pomyłek (confusion_*_w3.png) liczone
są przy progu 0.5, podczas gdy system decyduje progami kosztowymi z
ml-service/alert_thresholds.json (0.130–0.185). Dodaj do evaluation.py wariant
generujący confusion matrix przy progu kosztowym per model (drugi zestaw PNG
z sufiksem _costopt) oraz metryki progowe precision/recall/F1 przy obu progach,
dopisane do metrics_w3.csv jako nowe kolumny lub osobny plik
metrics_thresholded_w3.csv. Uruchom i pokaż wyniki — rozdz. 5.1.1 (F1/precision/
recall) będzie z tego korzystał.
```

**R3. Weryfikacja końcowa przed składem v9**

```text
Przeprowadź walidację nowej wersji pracy (v9) analogiczną do WalidacjaPDFv7.md:
wyekstrahuj tekst z PDF, sprawdź kolejno: (1) rozdz. 3 i 5 mają treść, nie tylko
nagłówki; (2) wszędzie 5 modeli (grep po „trzy klasyfikatory", „LSTM, Random
Forest i XGBoost"); (3) split 60/20/20 i test 6 000 (grep po „9 000", „70%",
„30%"); (4) LSTM (3,3) w opisie finalnym; (5) sekcje 4.6/4.7/4.8 istnieją;
(6) obietnica bootstrapu ma pokrycie w reports/bootstrap_auc_report.md;
(7) figury 4.1/4.3/4.5/4.7 zgodne z tekstem (ramka max_depth, podpisy 4.3/4.4);
(8) H1/H2/H3 w 3.2 i literalna weryfikacja w 5.6; (9) liczby w rozdz. 5 zgodne
z reports/*.csv; (10) spis tabel niepusty. Wynik: WalidacjaPDFv9.md z tabelą
status per punkt.
```

---

## 5. Instrukcja dalszej pracy nad pracą magisterską

### Kolejność (ścieżka krytyczna)

1. **Kod najpierw, tekst potem** — zadania B1–B4 (diagnoza PD per okno, fix
   wycieku progów, bootstrap, wariant bez SEX) generują liczby, na których
   opiera się rozdz. 5. Wykonać przed pisaniem E2. Szacunkowo < 1 dzień łącznie.
2. **Domknąć CREDIT-114 (final report)** — jest oznaczony P0 na ścieżce
   krytycznej w CHECKLIST.md; CREDIT-113 (stacking) jest P2 i można go
   **świadomie wyciąć z zakresu pracy** (jedno zdanie w „kierunkach dalszych
   badań"), zamiast opóźniać nim tekst.
3. **Rozdział 3 (E1)** — po stronie projektu wszystko gotowe, można pisać od razu.
4. **Aktualizacja rozdz. 4 (E3, E4, E5)** — równolegle z figurami (R1).
5. **Rozdział 5 + Zakończenie (E2)** — dopiero po B1–B4 i CREDIT-114.
6. **Spójność i skład (E6, E7, R2)**, na końcu **walidacja (R3)** przed
   wygenerowaniem „Praca Magisterska-9.pdf".

### Zasady przy pisaniu (wnioski z tej recenzji)

- **Jedno źródło prawdy dla liczb:** `reports/*.csv` po ostatnim retreningu.
  Nigdy nie przepisywać liczb z dokumentów sprintowych bez sprawdzenia w CSV
  (precedens: rozjazd 0.7779 vs 0.7741 — zad. E9).
- **Nie obiecywać niczego, czego nie ma w repo.** Każde zdanie typu „raportowana
  w rozdziale 5 wariancja…" musi mieć artefakt w `reports/`. Obietnica bez
  pokrycia to pytanie-pułapka zastawiona na samego siebie.
- **Słabe wyniki opisywać pierwszym.** Statyka wygrywa przy FA=10% — praca ma to
  powiedzieć wprost i zinterpretować (komplementarność), zanim zrobi to komisja.
  Uczciwe self-reporting ograniczeń to najmocniejsza obrona.
- **Figury tylko ze skryptów w repo.** Każdy rysunek rozdz. 4/5 musi być
  odtwarzalny jednym poleceniem (`thesis_figures/generate_ch4_figures.py`).
  Figury „znikąd" = zarzut niereprodukowalności.
- **Rozdzielać dwa sensy „dynamiczności"** konsekwentnie: architektura (LSTM)
  vs schemat oceny (trajektoria W0..W3). Teza pracy opiera się na drugim;
  nie wiązać jej z LSTM, który jest najsłabszym modelem.
- **Hipotezy sformułować tak, jak wyszły wyniki** (H2 = wczesność + unikalne
  wykrycia, nie wyższy catch rate), zanim komisja porówna je z liczbami.

### Przygotowanie do obrony (niezależnie od tekstu)

- Przećwiczyć odpowiedzi Q1–Q5 z sekcji 3 na głos, z liczbami z pamięci
  (AUC: CatBoost 0.780 / LSTM 0.761; DPD ≤ 0.039; EOD ≤ 0.033; progi 0.130–0.185;
  lead time ~2 okna; unikalne wykrycia 36–72/model; static wins @FA=10% do −7.7 pp).
- Mieć w zanadrzu wyniki B1 (PD per okno) i B4 (bez SEX) — nawet jeśli nie wejdą
  do pracy, zamykają dwa najgroźniejsze pytania jednym slajdem każdy.
- Slajd „ograniczenia pracy" pokazać SAMEMU przed sekcją pytań: przekrojowy
  zbiór → symulowany monitoring, jeden dataset, SEX w cechach (z uzasadnieniem
  badawczym). Komisja rzadko atakuje ograniczenia, które autor sam nazwał.