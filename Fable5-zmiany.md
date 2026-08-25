# Fable5-zmiany.md — zadania dla Claude Fable 5 i ich wykonanie

> Plik scala (2026-07-07): listę zadań `Uzyj-Fable5-Zanim-Zniknie.md` (+ angielski
> oryginał) oraz raporty wykonania `Fable5_Task1-4.md`. Struktura per zadanie:
> **opis i prompt → pełny raport wykonania → epilog** (co z ustaleń zostało
> wdrożone). Oryginalne pliki usunięte z repo — dostępne w historii gita.
>
> ⚠️ **Liczby w raportach są historyczne** (stan artefaktów na moment wykonania
> zadania, PRZED naprawami metodologicznymi z 2026-07-07 — progami na splicie
> kalibracyjnym i skalerami po splicie). Wartości kanoniczne: `ml-learing-center/
> reports/FINAL_REPORT.md` + `reports/*.csv`; ściąga: `docs/thesis/obrona_QA.md`.

## Spis zadań

| Zadanie | Status | Raport |
|---|---|---|
| 1. Kontradyktoryjny przegląd przed obroną | ✅ wykonane 2026-07-06 | sekcja Task 1 |
| 2. Fairness: interpretacja + mitygacja | ✅ wykonane 2026-07-06 | sekcja Task 2 |
| 3. Polowanie na błędy poprawności ML | ✅ wykonane 2026-07-06 | sekcja Task 3 |
| ad-hoc. Audyt wykonania sprintów (CHECKLIST vs repo) | ✅ wykonane 2026-07-07 | sekcja Task 4 |
| 4. Wariant B end-to-end | ⏭️ nie uruchamiane — funkcja powstała wcześniej w sprintach (CREDIT-101..116) |
| 5. Pisanie wyników/dyskusji | ✅ zrealizowane inną ścieżką — drafty `docs/thesis/Rozdzial{3,4,5}*.md` + paczka LaTeX |
| 6. Audyt kontraktu przez stos | ⏭️ nie uruchamiane osobno — częściowo pokryte testami parytetu i CREDIT-115/116 |
| 7. Test statyczne-vs-dynamiczne | ✅ pokryte w Task 1 (ustalenia #13/#14/#22) + `FINAL_REPORT.md` §2 i diagnozie PD-per-okno |

---

# ZADANIE 1 — Kontradyktoryjny przegląd przed obroną

**O co chodzi.** Fable 5 jako wrogi recenzent: atakuje metodologię pracy
w zestawieniu z tym, co *faktycznie* robi kod, i wskazuje każdą tezę, której
implementacja nie potwierdza.

**Prompt (użyty):**

```text
Jesteś recenzentem mojej pracy magisterskiej i jesteś sceptyczny. Twoim
zadaniem jest znaleźć każdą słabość, którą komisja może zaatakować na obronie.

Kontekst:
- To repo to system predykcji ryzyka niewypłacalności kart kredytowych: ensemble
  5 modeli (Random Forest, XGBoost, LSTM, LightGBM, CatBoost) serwowany przez
  usługę Flask ML, orkiestrowany przez backend .NET 8, z frontendem React.
- Praca to "Praca Magisterska-8.pdf" (najnowsza wersja).
- Dokumenty pomocnicze: WalidacjaPDFv7.md (walidacja), DokumentRoznice.md
  (różnice praca-vs-kod) oraz podsumowania PodsumowanieSprintu*.md.

Pracuj na wysokim wysiłku. Zrób to:
1. Przeczytaj PDF pracy i powyższe dokumenty.
2. Zweryfikuj kluczowe tezy pracy (o modelach, podejściu z oknem przesuwnym,
   audycie sprawiedliwości i metodologii ewaluacji) w zestawieniu z faktycznym
   kodem w ml-learing-center/ i ml-service/.
3. Zbuduj tabelę ustaleń. Dla każdego: teza z pracy, co pokazuje kod, rozbieżność,
   waga (wysoka/średnia/niska) oraz jak powinienem odpowiedzieć, gdy mnie o to
   zapytają.
4. Wypisz 5 najtrudniejszych pytań, które komisja prawdopodobnie zada, z mocną
   sugerowaną odpowiedzią na każde.

Zgłoś każdą wątpliwość, także te niepewne — sam je odfiltruję. Nie łagodź
ustaleń przez grzeczność.
```

## Wykonanie — raport (oryginalnie: sekcja Task 1 (ten plik))

### Raport (oryg. sekcja Task 1 (ten plik)) — Recenzja sceptyczna pracy magisterskiej (v8) + plan naprawczy

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
## Epilog Zadania 1 (stan 2026-07-07)

Plan naprawczy z sekcji 4 raportu został zrealizowany w całości:
naprawy U1 (train/serve parity), B2/O4 (progi na splicie kalibracyjnym +
skalery po splicie, `reports/{threshold,scaler}_leakage_fix.md`), B1/B3/B4
(diagnoza PD-per-okno, bootstrap, fairness bez SEX), E1/E2 (rozdz. 3 i 5 —
`docs/thesis/` + paczka LaTeX), CREDIT-113 descoped, CREDIT-114 i CREDIT-501
zielone. Pytania Q1–Q5 mają zaktualizowane odpowiedzi w `docs/thesis/obrona_QA.md`
(m.in. nowy wynik: LSTM jako jedyny wygrywa monitoringiem +2,6 pp @FA=10%).

---

# ZADANIE 2 — Wyniki sprawiedliwości: interpretacja + rekomendacja mitygacji

**O co chodzi.** Interpretacja DPD/EOD względem SEX dla 5 modeli W3, ranking
modeli fairness×jakość, rekomendacja jednej strategii mitygacji + gotowa proza.

**Prompt (użyty):**

```text
Pracuj na wysokim wysiłku. Pomagasz mi napisać i obronić sekcję o sprawiedliwości
(fairness) w pracy magisterskiej o predykcji niewypłacalności kredytowej.

Przeczytaj ml-learing-center/fairness_audit.py oraz wyniki, które zapisuje
(sprawdź ml-learing-center/reports/ i thesis_figures/). Audyt liczy Demographic
Parity Difference (DPD) i Equalized Odds Difference (EOD) względem SEX, przy użyciu
fairlearn, dla 5 modeli: Random Forest, XGBoost, LSTM, LightGBM, CatBoost
(warianty "_w3" z oknem przesuwnym).

Następnie:
1. Podsumuj, co liczby DPD/EOD faktycznie mówią o każdym modelu — prostym,
   broniącym się językiem, a nie tylko powtarzając liczby.
2. Uszereguj 5 modeli według tego, jak dobrze każdy broni się przy realnej
   decyzji kredytowej, ważąc sprawiedliwość względem jakości predykcji. Uzasadnij
   ranking.
3. Zarekomenduj JEDNĄ strategię mitygacji (np. reweighting, optymalizacja progu
   przez ThresholdOptimizer z fairlearn, albo post-processing) i wyjaśnij, DLACZEGO
   pasuje do tego zbioru i tego kontekstu prawno-etycznego, wraz z kompromisami.
4. Daj mi 3–4 akapity gotowej prozy do pracy (po polsku) interpretującej wyniki
   i uzasadniającej rekomendację.

Bądź precyzyjny co do różnicy między parytetem demograficznym a wyrównanymi
szansami i dlaczego ten wybór ma znaczenie dla kredytowania.
```

## Wykonanie — raport (oryginalnie: sekcja Task 2 (ten plik))


### Raport (oryg. sekcja Task 2 (ten plik)) — Sekcja fairness: analiza, ranking, mitygacja, proza + plan wykonawczy

> **Autor:** Claude Fable 5 · **Data:** 2026-07-06
> **Zakres:** interpretacja audytu CREDIT-112 (fairlearn, DPD/EOD wrt SEX, 5 modeli W3),
> ranking modeli fairness×jakość, rekomendacja mitygacji, gotowa proza do rozdz. 5.5b,
> lista kroków i prompty dla Opusa 4.8.
> **Źródła danych:** `ml-learing-center/fairness_audit.py`, `reports/fairness_metrics_w3.csv`,
> `reports/fairness_report.md`, `reports/metrics_w3.csv`, `ml-service/alert_thresholds.json`,
> base rate'y policzone na dokładnie tym splicie, którego używa audyt
> (`random_state=42`, `test_size=0.2`, `stratify=y`).

---

## 1. Fundament pojęciowy: DPD vs EOD i dlaczego ten wybór rozstrzyga wszystko

**Demographic Parity Difference (DPD)** — różnica odsetka klientów flagowanych jako
ryzykowni między grupami: `P(ŷ=1|SEX=M) − P(ŷ=1|SEX=F)`. Nie patrzy na to, kto
*faktycznie* nie spłacił. Parytet spełniony = model alarmuje mężczyzn i kobiety
równie często, niezależnie od rzeczywistego ryzyka.

**Equalized Odds Difference (EOD)** — warunkuje na prawdzie:
`max(|TPR_M − TPR_F|, |FPR_M − FPR_F|)`. Pyta: czy *faktycznie niespłacający* są
wykrywani równie często w obu grupach (TPR) i czy *rzetelnie spłacający* są
fałszywie flagowani równie często (FPR).

**Kluczowa liczba:** base rate defaultu w zbiorze testowym = **23.36% (M) vs 21.29% (F)**
(pełny zbiór: 24.17% vs 20.78%). Wniosek: **nawet idealny predyktor miałby
DPD ≈ +0.021** — flagowałby dokładnie przyszłych defaultujących, czyli 23.4% mężczyzn
i 21.3% kobiet. Parytet demograficzny jest matematycznie niekompatybilny z trafną
oceną ryzyka przy różnych base rate'ach; wymuszenie DPD=0 wymagałoby traktowania osób
o identycznym profilu ryzyka różnie ze względu na płeć — czyli dyskryminacji
bezpośredniej, sprzecznej z obowiązkiem rzetelnej oceny zdolności kredytowej
(art. 70 Prawa bankowego). Equalized odds dopuszcza różne częstości alarmów, jeśli
odzwierciedlają base rate'y, ale żąda **równego rozkładu ciężaru błędów** — to metryka
operacyjna dla kredytowania. DPD raportujemy jako screening wpływu (odpowiednik
amerykańskiej reguły 4/5), **wnioskujemy z EOD**.

---

## 2. Co liczby faktycznie mówią o każdym modelu

Kotwica interpretacyjna: obserwowane DPD (0.007–0.039) czytać względem
„DPD wyroczni" ≈ 0.021, nie względem zera.

| Model | DPD | EOD | Co dominuje w EOD | Interpretacja broniąca się |
|---|---:|---:|---|---|
| Random Forest | +0.035 | +0.029 | luka FPR (0.372 vs 0.343) | ~połowa DPD z base rate, ~połowa „od modelu". Koszt: rzetelni mężczyźni fałszywie flagowani o 2.9 pp częściej |
| XGBoost | +0.038 | +0.033 | **luka TPR** (0.768 vs 0.735) | Jedyny model, w którym EOD napędza luka wykrywalności: niespłacające kobiety wykrywane o 3.3 pp *rzadziej* — nierówna ochrona we wczesnym ostrzeganiu |
| LightGBM | +0.027 | +0.022 | luka TPR (0.749 vs 0.727) | Najmniejsze luki wśród drzew; nadwyżka nad wyrocznią tylko ~0.6 pp — zachowanie niemal aktuarialnie neutralne |
| CatBoost | +0.039 | +0.033 | luka FPR (0.435 vs 0.401) | Największe luki, częściowo mechaniczne: najniższy próg (0.130) → najwięcej alarmów ogółem (52%/48%). Jednocześnie **najwyższe TPR w obu grupach** (0.816/0.792) — najlepiej chroni obie grupy |
| LSTM | +0.007 | +0.015 | luka FPR, **odwrócona** (F 0.410 vs M 0.394) | Jedyny poniżej DPD wyroczni, jedyny z odwróconym znakiem selekcji. **Nie widzi cech demograficznych** — wejście (3,3) to wyłącznie PAY/BILL_AMT/PAY_AMT |

**Dwa wnioski przekrojowe (mocniejsze niż liczby):**

1. **Dodatnie DPD modeli statycznych ma w większości pochodzenie strukturalne**
   (base rate), a nadwyżka ponad wyrocznię to 0.6–1.8 pp. To poprawna odpowiedź na
   zarzut disparate impact: nie negujemy DPD, tylko dekomponujemy na składnik
   aktuarialny i modelowy.
2. **Kontrast LSTM vs drzewa = naturalne badanie ablacyjne**: modele statyczne
   dostają SEX jako one-hot, LSTM wyłącznie zachowanie płatnicze — i osiąga
   niemal parytet. Empiryczny dowód, że sygnał behawioralny jest w tym zbiorze
   prawie neutralny płciowo, a luki drzew pochodzą z warstwy demograficznej.
   Amunicja i do sekcji fairness, i na pytanie komisji o SEX w cechach.

**Zastrzeżenia do ujawnienia w pracy:** progi binaryzacji optymalizowane na tym
samym zbiorze testowym, na którym liczono audyt; audyt tylko po SEX
(nie AGE/EDUCATION/MARRIAGE); jeden split, bez przedziałów ufności
(przy n=2402/3598 różnice 0.02–0.03 mają niemałą wariancję próbkowania).

---

## 3. Ranking: kto broni się najlepiej przy realnej decyzji kredytowej

Kryterium: równowaga jakości (AUC/Brier z `metrics_w3.csv`) i sprawiedliwości
(EOD pierwotnie, DPD pomocniczo), z uwzględnieniem kontekstu progu.

| Miejsce | Model | AUC | Brier | DPD | EOD | Uzasadnienie |
|---|---|---:|---:|---:|---:|---|
| **1** | LightGBM | 0.7764 | 0.1366 | 0.027 | 0.022 | Jedyny Pareto-optymalny: 2. AUC (0.004 od lidera — granica szumu), najlepsza sprawiedliwość wśród drzew, żadnej słabości. Wybór domyślny |
| **2** | CatBoost | 0.7802 | 0.1354 | 0.039 | 0.033 | Najlepsza dyskryminacja i kalibracja; najgorsza sprawiedliwość, ale 3× pod limitem i częściowo mechaniczna (najniższy próg). Najwyższe TPR w obu grupach → najwięcej ochrony dla wszystkich. Ranking 1↔2 zależy od wag instytucji — powiedzieć wprost |
| **3** | LSTM | 0.7610 | 0.1387 | 0.007 | 0.015 | Mistrz parytetu, ale najsłabsza jakość; przewaga ~0.7 pp EOD nad LGBM nie równoważy 2 pp straty AUC w kontekście portfelowym. Rola: dowód ablacyjny, nie model decyzyjny |
| **4** | Random Forest | 0.7741 | 0.1372 | 0.035 | 0.029 | Zdominowany przez LGBM na obu osiach, ale sprawiedliwszy od XGB przy praktycznie tej samej jakości |
| **5** | XGBoost | 0.7760 | 0.1360 | 0.038 | 0.033 | Przewaga AUC nad RF (0.002) w szumie; luki spójnie największe po CatBooście, a EOD napędza luka TPR — nierówna *ochrona*, etycznie gorsza w systemie wczesnego ostrzegania niż luka FPR tej samej wielkości |

---

## 4. Rekomendacja mitygacji: ThresholdOptimizer (equalized odds) w warstwie alertów

**Jedna strategia:** post-processing progów decyzyjnych przez
`fairlearn.postprocessing.ThresholdOptimizer(constraints="equalized_odds")`,
osadzony w warstwie alertów monitoringu. Krok zerowy (poza mitygacją, jako
zgodność prawna): usunięcie SEX z wektora cech — per kontrast LSTM prawie nic
nie kosztuje.

**Dlaczego pasuje do tego zbioru i tego systemu (nie ogólnie):**

1. **System już decyduje progami** (`alert_thresholds.json`, per model).
   ThresholdOptimizer = ta sama mechanika + wymiar grupy (para progów
   wyrównująca TPR/FPR). Wpina się bez dotykania czegokolwiek innego.
2. **Nie narusza kalibracji, na której stoi teza pracy.** Trajektoria PD W0..W3
   ma sens dzięki kalibracji izotonicznej (CREDIT-105). Reweighting /
   in-processing (ExponentiatedGradient) = retrening + kaskadowe powtórzenie
   kalibracji i progów dla 5 modeli. Post-processing zostawia PD nietknięte.
3. **Celuje we właściwą metrykę.** Skoro obowiązującą definicją jest equalized
   odds, mitygacja musi optymalizować właśnie ją; klasyczny reweighting celuje
   w parytet demograficzny — metrykę uznaną za niewłaściwą przy różnych base rate'ach.
4. **Proporcjonalność.** Luki ≤0.034 przy limicie 0.10 → ciężka interwencja
   w trening jest nieproporcjonalna. Post-processing = udokumentowana,
   przetestowana zdolność włączana, gdy audyt-bramka wykaże przekroczenie.
5. **Kontekst prawny gra na korzyść przy precyzyjnym umiejscowieniu.** Próg
   zależny od płci w *decyzji kredytowej* = dyskryminacja bezpośrednia (logika
   2004/113/WE i Test-Achats C-236/09). Ale ten system to **wczesne ostrzeganie**:
   alert kieruje do przeglądu przez analityka (człowiek w pętli, art. 22 RODO),
   nie do odmowy. Wyrównaniu podlega ciężar przeglądu i równość ochrony przed
   niewykrytym pogorszeniem. AI Act art. 10 ust. 5 wprost dopuszcza przetwarzanie
   danych wrażliwych do wykrywania/korygowania biasu.

**Kompromisy (nazwać uczciwie):**
(a) wymaga SEX w momencie alertu — objąć zasadą ograniczenia celu (RODO);
(b) przesuwa progi z optimum kosztowego — oczekiwany koszt `5·FN+1·FP` rośnie
(przy tych lukach marginalnie; policzyć dokładnie);
(c) ścisły ThresholdOptimizer randomizuje między progami — w praktyce
deterministyczne przybliżenie, kosztem niedomknięcia luk do zera;
(d) nie zmienia modelu → po retreningu luki mogą wrócić — audyt jako stała
bramka wydaniowa, nie jednorazowe badanie.

---

## 5. Gotowa proza do pracy (rozdz. 5.5b — do wklejenia)

> Audyt sprawiedliwości przeprowadzono z użyciem biblioteki fairlearn dla pięciu skalibrowanych modeli W3, względem atrybutu chronionego SEX, na wydzielonym zbiorze testowym (6 000 obserwacji; 2 402 mężczyzn, 3 598 kobiet), przy binaryzacji predykcji progami kosztowymi wyznaczonymi w rozdziale 4 — audyt odzwierciedla zatem faktyczny punkt pracy systemu, a nie umowny próg 0,5. Zastosowano dwie komplementarne miary. Różnica parytetu demograficznego (DPD) porównuje częstość alarmów między grupami, abstrahując od rzeczywistych zdarzeń niewykonania zobowiązania; różnica wyrównanych szans (EOD) warunkuje na prawdziwej etykiecie i mierzy większą z dwóch luk: wykrywalności faktycznych defaultów (TPR) oraz fałszywych alarmów wśród klientów rzetelnie spłacających (FPR). Rozróżnienie to ma w kontekście kredytowym znaczenie zasadnicze. Częstość niewykonania zobowiązania różni się między grupami (23,4% wobec 21,3% w zbiorze testowym), wskutek czego nawet bezbłędny klasyfikator wykazywałby DPD na poziomie około 0,021; wymuszenie pełnego parytetu demograficznego wymagałoby traktowania osób o identycznym profilu ryzyka odmiennie ze względu na płeć, co samo stanowiłoby dyskryminację bezpośrednią i stałoby w sprzeczności z obowiązkiem rzetelnej oceny zdolności kredytowej wynikającym z art. 70 Prawa bankowego. Z tego względu DPD raportowane jest jako miara przesiewowa wpływu, natomiast właściwym kryterium oceny uczyniono wyrównane szanse — równy rozkład ciężaru błędów przy danym stanie faktycznym.
>
> Wszystkie pięć modeli spełnia przyjęte kryterium |DPD|, |EOD| ≤ 0,10 z co najmniej trzykrotnym marginesem: wartości DPD mieszczą się w przedziale od +0,007 (LSTM) do +0,039 (CatBoost), a EOD — od +0,015 (LSTM) do +0,033 (CatBoost, XGBoost). Interpretując te wyniki na tle wspomnianej różnicy base rate, większość obserwowanego DPD modeli drzewiastych ma pochodzenie strukturalne, a nadwyżka wnoszona przez same modele wynosi od około 0,6 do 1,8 punktu procentowego. Dekompozycja EOD ujawnia przy tym różnice jakościowe istotniejsze niż same wartości: w modelach Random Forest i CatBoost lukę tworzy częstość fałszywych alarmów (rzetelnie spłacający mężczyźni są flagowani odpowiednio o 2,9 i 3,3 punktu procentowego częściej), natomiast w modelu XGBoost — luka wykrywalności (niespłacające kobiety są identyfikowane o 3,3 punktu procentowego rzadziej), co w systemie wczesnego ostrzegania oznacza nierówną ochronę przed niewykrytym pogorszeniem sytuacji. Na szczególną uwagę zasługuje model LSTM, który jako jedyny nie otrzymuje na wejściu żadnych cech demograficznych — jego tensor wejściowy zawiera wyłącznie sekwencję statusów płatności, sald i wpłat — i jako jedyny osiąga wartości poniżej luki strukturalnej, z odwróconym znakiem częstości selekcji. Kontrast ten pełni rolę naturalnego badania ablacyjnego: sygnał czysto behawioralny okazuje się w badanym zbiorze niemal neutralny względem płci, co wskazuje, że umiarkowane luki modeli statycznych pochodzą z warstwy cech demograficznych i ich korelatów, nie zaś z historii płatniczej.
>
> Zestawienie sprawiedliwości z jakością predykcji prowadzi do wniosku, że wybór modelu do zastosowania decyzyjnego nie wymaga poświęcenia żadnego z tych kryteriów. Model LightGBM łączy drugą najwyższą zdolność dyskryminacyjną (AUC 0,776, o 0,004 od najlepszego wyniku) z najmniejszymi lukami sprawiedliwości wśród metod drzewiastych (DPD 0,027; EOD 0,022) i jako jedyny nie wykazuje słabości w żadnym z rozważanych wymiarów. Model CatBoost, mimo formalnie największych wartości DPD i EOD, osiąga najwyższą wykrywalność defaultów w obu grupach jednocześnie (TPR 0,816 i 0,792), a część jego luk ma charakter mechaniczny, wynikający z najniższego progu kosztowego i tym samym największej ogólnej częstości alarmów; pozostaje więc zasadnym wyborem tam, gdzie instytucja przypisuje szczególną wagę kompletności wykrywania. Model LSTM, pomimo najkorzystniejszego profilu parytetu, cechuje najniższa jakość predykcyjna (AUC 0,761), a jego przewaga sprawiedliwości nad modelem LightGBM — rzędu jednego punktu procentowego — nie równoważy w kontekście portfelowym dwupunktowej straty AUC.
>
> W zakresie mitygacji, wobec faktu, że wszystkie modele spełniają przyjęte kryterium ze znacznym zapasem, zasadne jest podejście proporcjonalne: utrzymanie audytu DPD/EOD jako stałej bramki wydaniowej po każdym retreningu oraz przygotowanie — jako udokumentowanego mechanizmu warunkowego — korekty post-hoc progów decyzyjnych metodą ThresholdOptimizer z biblioteki fairlearn, z ograniczeniem wyrównanych szans. Za takim umiejscowieniem interwencji przemawiają trzy argumenty. Po pierwsze, warstwa decyzyjna systemu już operuje progami per model, a korekta post-hoc nie narusza skalibrowanych prawdopodobieństw, na których opiera się trajektoria PD stanowiąca rdzeń niniejszej pracy — w przeciwieństwie do metod pre-processingu (ponowne ważenie danych) i in-processingu, które wymagałyby powtórzenia treningu, kalibracji i wyznaczania progów dla wszystkich pięciu modeli. Po drugie, mechanizm ten optymalizuje bezpośrednio wyrównane szanse, a więc kryterium uznane wyżej za właściwe dla oceny kredytowej, podczas gdy klasyczne ponowne ważenie celuje w parytet demograficzny. Po trzecie, zróżnicowanie progów względem atrybutu chronionego jest dopuszczalne właśnie dlatego, że badany system pełni funkcję wczesnego ostrzegania kierującego ekspozycję do przeglądu analityka, nie zaś zautomatyzowanej decyzji kredytowej: wyrównaniu podlega ciężar bycia objętym przeglądem oraz równość ochrony przed niewykrytym pogorszeniem, a przetwarzanie atrybutu chronionego w celu wykrywania i korygowania obciążeń znajduje wyraźną podstawę w art. 10 ust. 5 rozporządzenia w sprawie sztucznej inteligencji. Rozwiązanie to niesie kompromisy, które należy odnotować: wymaga dostępności atrybutu chronionego w warstwie alertów (co powinno zostać objęte zasadą ograniczenia celu), przesuwa progi względem optimum kosztowego, a jako korekta zewnętrzna wobec modelu nie usuwa źródła luk — stąd konieczność utrzymania audytu jako mechanizmu ciągłego, nie jednorazowego badania.

---

## 6. Lista kroków do zrobienia

| # | Krok | Typ | Priorytet | Zależności |
|---|---|---|---|---|
| F1 | Kontr-eksperyment bez SEX (dowód ablacyjny do akapitu 2 prozy) | kod | **P0** | — |
| F2 | Fix wycieku: progi kosztowe liczone na splicie kalibracyjnym, re-run audytu | kod | **P0** | — (tożsame z B2 z sekcja Task 1 (ten plik) — nie dublować, jeśli już wykonane) |
| F3 | Bootstrap CI dla DPD/EOD (odpowiedź na zarzut „jeden split, brak istotności") | kod | P1 | F2 (audyt na nowych progach) |
| F4 | Prototyp ThresholdOptimizer: policzyć faktyczne progi per grupa + koszt kompromisu | kod | P1 | F2 |
| F5 | Figura `fig_5_10_fairness.py` w `thesis_figures/rozdzial_5/` | kod/figura | P1 | F2 (żeby PNG pokazywały finalne progi) |
| F6 | Wklejenie prozy z §5 do rozdz. 5.5b + dopasowanie liczb, jeśli F1/F2 je zmienią | tekst | **P0** | F1, F2 |
| F7 | Bibliografia: Hardt/Price/Srebro 2016, Bird et al. 2020 (+ Test-Achats, AI Act już są w pracy) | tekst | P1 | — |
| F8 | Rozszerzenie audytu na AGE/EDUCATION/MARRIAGE jako appendix (obrona przed pytaniem „czemu tylko SEX?") | kod | P2 | F2 |
| F9 | Karta odpowiedzi na obronę (Q&A fairness) — wydruk do teczki | tekst | P1 | F1–F4 |

**Kolejność wykonywania: F2 → F1 → (F3, F4, F8 równolegle) → F5 → F6 → F7 → F9.**
F2 idzie pierwsze, bo zmienia progi, od których zależą wszystkie pozostałe liczby.

---

## 7. Gotowe prompty dla Opusa 4.8

Wklejać pojedynczo w Claude Code (model: Opus 4.8) w katalogu głównym repo.

### F2 — fix wycieku progów (wykonać PIERWSZE)

```text
W ml-learing-center/main.py sekcja CREDIT-106 optymalizuje progi alertu na
zbiorze TESTOWYM (_y_te_arr = y_te_w3.to_numpy(), main.py ok. linii 406-413) —
to wyciek: te same dane służą potem do ewaluacji, audytu fairness (CREDIT-112)
i porównania static-vs-dynamic. Przenieś optymalizację progów na split
kalibracyjny (X_cal_w3/y_cal_w3 dla modeli statycznych, Xs_cal_w3/ys_cal_w3 dla
LSTM — te same dane, na których fitowana jest kalibracja izotoniczna; to
akceptowalny kompromis, odnotuj w komentarzu). Po zmianie: uruchom python
main.py (zregeneruje alert_thresholds.json), potem python fairness_audit.py.
Wypisz tabelę porównawczą: stare vs nowe progi per model oraz stare vs nowe
DPD/EOD per model. Zapisz ją w reports/threshold_leakage_fix.md z wnioskiem,
czy zmiana jest kosmetyczna (oczekiwane) — to argument na obronę, że wyciek
nie zawyżył wniosków audytu. Niczego poza main.py nie modyfikuj; wyniki tylko
do reports/.
```

### F1 — kontr-eksperyment bez SEX (dowód ablacyjny)

```text
W ml-learing-center/ napisz skrypt fairness_no_sex.py: powtórz protokół
treningowy z main.py (okno W3 = WINDOW_DEFS[3], split 60/20/20 przez podwójny
train_test_split z random_state=42 i stratify — skopiuj dokładnie z
main.py:238-243, kalibracja izotoniczna CalibratedClassifierCV(FrozenEstimator,
'isotonic')) dla WARIANTU cech bez SEX: zmodyfikuj wynik engineer_features tak,
by wykluczyć kolumny SEX_* (zostaw EDUCATION_*/MARRIAGE_*). Przetrenuj RF,
XGBoost, LightGBM, CatBoost z hiperparametrami identycznymi jak w main.py
(LSTM pomiń — jego tensor (3,3) i tak nie zawiera SEX, co odnotuj w raporcie
jako punkt odniesienia). Policz per model: AUC i Brier na teście oraz DPD/EOD
po SEX (logika z fairness_audit.py — SEX z danych służy TYLKO do slicingu,
nie do modelu) przy progach kosztowych liczonych tym samym protokołem co
CREDIT-106 (po fixie F2: na splicie kalibracyjnym). NICZEGO nie nadpisuj —
nowe artefakty wyłącznie do reports/: fairness_no_sex_metrics.csv +
fairness_no_sex_report.md z tabelą porównawczą (wariant z SEX vs bez SEX:
AUC, Brier, DPD, EOD per model) i wnioskiem: czy usunięcie zmiennej chronionej
istotnie zmienia parytet i jakość (oczekiwanie: minimalnie, bo sygnał częściowo
wycieka przez korelaty — to teza do obrony; jeśli wyjdzie inaczej, opisz
uczciwie). Na końcu wypisz 3 zdania po polsku do wykorzystania w pracy.
```

### F3 — bootstrap CI dla metryk fairness

```text
W ml-learing-center/ napisz skrypt fairness_bootstrap.py: reużyj
load_test_split() i _load_thresholds() z fairness_audit.py (import, nie
copy-paste), po czym wykonaj 1000 bootstrapowych repróbkowań zbioru testowego
(ze zwracaniem, seed=42; resampling indeksów wspólny dla y_true/y_prob/sex_te,
żeby zachować spójność wierszy). W każdym powtórzeniu policz DPD i EOD per
model (fairlearn) przy progach z alert_thresholds.json. Wyjście:
reports/fairness_bootstrap_w3.csv (1000 wierszy × 5 modeli × 2 metryki) oraz
reports/fairness_bootstrap_report.md z tabelą: DPD i EOD per model ze średnią,
odchyleniem std i 95% CI percentylowym + wnioski: (a) czy CI któregokolwiek
modelu przekracza 0.10 (oczekiwane: nie), (b) czy różnica LSTM vs reszta jest
poza nakładaniem CI, (c) czy różnice między modelami drzewiastymi są
rozróżnialne statystycznie (oczekiwane: częściowo nie — napisać uczciwie).
Dodaj wykres reports/fairness_bootstrap_w3.png (boxploty DPD i EOD per model,
pozioma linia na 0.10 i na 0.021 = luka strukturalna base rate).
```

### F4 — prototyp ThresholdOptimizer (mechanizm warunkowy)

```text
W ml-learing-center/ napisz skrypt mitigation_threshold_optimizer.py:
dla 5 modeli W3 (reużyj load_test_split z fairness_audit.py) zastosuj
fairlearn.postprocessing.ThresholdOptimizer z constraints="equalized_odds"
i objective="balanced_accuracy_score" (lub odpowiednim dla kosztu FN=5×FP —
sprawdź w dokumentacji fairlearn dostępne objectives i wybierz najbliższy;
jeśli żaden nie odzwierciedla asymetrii 5:1, odnotuj to jako ograniczenie).
UWAGA: ThresholdOptimizer wymaga fitowania na danych z sensitive_features —
fituj na splicie kalibracyjnym (odtwórz go jak w main.py), ewaluuj na teście.
Ponieważ mamy gotowe y_prob (predict_proba), użyj trybu prefit/predict_method
odpowiedniego dla skalibrowanych estymatorów — dla LSTM opakuj kalibrator w
minimalny obiekt z predict_proba. Wyjście: reports/mitigation_thresholds.md
z tabelą per model: (a) progi per grupa (M/F) wybrane przez optymalizator,
(b) DPD/EOD przed → po, (c) koszt 5·FN+1·FP przed → po (kompromis!),
(d) TPR/FPR per grupa przed → po. Wniosek: o ile mitygacja domyka luki i ile
kosztuje. Podkreśl w raporcie, że to mechanizm WARUNKOWY (bramka 0.10 nie jest
przekroczona), zgodnie z rekomendacją z sekcja Task 2 (ten plik) §4. Nie zmieniaj
artefaktów produkcyjnych.
```

### F5 — figura fairness do rozdziału 5

```text
W ml-learing-center/thesis_figures/ obejrzyj strukturę (README.md, common/,
rozdzial_5/fig_5_*.py — przeczytaj 1-2 istniejące skrypty, żeby przejąć
konwencję stylu, palety i zapisu do output/). Napisz
rozdzial_5/fig_5_10_audyt_fairness.py generujący jedną złożoną figurę
(2 panele lub 2×2): (a) selection rate per SEX per model z liniami base rate
(0.2336 M / 0.2129 F), (b) TPR i FPR per SEX per model, (c) opcjonalnie DPD/EOD
per model jako słupki z linią limitu 0.10 i linią luki strukturalnej 0.021.
Dane bierz z reports/fairness_metrics_w3.csv (nie hardkoduj liczb). Podpisy
i etykiety po polsku (do pracy magisterskiej). Wygeneruj PNG i sprawdź, że
generate_all.py go obejmuje (dopisz, jeśli lista skryptów jest jawna).
```

### F6 — wklejenie prozy + spójność liczb

```text
Przeczytaj sekcja Task 2 (ten plik) §5 (cztery akapity prozy o audycie fairness) oraz
aktualne wyniki: reports/fairness_report.md, reports/fairness_metrics_w3.csv,
reports/threshold_leakage_fix.md (jeśli istnieje po F2) i
reports/fairness_no_sex_report.md (jeśli istnieje po F1). Zadanie: przygotuj
finalną wersję sekcji 5.5b pracy do docs/thesis/Rozdzial5_5b_fairness.md:
(1) weź prozę z sekcja Task 2 (ten plik) §5 jako bazę; (2) zaktualizuj KAŻDĄ liczbę,
jeśli po F1/F2 progi lub DPD/EOD się zmieniły (porównaj z aktualnym CSV —
nie ufaj liczbom z prozy w ciemno); (3) jeśli F1 wykonane — dopisz jedno
zdanie z wynikiem kontr-eksperymentu bez SEX jako domknięcie argumentu
ablacyjnego; (4) jeśli F3 wykonane — dodaj przedziały ufności przy pierwszym
przywołaniu DPD/EOD; (5) dodaj odsyłacze do figury 5.10 i tabeli z wynikami.
Zachowaj styl akademicki oryginału. Na końcu wypisz listę zmian względem bazy.
```

### F7 — bibliografia fairness

```text
Przygotuj wpisy bibliograficzne w formacie identycznym jak [1]–[31] w
„Praca Magisterska-8.pdf" (przeczytaj 2-3 wpisy dla wzorca) dla: (1) Hardt M.,
Price E., Srebro N., „Equality of opportunity in supervised learning",
NeurIPS 2016 (definicja equalized odds — cytować przy pierwszym użyciu EOD);
(2) Bird S. i in., „Fairlearn: A toolkit for assessing and improving fairness
in AI", Microsoft, MSR-TR-2020-32, 2020 (narzędzie audytu); (3) opcjonalnie
Barocas S., Hardt M., Narayanan A., „Fairness and machine learning", MIT Press
2023 (tło DP vs EO). Wskaż numerację kontynuującą obecną bibliografię ([32],
[33], [34]) i dokładne miejsca cytowań w sekcji 5.5b (definicje DPD/EOD,
opis narzędzia, dyskusja wyboru metryki). Sprawdź, czy praca cytuje już AI Act
[25] i RODO [26] — sekcja 5.5b ma się do nich odwołać, nie dublować.
```

### F8 — rozszerzenie audytu na pozostałe atrybuty (appendix)

```text
W ml-learing-center/ napisz skrypt fairness_extended.py rozszerzający audyt
CREDIT-112 na atrybuty AGE (binning: <30, 30-45, >45), EDUCATION (1-4,
zbij 0/5/6 do „inne") i MARRIAGE (1/2, zbij 0/3 do „inne"). Reużyj
load_test_split z fairness_audit.py, ale zwróć dodatkowo kolumny AGE/EDUCATION/
MARRIAGE ze zbioru testowego (uwaga: muszą być poprawnie wyrównane ze splitem —
przekaż je przez train_test_split razem z X i y jak sex_all w oryginale).
Dla każdego atrybutu i modelu policz DPD i EOD (dla atrybutów wielogrupowych
fairlearn liczy max różnicę między grupami — odnotuj to w raporcie). Wyjście:
reports/fairness_extended_metrics.csv + reports/fairness_extended_report.md
z tabelami per atrybut i werdyktem względem progu 0.10 per atrybut per model.
Jeśli którykolwiek przekracza 0.10 — NIE ukrywaj, opisz i wskaż, że to materiał
do dyskusji ograniczeń w pracy. To materiał na appendix pracy (obrona przed
pytaniem „czemu audytował pan tylko płeć?").
```

### F9 — karta Q&A na obronę (fairness)

```text
Przeczytaj sekcja Task 2 (ten plik) (całość) oraz aktualne raporty fairness w reports/
(fairness_report.md, threshold_leakage_fix.md, fairness_no_sex_report.md,
fairness_bootstrap_report.md, mitigation_thresholds.md — te, które istnieją).
Przygotuj docs/thesis/obrona_fairness_QA.md: 8-10 przewidywanych pytań komisji
o sekcję fairness z odpowiedziami 3-5 zdań każda, z liczbami. Obowiązkowo
uwzględnij: (1) „dlaczego SEX jest cechą modelu, skoro prawo UE zabrania?" —
odpowiedź warstwowa: cel badawczy + wynik kontr-eksperymentu bez SEX + LSTM
jako dowód ablacyjny; (2) „DPD dodatnie = disparate impact, czemu pan to
bagatelizuje?" — odpowiedź przez dekompozycję na lukę strukturalną 0.021
i nadwyżkę modelową + wnioskowanie z EOD; (3) „czemu equalized odds a nie
demographic parity?" — argument o niekompatybilności DP z trafną oceną przy
różnych base rate'ach; (4) „progi liczone na teście — czy audyt nie jest
skażony?" — wynik F2; (5) „jeden split, skąd pewność?" — CI z F3;
(6) „ThresholdOptimizer to jawne różnicowanie po płci — jak to legalne?" —
argument o warstwie wczesnego ostrzegania + human-in-the-loop + AI Act art.
10(5) + status mechanizmu warunkowego; (7) „czemu tylko SEX?" — wynik F8;
(8) „LSTM najsprawiedliwszy — czemu go nie wybrać?" — asymetria 0.7 pp EOD vs
2 pp AUC. Format: pytanie, odpowiedź, liczby-amunicja w punktach.
```

---

## 8. Liczby-amunicja (ściąga do obrony)

- Test: 6 000 (M 2 402 / F 3 598); base rate: **M 23.36% / F 21.29%** (pełny zbiór 24.17/20.78).
- **„DPD wyroczni" ≈ 0.021** — luka strukturalna z base rate; punkt odniesienia dla wszystkich DPD.
- DPD: LSTM 0.007 < LGBM 0.027 < RF 0.035 < XGB 0.038 < CatBoost 0.039 (limit 0.10).
- EOD: LSTM 0.015 < LGBM 0.022 < RF 0.029 < XGB 0.033 ≈ CatBoost 0.033.
- Dekompozycja EOD: RF/CatBoost/LSTM → luka FPR; XGB/LGBM → luka TPR; LSTM jako jedyny z odwróconym znakiem (F > M).
- AUC: CatBoost 0.7802 > LGBM 0.7764 > XGB 0.7760 > RF 0.7741 > LSTM 0.7610; Brier: CatBoost 0.1354 (najlepszy) … LSTM 0.1387.
- Progi kosztowe (FN=5×FP): CatBoost 0.130, RF 0.145, LGBM 0.160, LSTM 0.175, XGB 0.180.
- CatBoost: najwyższe TPR w OBU grupach (0.816 M / 0.792 F) — „najsprawiedliwiej chroni", choć ma największe luki.
- LSTM: wejście (3,3) bez żadnych cech demograficznych — jedyny model „unaware by construction".
- Disparate impact ratio (4/5 rule): wszystkie modele ≥ 0.92 (LSTM 0.99) — daleko od progu 0.8.
## Epilog Zadania 2 (stan 2026-07-07)

Proza z §5 weszła (z liczbami przeliczonymi po leakage-fix) do
`docs/thesis/Rozdzial5.md` §5.5b i `docs/thesis/latex/rozdzial5.tex`.
Kroki F1/F2 wykonane: kontr-eksperyment bez SEX dał wynik MOCNIEJSZY niż
oczekiwany w raporcie (|ΔAUC| ≤ 0,001 przy DPD XGB 0,036→0,011, LGBM →0,007 —
luki były częściowo bezpośrednim efektem SEX, usunięcie nic nie kosztuje);
F5 = figura `fig_5_10_audyt_fairness`. ThresholdOptimizer pozostaje mechanizmem
warunkowym (opisany w pracy), F3/F4 opcjonalne. Aktualne Q&A: `docs/thesis/obrona_QA.md`.

---

# ZADANIE 3 — Polowanie na błędy poprawności (kod krytyczny dla ryzyka)

**O co chodzi.** Rygorystyczny przegląd poprawności ścieżek trening↔inferencja:
inżynieria cech, tensory LSTM, skalery, NaN/inf.

**Prompt (użyty):**

```text
Pracuj na wysokim wysiłku. Zrób rygorystyczny przegląd poprawności kodu ML
krytycznego dla ryzyka w tym repo. Potrzebuję tego pewnego przed obroną pracy.

Pliki do skupienia:
- ml-service/features.py i ml-service/app.py — logika engineer_features()
  (statystyki płatności, trendy rachunków, wskaźnik wykorzystania, liczby
  opóźnień) oraz prepare_lstm_input(), które kształtuje 6-miesięczne sekwencje
  w tensor (1, 6, 3).
- ml-service/sliding_window.py — logika okna 3-miesięcznego.
- Obsługa skalerów: lstm_scalers_w3.pkl / scaler_w3.pkl są zapisane wcześniej
  i stosowane przy inferencji, NIE dopasowywane ponownie. Sprawdź, czy kod
  faktycznie tak robi.

Sprawdź w szczególności:
- Niezgodności kolejności cech lub wyrównania kolumn między treningiem
  (ml-learing-center/) a inferencją (ml-service/).
- Błędy o jeden lub złą oś w sekwencji 6-miesięcznej / reshape do (1, 6, 3).
- Skew treningu/inferencji w skalowaniu (przypadkowe ponowne dopasowanie, zły
  skaler, wyciek danych).
- NaN / dzielenie przez zero w cechach pochodnych (np. wskaźnik wykorzystania).

Zgłoś KAŻDE ustalenie, którego nie jesteś pewien, że jest OK, z: file:line,
opisem obawy, poziomem pewności, wagą i konkretną poprawką. Nie filtruj wstępnie
pod kątem ważności — ja to zrobię. To nie jest przegląd bezpieczeństwa; skup się
na poprawności.
```

## Wykonanie — raport (oryginalnie: sekcja Task 3 (ten plik))

### Raport (oryg. sekcja Task 3 (ten plik)) — Rygorystyczny przegląd poprawności kodu ML (trening ↔ inferencja)

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
z sekcja Task 1 (ten plik). Nie bug — ale musi być opisane w rozdz. 3 pracy jako
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
   z ewentualnym B2 z sekcja Task 1 (ten plik) (progi na splicie kalibracyjnym), żeby
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
4. Dopisz do sekcja Task 3 (ten plik) sekcję "Status po naprawie" z datą, listą
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
## Epilog Zadania 3 (stan 2026-07-07)

Prompty O1–O4 wykonane: fix U1/U2 (stałe kategorie `UCI_CATEGORIES`, parytet
single-row↔batch = 0,0), hardening walidacji wejścia (O3), skalery po splicie
(O4, |ΔAUC| ≤ 0,0009), 8 testów parytetu w `ml-service/tests/
test_train_serve_parity.py` (w CI). Dane demo w Postgres wyczyszczone
i zseedowane ponownie po fixie (O5/P4). Ustalenia U5/U6/U14 (potwierdzenia
poprawności osi LSTM i transform-only skalerów) można cytować na obronie.

---

# ZADANIE AD-HOC — Audyt wykonania sprintów (CHECKLIST.md vs stan repo)

**O co chodzi.** Zadanie spoza pierwotnej listy: weryfikacja wszystkich 26 zadań
CREDIT oznaczonych 🟢 przeciwko artefaktom, analiza ryzyk istniejącej
i proponowanej implementacji, prompty naprawcze.

**Prompt (użyty):** *„Zobacz jak dotychczasowo zostały wykonane sprinty
w CHECKLIST.md, używając wysokiego wysiłku sprawdź i przeanalizuj wykonanie tych
zadań, utwórz plik [raport] w którym opiszesz swoje wnioski oraz gotowe prompty
dla Opusa 4.8 do wprowadzenia zmian, opisz jakie ryzyko występuje z istniejącej
oraz proponowanej implementacji."*

## Wykonanie — raport (oryginalnie: sekcja Task 4 (ten plik))

### Raport (oryg. sekcja Task 4 (ten plik)) — Audyt wykonania sprintów (CHECKLIST.md vs stan faktyczny repo)

> **Autor:** Claude Fable 5 · **Data:** 2026-07-07
> **Zakres:** weryfikacja wszystkich 26 zadań oznaczonych 🟢 w `CHECKLIST.md` przeciwko
> kodowi, artefaktom, testom i historii gita; analiza ryzyk istniejącej implementacji
> i ryzyk proponowanych zmian; gotowe prompty dla Opusa 4.8.
> **Metoda weryfikacji:** `git log` (pełna historia, rozkład dat commitów), inspekcja
> plików per DoD zadania (CI workflow, docker-compose, DTO backendu, typy TS frontendu,
> kontrakt API, artefakty modeli, raporty), zliczenie testów (`[Fact]`/`[Theory]`
> w xUnit, `test(`/`it(` w Vitest), porównanie liczb z CHECKLIST z faktycznymi
> wartościami w `alert_thresholds.json` i `reports/*.md`. Kontekst z wcześniejszych
> audytów: sekcja Task 1 (ten plik) (praca vs kod), sekcja Task 3 (ten plik) (poprawność ML).

---

## 1. Werdykt ogólny

**Wykonanie zadań jest w przeważającej mierze rzetelne** — na 26 zadań 🟢
zweryfikowałem artefakty każdego i wszystkie ISTNIEJĄ i robią to, co deklaruje
CHECKLIST. Liczby testów zgadzają się co do sztuki (backend 24, frontend 34).
Znalazłem jednak: (a) **trzy rozbieżności liczbowe** między CHECKLIST a artefaktami
(przestarzałe wpisy sprzed re-runu CREDIT-109), (b) **anomalię osi czasu** — całość
„Sprintów 1–5" (kalendarzowo: 2 cze – 10 sie) została wykonana w **6 dni**
(2026-06-01…06-06), co git bezlitośnie pokaże każdemu, kto sprawdzi, (c) **lukę
CI** — testy `ml-learing-center` nie są uruchamiane w pipeline, oraz (d) fakt, że
wszystkie zadania serwingowe (104→202→203→302→303→211) stoją na ścieżce inferencji
dotkniętej krytycznym bugiem U1 z sekcja Task 3 (ten plik) — **w tym dane zapisane w
PostgreSQL, które po naprawie buga staną się nieaktualne**.

---

## 2. Weryfikacja per zadanie

### Sprint 1 (deklarowane 2–15 cze; faktycznie zmergeowane 2026-06-01…06-02)

| Task | Deklaracja | Weryfikacja | Status |
|---|---|---|---|
| CREDIT-101 | `extract_windows()` + test pytest | `sliding_window.py` ✓ (4 okna W0–W3, poprawne mapowanie kolumn — zweryfikowane w Task3/U5); `sliding_window_test.py` istnieje, **ale nie jest uruchamiany w CI** (ci.yml testuje tylko `ml-service/`) | ✅ z luką CI |
| CREDIT-102 | Retrain W3, artefakty `_w3`, fix mismatchu | Artefakty `_w3` ✓ (10 plików); fix `utilization_rate`/`severe_late` potwierdzony (Task3/U14: parytet trening↔inferencja) | ✅ |
| CREDIT-103 | ≥9 wykresów + metryki | `reports/` zawiera 40+ plików: metrics_w3.csv, roc/pr/calibration/ks/confusion per model ✓ | ✅ |
| CREDIT-201 | xUnit+pytest+Vitest+CI | `.github/workflows/ci.yml` ✓ (3 joby: backend/.NET, ml-service/pytest, frontend) | ✅ |
| CREDIT-401 | Schemat Postgres + EF Core | `backend/WebApi/Data`, `Models`, `Migrations` ✓ | ✅ |
| CREDIT-402 | docker-compose db+backend+ml-service | `docker-compose.yml` ✓ (postgres:16 z healthcheck, backend z auto-migracją przez env, frontend poza compose zgodnie z DoD) | ✅ |

### Sprint 2 (deklarowane 16–29 cze; faktycznie 2026-06-03…06-04)

| Task | Weryfikacja | Status |
|---|---|---|
| CREDIT-210 | `docs/api-contracts/monitoring.md` — 491 linii, 4 endpointy ✓ | ✅ |
| CREDIT-104 | `/predict/timeseries` w `app.py:304-375` ✓ (4 okna, trendy, alerty) | ✅ ale dotknięty U1 |
| CREDIT-105 | Kalibracja izotoniczna w `main.py:202-360` ✓ (CalibratedClassifierCV+FrozenEstimator, 3-way split, LSTM external calibrator) | ✅ z zastrz. U4 (skalery przed splitem) |
| CREDIT-202 | Kontroler + `MonitoringTimeseriesTests.cs` (4 testy) ✓ | ✅ |
| CREDIT-203 | Repozytoria + `SnapshotPersistenceTests.cs` (4 testy) ✓ | ✅ z ryzykiem R5 (brak transakcji) |

### Sprint 3 (deklarowane 30 cze–13 lip; faktycznie 2026-06-04…06-05)

| Task | Weryfikacja | Status |
|---|---|---|
| CREDIT-110 | `timeseries_eval.py` + `lead_time_report.md` ✓; liczby CHECKLIST (~50% catch, lead ~2.05, slope_auc ~0.59) zgodne z raportem | ✅ |
| CREDIT-111 | `static_vs_dynamic.py` + raport + 5 PNG ✓; **ALE** liczby w CHECKLIST przestarzałe — patrz §3.2 | ⚠️ rozbieżność |
| CREDIT-106 | `alert_thresholds.json` ✓; **ALE** CHECKLIST podaje LSTM=0.185, plik zawiera **0.175** — patrz §3.1 | ⚠️ rozbieżność |
| CREDIT-204 | `ClientHistoryTests.cs` (5 testów) ✓ | ✅ |
| CREDIT-301 | `TimelineChart.tsx`+`TrendAlerts.tsx`+`monitoringApi.ts` ✓ | ✅ |

### Sprint 4 (deklarowane 14–27 lip; faktycznie 2026-06-03…06-05)

| Task | Weryfikacja | Status |
|---|---|---|
| CREDIT-302 | `ClientList.tsx`+`ClientHistory.tsx` + testy (4+6) ✓ | ✅ |
| CREDIT-205 | `PersistenceTests.cs` — 8 `[Fact]` ✓, Testcontainers; „atomowa transakcja świadomie odłożona" — nadal odłożona (R5) | ✅ |
| CREDIT-107 | SHAP w `app.py:61-233` ✓ (4 explainery, top-5) | ✅ z zastrz. U9/U10 |
| CREDIT-108 | `optuna_tuning.py` + `reports/optuna_study.md` + `optuna_trials.csv` ✓; tuned świadomie niepromowane (udokumentowane w main.py:443-448) | ✅ |

### Sprint 5 (deklarowane 28 lip–10 sie; faktycznie 2026-06-05…06-06)

| Task | Weryfikacja | Status |
|---|---|---|
| CREDIT-303 | `SnapshotForm.tsx` + testy (5) ✓ | ✅ |
| CREDIT-211 | `ShapExplanation.tsx` (7 testów) + DTO `Shap` w backendzie ✓ | ✅ |
| CREDIT-109 | 5 modeli w `app.py` ✓, CatBoost AUC 0.7802 zgodne z `metrics_w3.csv` | ✅ |
| CREDIT-112 | Pełny audyt zweryfikowany w sekcja Task 2 (ten plik) ✓ | ✅ z zastrz. (SEX w cechach, progi z testu) |
| CREDIT-115 | `TimeseriesResponse.cs` zawiera Lightgbm/Catboost ✓ | ✅ |
| CREDIT-116 | `ModelKey = 'randomForest'\|'xgboost'\|'lightgbm'\|'catboost'\|'lstm'` w `monitoring.ts` ✓ | ✅ |

**Liczby testów — pełna zgodność z deklaracjami:** backend 4+2+5+8+4+1 = **24**
(CHECKLIST: „16 → 24"); frontend 1+4+6+5+3+5+7+3 = **34** (CHECKLIST: „27→34"). ✓

### Sprint 6 — otwarte

- 🔴 CREDIT-113 (stacking, P2) — **blokuje** 🔒 CREDIT-114 (final report, **P0, ścieżka krytyczna tezy**).
- 🔴 CREDIT-304 (UI polish, P2), 🔒 CREDIT-501 (docs, P0 — m.in. aktualizacja CLAUDE.md).
- **CLAUDE.md jest rażąco przestarzały**: opisuje „ensemble of 3 ML models", nie zna
  endpointów monitoringu, bazy PostgreSQL ani okna 3-mies. — czyli dokument sterujący
  narzędziami AI w repo opisuje system sprzed 5 sprintów.

---

## 3. Rozbieżności CHECKLIST/dokumentacja vs artefakty

### 3.1. CREDIT-106 — próg LSTM

CHECKLIST (linia 106): „RF=0.145 / XGB=0.180 / **LSTM=0.185**".
`ml-service/alert_thresholds.json`: LSTM = **0.175** (oraz LGBM=0.16, CatBoost=0.13,
których wpis w ogóle nie wymienia). Przyczyna: wpis z pierwotnego runu 3-modelowego,
nieodświeżony po re-runie w CREDIT-109. **Ryzyko:** liczba 0.185 mogła trafić do
podsumowań sprintów/prezentacji/pracy.

### 3.2. CREDIT-111 — zakres wyników static-vs-dynamic

CHECKLIST (linia 102): „monitoring tracił **2-6pp** catch vs static" oraz „**43-184
unikalnych catchy/model**". Faktyczny `reports/static_vs_dynamic_report.md`:
strata przy FA=10% wynosi **1.3–7.7 pp** (LSTM −7.69), a lead-only wins to
**36–72/model** (CatBoost 36, RF 72). Liczby w CHECKLIST pochodzą z runu sprzed
CREDIT-109. Dodatkowo nagłówek samego raportu mówi „W3-calibrated **RF/XGB/LSTM**"
(3 modele), choć ciało raportu ma 5 — przestarzały nagłówek.

### 3.3. Oś czasu sprintów — kalendarz vs git

Rozkład dat commitów (pełna historia): grudzień 2025–kwiecień 2026 = system legacy
(3 modele); następnie **cała realizacja „Sprintów 1–5" w 6 dni: 2026-06-01…06-06**
(83 commity, PR #4–#40), podczas gdy CHECKLIST/plan deklarują 5×2 tygodnie
(2 cze – 10 sie). Od 6 czerwca do dziś (7 lipca) — miesiąc przerwy, prace Sprintu 6
nierozpoczęte. **Ryzyko na obronie:** jeśli praca (rozdz. 3.6) opisze metodykę
„6 sprintów × 2 tygodnie, GitHub Flow", a komisja zajrzy do publicznego repo,
git przeczy narracji. To samo dotyczy CHECKLIST-owych dat sprintów.

### 3.4. Luka CI

`ci.yml` uruchamia pytest tylko w `ml-service/`. Testy `ml-learing-center/`
(`sliding_window_test.py`) i cała warstwa treningowo-ewaluacyjna nie są objęte CI —
DoD CREDIT-101 („+ test pytest") jest spełnione literalnie (test istnieje), ale nie
duchowo (nic go nie uruchamia automatycznie).

---

## 4. Ryzyka ISTNIEJĄCEJ implementacji

| ID | Ryzyko | Dotknięte zadania | Waga | Szczegóły |
|---|---|---|---|---|
| R1 | **Train/serve skew (U1 z Task3): serving zeruje demografie** — każda predykcja przez Flask, każdy snapshot zapisany do Postgres, każdy SHAP w UI policzony na wyzerowanych SEX/EDUCATION/MARRIAGE | 104, 202, 203, 302, 303, 211, 115, 116 | **Krytyczna** | 3% klientów zmienia decyzję alertu; **dane w DB są skażone** — po fixie wymagają re-scoringu; demo na obronie ≠ raporty |
| R2 | **Progi kosztowe optymalizowane na zbiorze testowym** (main.py:406-413), na którym potem liczone są fairness (112) i static-vs-dynamic (111) | 106, 111, 112 | Wysoka | Wyciek progu; praca sama ostrzega przed tym błędem w 4.1.1 |
| R3 | **Skalery fitowane przed splitem** (main.py:77, 233, 312) | 102, 105 | Średnia | Sprzeczne z deklaracją „zamrożonego" testu; liczbowo znikome |
| R4 | **Framing CREDIT-111 rozjechany z danymi**: „comparable discrimination" przy stracie do 7.7 pp @FA=10% u wszystkich 5 modeli + przestarzałe liczby w CHECKLIST | 111, 114 | Wysoka | Hipoteza H2 musi być sformułowana wokół wczesności/unikalnych wykryć ZANIM komisja zobaczy liczby |
| R5 | **Brak transakcji atomowej w zapisie migawki** (świadomie odłożone w CREDIT-205, nigdy niedomknięte): snapshot + 5 predykcji + 5 trendów zapisywane osobno | 203, 205 | Średnia | Awaria w połowie zapisu = niespójna trajektoria w DB; brak taska follow-up |
| R6 | **CREDIT-113 (P2) blokuje CREDIT-114 (P0)** — ogon ścieżki krytycznej tezy wisi na zadaniu o najniższym priorytecie | 113, 114 | Wysoka (terminowa) | Miesiąc bez commitów; raport finalny (baza rozdz. 5) nie istnieje |
| R7 | **Dokumentacja przestarzała**: CLAUDE.md (3 modele, brak DB/monitoringu), nagłówek static_vs_dynamic_report.md, wpisy CHECKLIST §3.1–3.2 | 501 | Średnia | Błędne liczby mogą propagować do pracy/prezentacji; narzędzia AI w repo dostają fałszywy kontekst |
| R8 | **CI nie chroni warstwy ML**: brak testów parytetu batch↔serving (dlatego R1 przeszedł), testy ml-learing-center poza pipeline | 201 | Średnia | Każdy fix z tego audytu może cicho zregresować |
| R9 | Oś czasu git vs deklarowany kalendarz sprintów (§3.3) | narracja pracy | Średnia | Ryzyko wizerunkowe na obronie, łatwe do uprzedzenia |
| R10 | Legacy `/predict` (nieskalibrowane modele, próg 0.5) współistnieje z W3 — dwa endpointy dają sprzeczne decyzje dla tego samego klienta | 104 | Niska | Świadome legacy; wymaga adnotacji, nie kodu |

## 5. Ryzyka PROPONOWANYCH zmian (czego pilnować przy naprawie)

| ID | Zmiana | Ryzyko wtórne | Mitygacja |
|---|---|---|---|
| P-A | Fix U1 (stałe kategorie w one-hot) | (1) Dane w Postgres zapisane przed fixem stają się niespójne z nowymi predykcjami — historia klienta pokaże skok PD nie wynikający z zachowania; (2) zrzuty SHAP/PD w `prezentacja_seminarium/` przestają odpowiadać systemowi; (3) zmiana kolejności kolumn dummy przy nieostrożnej implementacji złamie `scaler_w3` | Re-scoring lub czyszczenie danych demo w DB (prompt O5 w Task3 + P4 niżej); regeneracja zrzutów; test parytetu PRZED merge |
| P-B | Przeliczenie progów na splicie kalibracyjnym (R2) | Kaskada zmian liczb: `alert_thresholds.json` → fairness → static-vs-dynamic → CHECKLIST → podsumowania sprintów → praca → prezentacja. Zrobione częściowo = gorsze niż wcale (dwa niespójne zestawy liczb w obiegu) | Jeden atomowy re-run wszystkich raportów + jeden commit aktualizujący wszystkie dokumenty (prompt P2) |
| P-C | Retrain ze skalerami po splicie (R3) | Wszystkie artefakty modeli się zmieniają (nowe wagi), metryki drgną o ~0.001; jeśli praca już cytuje stare liczby — rozjazd | Wykonać RAZEM z P-B (jeden retrain, jedna regeneracja); porównanie przed/po jako dowód znikomości do pracy; albo świadomie NIE robić i opisać w pracy jako ograniczenie |
| P-D | Descope CREDIT-113 (stacking) i odblokowanie 114 | Zmiana grafu zależności w TASKS/CHECKLIST; „ostatnie ogniwo" znika z narracji; jeśli praca obiecuje ensemble — luka | Udokumentowana decyzja zakresu (P2 poniżej); w pracy jedno zdanie w „kierunkach dalszych badań" |
| P-E | Jeśli jednak robić CREDIT-113: stacking wymaga predykcji out-of-fold | Meta-learner trenowany na predykcjach z tego samego zbioru, na którym trenowano modele bazowe = wyciek; trenowany na teście = dyskwalifikacja; dodatkowo psuje historię kalibracji | Protokół OOF na części treningowej + kalibracja meta-modelu na splicie kalibracyjnym (prompt P6) |
| P-F | Transakcja atomowa w `ScoreAndPersistAsync` (R5) | Zmiana zachowania współbieżnego; EF InMemory nie testuje transakcji — pozorna zieleń | Testy na Testcontainers (harness z CREDIT-205 już to umie) — wymusić test rollbacku |
| P-G | Aktualizacja CLAUDE.md/README (R7) | Niska — czysto dokumentacyjna; jedyne ryzyko to utrwalenie liczb, które P-B za chwilę zmieni | Wykonać PO P-A/P-B, nie przed |

**Zależność nadrzędna:** P-A i P-B zmieniają liczby, na których stoją dokumenty
i praca. Dlatego kolejność: **naprawy kodu → jeden re-run wszystkich raportów →
dopiero potem aktualizacja dokumentów i tekstu pracy.** Odwrotna kolejność = podwójna robota.

---

## 6. Gotowe prompty dla Opusa 4.8

Wklejać pojedynczo, w podanej kolejności. Prompty P1–P3 są bezpieczne (dokumentacja
i porządek), P4–P6 zmieniają kod/dane. Prompty O1–O5 z sekcja Task 3 (ten plik) oraz
B1–B4/F1–F4 z Task1/Task2 pozostają w mocy — poniżej tylko NOWE zadania z tego audytu.

### P1 — Naprawa rozbieżności liczbowych w CHECKLIST i raportach (R7, §3.1–3.2)

```text
W repo są przestarzałe liczby z runu 3-modelowego sprzed CREDIT-109. Napraw:
1. CHECKLIST.md linia ~106 (CREDIT-106): zamień "RF=0.145 / XGB=0.180 / LSTM=0.185"
   na pełne 5 progów z ml-service/alert_thresholds.json (odczytaj plik — obecnie:
   RF=0.145, XGB=0.180, LGBM=0.160, CatBoost=0.130, LSTM=0.175).
2. CHECKLIST.md linia ~102 (CREDIT-111): zamień "2-6pp" i "43-184 unikalnych
   catchy/model" na wartości z reports/static_vs_dynamic_report.md (straty @FA=10%:
   1.3-7.7 pp; lead-only wins: 36-72/model — zweryfikuj czytając raport, nie ufaj
   tym liczbom w ciemno).
3. reports/static_vs_dynamic_report.md nagłówek: "W3-calibrated RF/XGB/LSTM" →
   wymień 5 modeli (raport w ciele ma 5 sekcji).
4. Przeszukaj (grep) PodsumowanieSprintu*.md, prezentacja_seminarium/ i
   plan_sprintow_wariant_B.md pod kątem tych samych przestarzałych liczb
   (0.185, "2-6pp", "43-184", "43", "184") i popraw analogicznie, wypisując
   listę wszystkich miejsc, które zmieniłeś.
Nie zmieniaj żadnych plików w reports/ poza nagłówkiem z pkt 3 (to artefakty
runów — poprawiamy tylko opisy, nie dane). Jeden commit:
"docs: reconcile CHECKLIST/summaries with post-CREDIT-109 artifacts".
```

### P2 — Decyzja zakresu: descope CREDIT-113, odblokowanie CREDIT-114 (R6)

```text
CREDIT-113 (stacking, P2) blokuje CREDIT-114 (final report, P0, ścieżka krytyczna
tezy), a Sprint 6 się nie rozpoczął. Wykonaj kontrolowany descope:
1. W TASKS.md i CHECKLIST.md: przenieś CREDIT-113 do nowej sekcji "Descoped /
   Backlog po obronie" ze statusem ⚪ i adnotacją: "Świadoma decyzja zakresu
   2026-07-07: stacking nie wnosi do dowodu tezy (H1/H2/H3 nie wymagają
   ensemble), a wymaga protokołu OOF + rekalibracji; przeniesione do kierunków
   dalszych badań."
2. Usuń 113 z blocked_by CREDIT-114 (zostaje: 103, 111) i zmień status 114
   z 🔒 na 🔴; zaktualizuj "Aktualne zadanie" GF na CREDIT-114, statystyki
   (26/2/2 → odpowiednio) i ścieżkę krytyczną (101→102→104→110→111→114 bez
   zmian — 113 nigdy na niej nie było, popraw tylko dopisek "ostatnie ogniwo").
3. Zaktualizuj datę "Ostatnia aktualizacja" z opisem zmiany.
4. W plan_sprintow_wariant_B.md dodaj analogiczną adnotację przy CREDIT-113,
   jeśli plik go wymienia (sprawdź grepem).
Jeden commit: "chore: descope CREDIT-113 (stacking) — unblock CREDIT-114 final
report (P0 critical path)".
```

### P3 — Wykonanie CREDIT-114: generator raportu finalnego (R6)

```text
Zrealizuj CREDIT-114 (final report) na branchu sprint6/final-report. Napisz
ml-learing-center/final_report.py, który NIE trenuje niczego, tylko agreguje
istniejące artefakty do jednego raportu:
1. Wczytaj: reports/metrics_w3.csv, fairness_metrics_w3.csv,
   static_vs_dynamic_metrics.csv i _operating.csv, timeseries_metrics.csv,
   optuna_trials.csv, alert_thresholds.json.
2. Wygeneruj reports/FINAL_REPORT.md z sekcjami mapującymi się 1:1 na strukturę
   rozdz. 5 pracy: (a) tabela 5 modeli × AUC/Gini/KS/Brier + wskazanie
   najlepszego, (b) progi kosztowe + interpretacja, (c) static vs monitoring —
   tabela catch rate @FA=5/10/20% per model + lead-only wins + mean lead time,
   Z UCZCIWYM werdyktem per model (przy FA=10% statyka wygrywa u wszystkich —
   napisz to wprost, framing: komplementarność i wczesność, nie wyższość),
   (d) fairness DPD/EOD per model + per-group breakdown, (e) weryfikacja
   hipotez H1/H2/H3 (H1: porównaj z liczbami legacy w PodsumowanieSprintu1.md;
   H2: potwierdzona częściowo — wczesność tak, catch rate nie; H3: potwierdzona),
   (f) ograniczenia (jeden zbiór, symulowany monitoring, progi z testu jeśli
   jeszcze nienaprawione — sprawdź w main.py czy CREDIT-106 liczy na y_te_w3
   czy y_cal_w3 i napisz zgodnie ze stanem faktycznym).
3. Każda liczba w raporcie MUSI pochodzić z odczytu plików, nie z pamięci/
   dokumentów — CHECKLIST zawiera przestarzałe wartości.
4. Zaktualizuj CHECKLIST.md (114 → 🟢, statystyki, data) zgodnie z workflow
   z sekcji "📝 Workflow aktualizacji checklisty".
Wynik: PR z final_report.py + FINAL_REPORT.md + aktualizacja CHECKLIST.
```

### P4 — Higiena danych w Postgres po fixie U1 (P-A)

```text
Kontekst: naprawiono (lub zaraz zostanie naprawiony — sprawdź stan
ml-service/features.py: czy get_dummies dostaje pd.Categorical ze stałymi
kategoriami) bug zerowania cech demograficznych w inferencji Flask. Wszystkie
snapshoty zapisane w PostgreSQL przed fixem mają predykcje policzone błędną
ścieżką. Zaprojektuj i wykonaj higienę danych:
1. Napisz backend/WebApi narzędzie lub skrypt SQL+HTTP (wybierz prostsze:
   jednorazowy skrypt .NET w stylu istniejących narzędzi lub skrypt Pythona
   wołający POST /predict/timeseries), który: (a) wylistuje wszystkich klientów
   i ich snapshoty (GET /api/v1/monitoring/clients + history), (b) dla każdego
   snapshotu ponownie zescoruje 22 cechy przez naprawiony serwis, (c) porówna
   stare vs nowe PD i wypisze tabelę różnic per snapshot.
   UWAGA: history endpoint zwraca tylko PD, nie surowe cechy — sprawdź w
   schemacie DB (backend/WebApi/Models, Migrations), czy Snapshot przechowuje
   22 cechy wejściowe. Jeśli TAK: re-scoring z danych DB. Jeśli NIE: re-scoring
   niemożliwy — jedyną czystą opcją jest TRUNCATE danych demo + ponowny seed
   (ml-learing-center/seed_demo_clients.py); udokumentuj to i wykonaj wariant
   możliwy.
2. Dodaj do docs/api-contracts/monitoring.md krótką adnotację "Data note:
   snapshoty sprzed <data fixu> zostały przeliczone/wyczyszczone po naprawie
   train/serve skew (sekcja Task 3 (ten plik) U1)".
3. Nic nie usuwaj bez wypisania najpierw, co zostanie usunięte, i zatrzymania
   się, jeśli w DB są dane inne niż demo/seed.
```

### P5 — Domknięcie CI: warstwa ML + transakcja atomowa (R5, R8)

```text
Dwa domknięcia higieny inżynierskiej:
1. CI dla ml-learing-center: w .github/workflows/ci.yml dodaj job
   ml-training-tests uruchamiający pytest w ml-learing-center/ (przynajmniej
   sliding_window_test.py; sprawdź, czy inne pliki *_test.py istnieją).
   UWAGA na koszt: NIE instaluj tensorflow/catboost, jeśli testy ich nie
   importują — sprawdź importy testów i zainstaluj minimalny zestaw
   (prawdopodobnie sam pandas/numpy/pytest wystarczy; jeśli testy ciągną
   features.py, dojdzie scikit-learn). Jeśli import main.py jest nieunikniony —
   pomiń ten test w CI z komentarzem zamiast instalować 2 GB zależności.
2. Transakcja atomowa w zapisie migawki (odłożona w CREDIT-205):
   w MonitoringService.ScoreAndPersistAsync (backend/WebApi/Services) opakuj
   zapis Snapshot + 5 Predictions + 5 Trends w jawną transakcję EF Core
   (Database.BeginTransactionAsync / commit / rollback). Zachowaj istniejące
   zachowanie 409 CONFLICT. Dodaj test do PersistenceTests.cs (harness
   Testcontainers już jest): symuluj błąd po zapisie snapshotu a przed
   predykcjami (np. przez podklasę serwisu lub wstrzyknięcie złych danych)
   i asertuj, że w DB nie ma osieroconego snapshotu. EF InMemory NIE testuje
   transakcji — test musi być w klasie z PostgresFixture.
Uruchom testy backendu i pokaż wynik. Dwa osobne commity.
```

### P6 — (opcjonalnie, tylko jeśli decyzja = jednak robić stacking) CREDIT-113 bez wycieku

```text
Jeśli zapadła decyzja o realizacji CREDIT-113 (stacking) zamiast descope:
zaimplementuj w ml-learing-center/stacking.py protokół bez wycieku:
1. Na części TRENINGOWEJ (60%, odtwórz split z main.py random_state=42):
   predykcje out-of-fold (5-fold StratifiedKFold) 5 modeli bazowych
   (retrenowanych per fold z hiperparametrami z main.py — dla LSTM dopuszczalne
   uproszczenie: mniejsza liczba epok, odnotuj) jako macierz cech meta 5 kolumn.
2. LogisticRegression jako meta-learner na OOF; kalibracja meta-modelu na
   splicie kalibracyjnym (20%); ewaluacja WYŁĄCZNIE na teście (20%).
3. Raport reports/stacking_report.md: AUC/Brier stacking vs najlepszy pojedynczy
   (CatBoost 0.7802) + wniosek. Oczekiwanie realistyczne: zysk 0-0.3 pp —
   jeśli stacking NIE wygrywa, napisz to wprost (to też jest wynik do pracy).
4. NIE podłączaj stackingu do ml-service/ bez osobnej decyzji — to eksperyment
   do rozdz. 5, nie zmiana produkcyjna (uzasadnienie: wymagałby 6. progu
   kosztowego, SHAP nie działa na meta-modelu wprost, DTO 5-modelowe by się
   zmieniło).
Zabezpieczenie: meta-learner NIGDY nie widzi predykcji policzonych na danych,
na których bazowy model był trenowany, ani żadnych danych testowych przed
finalną ewaluacją.
```

### P7 — Aktualizacja CLAUDE.md i realizacja CREDIT-501 (R7) — wykonać PO P1–P5

```text
Zrealizuj dokumentacyjną część CREDIT-501: przepisz CLAUDE.md tak, by opisywał
FAKTYCZNY stan systemu (obecny opisuje wersję sprzed 5 sprintów):
1. Przeczytaj: docker-compose.yml, docs/api-contracts/monitoring.md,
   ml-service/app.py (endpointy i ładowane artefakty), backend/WebApi/
   (kontrolery, DTO), frontend/WebApp/src (komponenty), CHECKLIST.md.
2. Zaktualizuj: (a) opis systemu — 5 modeli (RF/XGB/LightGBM/CatBoost/LSTM),
   okno przesuwne W0..W3, kalibracja izotoniczna, progi kosztowe, monitoring
   trajektorii PD; (b) tabela serwisów + PostgreSQL 16 (5432) + docker-compose;
   (c) endpointy: /predict (legacy), /predict/timeseries, /api/v1/monitoring/*
   (4 endpointy z kontraktu); (d) komponenty frontendu (Timeline, ClientList,
   ClientHistory, SnapshotForm, ShapExplanation, TrendAlerts); (e) komendy
   dev bez zmian, dodaj docker compose up i pytest/dotnet test/vitest;
   (f) sekcja "Znane ograniczenia" z odnośnikami do Fable5_Task1/2/3.md
   i sekcja Task 4 (ten plik). Zachowaj zwięzłość CLAUDE.md (to instrukcje dla narzędzi,
   nie dokumentacja) — szczegóły linkuj do monitoring.md i README.
3. Uzupełnij README.md o krótki opis Wariantu B + instrukcję uruchomienia
   end-to-end, oraz utwórz docs/MODEL_CARD.md (5 modeli: dane, okno W3,
   kalibracja, progi, metryki z reports/metrics_w3.csv, fairness z
   fairness_metrics_w3.csv, ograniczenia — liczby CZYTAJ z plików).
4. Zaktualizuj CHECKLIST.md (501 → 🟢 jeśli DoD spełnione, statystyki, data).
```

---

## 7. Rekomendowana kolejność wykonania (całość planu naprawczego)

| Krok | Zadanie | Źródło promptu | Zmienia liczby? |
|---|---|---|---|
| 1 | O1+O2 (fix U1 + testy parytetu) | Task3 | Tylko serving (nie raporty) |
| 2 | P4 (higiena DB po fixie) | Task4 | Dane demo |
| 3 | B2/F2 (progi na splicie kalibracyjnym) + opcjonalnie O4 (skalery) | Task1/Task2/Task3 | **TAK — wszystkie raporty** |
| 4 | Jeden re-run: main.py → evaluation → fairness → timeseries → static_vs_dynamic | (część B2/O4) | — |
| 5 | P1 (rekonsyliacja liczb w dokumentach) | Task4 | Dokumenty |
| 6 | P2 (descope 113) **albo** P6 (stacking OOF) | Task4 | — / raport |
| 7 | P3 (CREDIT-114 final report) | Task4 | Nowy raport |
| 8 | P5 (CI + transakcja) | Task4 | — |
| 9 | P7 (CLAUDE.md/README/Model Card — CREDIT-501) | Task4 | — |
| 10 | Pisanie rozdz. 3/5 pracy (E1/E2 z Task1, proza z Task2) | Task1/Task2 | — |

Zasada: **kroki 1–4 przed jakimkolwiek pisaniem liczb do pracy** — inaczej każda
zmiana progu/skalera unieważnia napisane akapity.

---

## 8. TL;DR dla autora

1. **Zadania są wykonane naprawdę** — wszystkie 26 🟢 ma artefakty, testy zgadzają
   się co do sztuki; zespół ma prawo mówić o rygorze inżynierskim (CI, Testcontainers,
   kontrakt API, PR flow).
2. **Ale trzy wpisy CHECKLIST kłamią liczbowo** (progi LSTM, zakresy CREDIT-111) —
   to pozostałości sprzed CREDIT-109; naprawa to 15 minut (P1), a nienaprawione
   mogą wciec do pracy.
3. **Git ujawnia, że „5 sprintów" to 6 dni pracy** — przygotuj uczciwą narrację
   (np. „plan sprintowy jako struktura zakresu, realizacja skompresowana") zamiast
   liczyć, że nikt nie sprawdzi.
4. **Największe ryzyko techniczne pozostaje w serwingu (U1)** — i rozlewa się na
   dane w Postgres oraz każde demo; napraw przed obroną, potem wyczyść DB.
5. **Ścieżka krytyczna tezy stoi**: CREDIT-114 (P0) czeka na CREDIT-113 (P2) od
   miesiąca. Descope 113 (P2) i zrób 114 (P3) — to jedyne, co realnie blokuje
   rozdział 5 pracy.

## Epilog Zadania ad-hoc (stan 2026-07-07)

Prompty P1–P5 i P7 wykonane: rekonsyliacja liczb w dokumentach, descope
CREDIT-113 (backlog po obronie), CREDIT-114 (`final_report.py` →
`reports/FINAL_REPORT.md`), higiena danych demo w Postgres, job CI dla warstwy
treningowej + transakcja atomowa zapisu migawki z testem rollbacku na
Testcontainers, CREDIT-501 (README / MODEL_CARD / ARCHITECTURE / CLAUDE.md).
P6 (stacking OOF) nieaktualny po descope. Stan projektu: 28/30 zadań zielonych,
0 zablokowanych; otwarty wyłącznie CREDIT-304 (UI polish). Podsumowania
sprintów scalono w `PodsumowanieSprintow.md`.
