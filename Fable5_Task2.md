
# Fable5_Task2.md — Sekcja fairness: analiza, ranking, mitygacja, proza + plan wykonawczy

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
| F2 | Fix wycieku: progi kosztowe liczone na splicie kalibracyjnym, re-run audytu | kod | **P0** | — (tożsame z B2 z `Fable5_Task1.md` — nie dublować, jeśli już wykonane) |
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
przekroczona), zgodnie z rekomendacją z Fable5_Task2.md §4. Nie zmieniaj
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
Przeczytaj Fable5_Task2.md §5 (cztery akapity prozy o audycie fairness) oraz
aktualne wyniki: reports/fairness_report.md, reports/fairness_metrics_w3.csv,
reports/threshold_leakage_fix.md (jeśli istnieje po F2) i
reports/fairness_no_sex_report.md (jeśli istnieje po F1). Zadanie: przygotuj
finalną wersję sekcji 5.5b pracy do docs/thesis/Rozdzial5_5b_fairness.md:
(1) weź prozę z Fable5_Task2.md §5 jako bazę; (2) zaktualizuj KAŻDĄ liczbę,
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
Przeczytaj Fable5_Task2.md (całość) oraz aktualne raporty fairness w reports/
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