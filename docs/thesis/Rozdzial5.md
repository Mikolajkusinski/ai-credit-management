# Rozdział 5. Analiza wyników i ocena modeli (+ Zakończenie)

> **Draft do wklejenia (2026-07-07).** Wszystkie liczby pochodzą z kanonicznych
> artefaktów `ml-learing-center/reports/` (stan po naprawach metodologicznych
> 2026-07-07; agregacja: `FINAL_REPORT.md`). Miejsca na rysunki: `[RYS: ...]`.
> Nowe pozycje bibliografii: `[NOWE: Hardt 2016]`, `[NOWE: Bird 2020]`,
> `[NOWE: Zadrozny-Elkan 2002]`, `[NOWE: Akiba 2019]` — do dodania przy składzie.

## 5.1. Metryki oceny jakości modeli klasyfikacyjnych

### 5.1.1. Dokładność, precyzja, czułość, F1 — i dlaczego nie są metrykami wiodącymi

Przy rozkładzie klas 78/22 dokładność jest myląca: klasyfikator zwracający
zawsze klasę większościową osiąga 78% przy zerowej użyteczności biznesowej.
Precyzja, czułość i F1 zależą od progu klasyfikacyjnego, który w niniejszym
systemie nie jest stały (progi kosztowe per model, sekcja 4.7) — ich wartości
opisują więc punkt pracy, nie model. Z tych powodów metryki progowe pełnią
w pracy rolę pomocniczą (czułość i odsetek fałszywych alarmów raportowane są
w analizie reguł decyzyjnych, sekcja 5.4, oraz w audycie sprawiedliwości,
sekcja 5.5), a porównanie modeli opiera się na metrykach niezależnych od progu.

### 5.1.2. Krzywa ROC i pole pod krzywą (AUC-ROC)

AUC — prawdopodobieństwo, że losowy defaultujący otrzyma wyższe PD niż losowy
spłacający — jest niezależne od progu i proporcji klas, co czyni je standardem
porównawczym w credit scoringu [10]. Raportowane są także pochodne: Gini
(2·AUC − 1) oraz statystyka Kołmogorowa–Smirnowa (maksymalna separacja
dystrybuant wyników obu klas), tradycyjnie używane w praktyce bankowej.

### 5.1.3. Wynik Briera i macierz pomyłek

Ponieważ trajektoria PD wymaga skali absolutnej (rozdz. 4.6), obok zdolności
rankingowej oceniana jest jakość kalibracji — wynikiem Briera (średni kwadrat
odchylenia prognozy od wyniku binarnego; niższy = lepszy). Macierze pomyłek
prezentowane są przy progach kosztowych z sekcji 4.7, czyli w faktycznym
punkcie pracy systemu.

## 5.2. Wyniki modeli — zestawienie porównawcze

Wszystkie wyniki dotyczą zamrożonego zbioru testowego (6 000 klientów, w tym
1 327 defaultujących) i modeli po kalibracji izotonicznej.

**Tabela 5.1.** Metryki pięciu modeli W3 (test).

| Model | AUC | Gini | KS | Brier | Próg kosztowy |
|---|---:|---:|---:|---:|---:|
| Random Forest | 0,7741 | 0,548 | 0,408 | 0,1374 | 0,145 |
| XGBoost | 0,7761 | 0,552 | 0,423 | 0,1360 | 0,165 |
| LightGBM | 0,7767 | 0,553 | 0,417 | 0,1363 | 0,160 |
| **CatBoost** | **0,7793** | **0,559** | 0,415 | **0,1357** | 0,160 |
| LSTM | 0,7614 | 0,523 | 0,399 | 0,1388 | 0,155 |

**Random Forest** (5.2.1) osiąga AUC 0,7741 — najniższe wśród modeli
drzewiastych, przy najlepszej stabilności rankingu cech; jego ważności
(dominacja PAY_max, late_count, recent_pay_status) są punktem odniesienia dla
analizy interpretowalności. **XGBoost** (5.2.2, AUC 0,7761) i **LightGBM**
(5.2.3, AUC 0,7767) osiągają wyniki praktycznie nierozróżnialne — zgodnie
z oczekiwaniem dla dwóch implementacji tej samej idei wzmacniania
gradientowego na wspólnej przestrzeni cech. **CatBoost** (5.2.4) jest najlepszy
w obu wymiarach — dyskryminacji (AUC 0,7793) i kalibracji (Brier 0,1357).
**LSTM** (5.2.5, AUC 0,7614) zamyka stawkę: na tabelarycznych danych
kredytowych o zaledwie trzech krokach czasowych surowa sekwencja nie
rekompensuje braku ręcznie zaprojektowanych cech agregujących — wynik spójny
z literaturą benchmarkową wskazującą przewagę metod drzewiastych na danych
tabelarycznych [10], [11]. Model sekwencyjny wnosi jednak dwie unikalne
własności, omówione w sekcjach 5.4 (jedyny model, dla którego reguła
monitorująca wygrywa również na czułości) i 5.5 (najbliższy parytetu
demograficznego — jako jedyny nie otrzymuje na wejściu żadnych cech
demograficznych).

[RYS: roc_comparison_w3.png; pr_comparison_w3.png; calibration_comparison_w3.png]

## 5.3. Wzajemne porównanie pięciu modeli

Różnice AUC między modelami drzewiastymi (0,0026–0,0052) są małe, dlatego
zbadano ich istotność bootstrapem: 40 repróbkowań zbioru testowego ze
zwracaniem, w wariancie sparowanym dla różnic par modeli.

**Tabela 5.2.** Bootstrap AUC (40 powtórzeń; 95% przedziały percentylowe).

| Model | AUC | 95% CI |
|---|---:|---|
| Random Forest | 0,7741 | [0,765; 0,786] |
| XGBoost | 0,7761 | [0,767; 0,789] |
| LightGBM | 0,7767 | [0,766; 0,790] |
| CatBoost | 0,7793 | [0,770; 0,793] |
| LSTM | 0,7614 | [0,753; 0,772] |

Sparowane przedziały różnic prowadzą do trzech wniosków: (1) przewaga
CatBoost nad lasem losowym (+0,0051) i XGBoost (+0,0035) jest rozróżnialna
(przedziały nie zawierają zera), nad LightGBM — nie; (2) różnice w trójce
RF/XGBoost/LightGBM mieszczą się w szumie próbkowania i należy je raportować
jako porównywalne; (3) przewaga wszystkich modeli drzewiastych nad LSTM
(+0,013 do +0,018) jest wyraźna i stabilna. Bootstrap repróbkuje wyłącznie
zbiór testowy przy ustalonych modelach, nie obejmuje więc wariancji treningu.

## 5.4. Reguła statyczna (W3) vs reguła monitorująca (W0..W3) — weryfikacja empiryczna Wariantu B

Sekcja przeformułowana względem pierwotnego konspektu („porównanie
z klasycznymi metodami scoringowymi"): właściwym eksperymentem rozstrzygającym
tezę jest porównanie dwóch **reguł decyzyjnych** na tych samych modelach.
Reguła statyczna alarmuje, gdy PD najnowszego okna przekracza próg
(PD_W3 ≥ θ); reguła monitorująca — gdy próg przekracza PD któregokolwiek okna
(max(PD_W0..W3) ≥ θ). Ponieważ druga reguła jest nadzbiorem pierwszej (przy tym
samym progu flaguje co najmniej tyle samo osób, ale też generuje więcej
fałszywych alarmów), uczciwe porównanie wymaga wyrównania budżetu fałszywych
alarmów: progi θ dobierane są niezależnie dla każdej reguły tak, aby odsetek
fałszywych alarmów (FA) wśród spłacających wynosił zadane 5, 10 lub 20%.

**Tabela 5.3.** Zmiana czułości (monitoring − statyka, pp) przy zadanych
budżetach FA oraz wartości specyficzne dla monitoringu (@FA = 10%).

| Model | Δ @FA=5% | Δ @FA=10% | Δ @FA=20% | Wykrycia tylko-monitoring | Śr. wyprzedzenie (okna) |
|---|---:|---:|---:|---:|---:|
| Random Forest | +6,9 | **−10,9** | +2,3 | 48 | 1,96 |
| XGBoost | +8,3 | **−5,1** | +0,6 | 47 | 2,05 |
| LightGBM | +0,7 | **−5,0** | −2,0 | 52 | 2,06 |
| CatBoost | +8,1 | **−6,4** | −8,6 | 39 | 2,09 |
| **LSTM** | +10,0 | **+2,6** | −2,3 | **74** | 2,04 |

[RYS: static_vs_dynamic_{random_forest,xgboost,lightgbm,catboost,lstm}_w3.png]

Wyniki są mieszane i praca raportuje je bez upiększeń. Przy kanonicznym
budżecie FA = 10% reguła statyczna osiąga wyższą czułość dla wszystkich
czterech modeli statycznych (od −5,0 do −10,9 pp): agregator maksimum po
czterech silnie skorelowanych oknach „widzi" czterokrotnie więcej szumu niż
pojedyncza, skalibrowana ocena W3, więc wyrównanie budżetu fałszywych alarmów
wymusza wyżej położony próg i utratę części wykryć. Wyjątkiem jest **LSTM —
jedyny model sekwencyjny — dla którego reguła monitorująca wygrywa także na
czułości (+2,6 pp)**, co jest spójne z hipotezą, że architektura przetwarzająca
sekwencję najlepiej wykorzystuje informację zawartą w trajektorii.

Wartość monitoringu ujawnia się w dwóch wymiarach nieuchwytnych dla samej
czułości. Po pierwsze, **wyprzedzenie czasowe**: wśród wykrytych defaultujących
alarm pada średnio około dwa okna przed W3 — w praktyce bankowej to czas na
działania miękkie (kontakt, restrukturyzacja, obniżenie limitu), których
wartość nie jest ujęta w macierzy pomyłek. Po drugie, **wykrycia unikalne**:
39–74 defaultujących na model, których reguła statyczna nie flaguje w ogóle —
klienci, u których ryzyko uwidoczniło się we wcześniejszych oknach i „uspokoiło"
w W3. Reguła monitorująca jest zatem komplementarna wobec statycznej, nie
substytucyjna; rozstrzygnięcie bilansu zależy od modelu kosztów instytucji
(im droższe późne wykrycie względem fałszywego alarmu, tym większa wartość
monitoringu).

Interpretację uzupełnia diagnoza rozkładu PD per okno, przeprowadzona osobno
dla obu klas. W modelach drzewiastych średnie PD klientów spłacających jest
praktycznie identyczne we wszystkich oknach (różnica W0 − W3 od −0,002 do
−0,004, częstość alarmów stabilna), a u defaultujących rośnie wyraźnie ku W3
(o 0,065–0,071). Oznacza to, że (a) modele te nie zawyżają ocen na starszych
oknach — **nie występuje istotne przesunięcie rozkładu** między treningiem na
W3 a inferencją na W0..W2, oraz (b) dominacja najstarszego okna w histogramie
pierwszych alertów jest artefaktem zliczania pierwszego przekroczenia przy
zbliżonej częstości alarmów per okno, nie dowodem na masowe „wczesne sygnały";
sygnał narastania ryzyka u defaultujących jest natomiast rzeczywisty. Jedynie
LSTM wykazuje niewielki dryf również dla klasy spłacającej (+0,004 średniego
PD i 45,4% wobec 39,6% częstości alarmów na W0 względem W3) — jego wynik
w regule monitorującej należy więc czytać z tą poprawką, choć porównanie przy
stałym budżecie fałszywych alarmów z tabeli 5.3 ten efekt z konstrukcji
neutralizuje [RYS: pd_per_window_{model}.png].

## 5.5. Interpretowalność modeli i ich przydatność decyzyjna

Wyjaśnialność zrealizowano metodą SHAP (rozdz. 2.5): dla czterech modeli
drzewiastych system zwraca przy każdej predykcji pięć cech o największym
wkładzie, z konwencją znaku „wartość dodatnia podnosi PD". Wyjaśnienia liczone
są przez TreeExplainer na estymatorze bazowym (sprzed kalibracji) — korekta
izotoniczna jest monotoniczna, więc nie zmienia rankingu cech, natomiast
wartości SHAP opisują skalę modelu bazowego i nie sumują się do serwowanego,
skalibrowanego PD; jest to udokumentowany kompromis na rzecz czasu odpowiedzi
(pojedyncze wyjaśnienie ~100 ms, wobec limitu 2 s). Dla LSTM wyjaśnienia
pominięto (TreeExplainer nie ma zastosowania, a KernelExplainer przekracza
budżet czasowy). Rankingi cech są zbieżne między modelami i z ważnościami lasu
losowego: dominują świeże zachowania płatnicze (PAY_max, recent_pay_status,
late_count, utilization_rate), zmienne demograficzne zajmują odległe pozycje —
struktura zależności w danych, nie artefakt jednej rodziny algorytmów.

### 5.5b. Audyt sprawiedliwości względem atrybutu chronionego

Audyt przeprowadzono biblioteką fairlearn [NOWE: Bird 2020] dla pięciu
skalibrowanych modeli, względem atrybutu SEX, na zbiorze testowym (6 000
obserwacji; 2 402 mężczyzn, 3 598 kobiet), przy binaryzacji progami kosztowymi
z sekcji 4.7 — audyt odzwierciedla więc faktyczny punkt pracy systemu, a nie
umowny próg 0,5. Zastosowano dwie komplementarne miary. Różnica parytetu
demograficznego (DPD) porównuje częstość alarmów między grupami, abstrahując od
rzeczywistych zdarzeń; różnica wyrównanych szans (EOD) [NOWE: Hardt 2016]
warunkuje na prawdziwej etykiecie i mierzy większą z dwóch luk: wykrywalności
faktycznych defaultów (TPR) oraz fałszywych alarmów wśród spłacających (FPR).

Rozróżnienie to ma znaczenie zasadnicze. Częstość defaultu różni się między
grupami (23,4% mężczyźni wobec 21,3% kobiety w zbiorze testowym), wskutek czego
nawet bezbłędny klasyfikator wykazywałby DPD około +0,021; wymuszenie pełnego
parytetu demograficznego wymagałoby traktowania osób o identycznym profilu
ryzyka odmiennie ze względu na płeć — co samo stanowiłoby dyskryminację
bezpośrednią i stałoby w sprzeczności z obowiązkiem rzetelnej oceny zdolności
kredytowej (art. 70 Prawa bankowego). Dlatego DPD raportowane jest jako miara
przesiewowa, a kryterium oceny stanowią wyrównane szanse — równy rozkład
ciężaru błędów przy danym stanie faktycznym.

**Tabela 5.4.** Audyt fairness przy progach kosztowych (limit DoD: 0,10).

| Model | Próg | DPD | EOD | Składnik dominujący EOD |
|---|---:|---:|---:|---|
| Random Forest | 0,145 | +0,035 | +0,028 | luka FPR (0,375 vs 0,347) |
| XGBoost | 0,165 | +0,036 | +0,028 | luka FPR (0,369 vs 0,341) |
| LightGBM | 0,160 | +0,035 | +0,027 | luka FPR (0,371 vs 0,344) |
| CatBoost | 0,160 | +0,039 | +0,033 | luka FPR (0,394 vs 0,361) |
| LSTM | 0,155 | **+0,006** | +0,021 | luka TPR, **odwrócona** (0,727 vs 0,748) |

[RYS: fig_5_10_audyt_fairness.png]

Wszystkie modele spełniają kryterium |DPD|, |EOD| ≤ 0,10 z co najmniej
trzykrotnym marginesem — hipoteza H3 jest potwierdzona. Interpretując wyniki
na tle luki strukturalnej +0,021: modele drzewiaste dokładają od siebie
0,014–0,018 ponad różnicę base rate, a lukę wyrównanych szans tworzy w nich
konsekwentnie składnik fałszywych alarmów — rzetelnie spłacający mężczyźni są
błędnie flagowani o 2,7–3,3 pp częściej niż kobiety. Na szczególną uwagę
zasługuje LSTM: jako jedyny nie otrzymuje na wejściu żadnych cech
demograficznych (tensor 3×3 zawiera wyłącznie sekwencję statusów, sald
i wpłat) i jako jedyny osiąga DPD poniżej luki strukturalnej, z odwróconym
znakiem luk błędów.

Kontrast ten podsunął naturalny eksperyment ablacyjny, który przeprowadzono
wprost: cztery modele drzewiaste przetrenowano w identycznym protokole
**z usuniętymi kolumnami SEX** (atrybut służy wtedy wyłącznie do pomiaru metryk).
Rezultat: zdolność predykcyjna nie zmieniła się w granicach szumu (|ΔAUC| ≤
0,001 dla każdego modelu), natomiast parytet uległ wyraźnej poprawie — DPD
XGBoost spadło z +0,036 do +0,011, LightGBM z +0,035 do +0,007, lasu losowego
z +0,035 do +0,027, CatBoost z +0,039 do +0,022, z analogicznym spadkiem EOD
(XGBoost do +0,004, LightGBM do +0,002). Wniosek jest dwojaki. Po pierwsze,
umiarkowane luki modeli pełnocechowych wynikały w istotnej części
z bezpośredniego użycia atrybutu chronionego, nie wyłącznie z korelatów —
a jego usunięcie **nic nie kosztuje**: to jednoznaczna rekomendacja wdrożeniowa
(w systemie produkcyjnym zmienna płci powinna zostać usunięta z wektora cech,
pozostając w danych wyłącznie do celów audytu, na co wprost pozwala art. 10
ust. 5 rozporządzenia o sztucznej inteligencji [25]). Po drugie, wariant
badawczy z jawnym SEX spełnił swoją rolę: pozwolił skwantyfikować wpływ
atrybutu zamiast zakładać go a priori.

Wobec spełnienia kryterium H3 z zapasem, aktywna mitygacja nie jest konieczna;
zasadne jest podejście proporcjonalne: audyt DPD/EOD jako stała bramka
wydaniowa po każdym retreningu, usunięcie SEX z cech jako krok wdrożeniowy,
a jako udokumentowany mechanizm warunkowy — korekta post-hoc progów metodą
ThresholdOptimizer (fairlearn) z ograniczeniem wyrównanych szans, która nie
narusza skalibrowanych prawdopodobieństw (rdzenia trajektorii PD) i wpina się
w istniejącą, progową warstwę decyzyjną. Jej zastosowanie w systemie wczesnego
ostrzegania — gdzie alert kieruje do przeglądu analityka, nie do decyzji
odmownej — wyrównuje ciężar bycia objętym przeglądem, a nie warunki oferty.

## 5.6. Dyskusja wyników i weryfikacja hipotez badawczych

**H1 — potwierdzona.** Modele 3-miesięczne zachowują jakość 6-miesięcznych
baseline'ów: las losowy 0,7741 wobec 0,7792 (−0,51 pp), XGBoost 0,7761 wobec
0,7818 (−0,57 pp), LSTM 0,7614 wobec 0,7686 (−0,72 pp) — wszystkie straty
poniżej 1 pp (porównanie orientacyjne: baseline'y nie były kalibrowane).
Skrócenie okna, warunkujące istnienie trajektorii, nie odbiera modelom
zdolności dyskryminacyjnej.

**H2 — potwierdzona częściowo, w brzmieniu przyjętym w 3.2.** Wcześniejsza
detekcja: tak — średnio ~2 okna wyprzedzenia; wykrycia niedostępne regule
statycznej: tak — 39–74 na model. Natomiast czułość przy stałym budżecie
fałszywych alarmów 10% jest dla czterech modeli statycznych niższa (do
−10,9 pp) — z wyjątkiem LSTM (+2,6 pp). Teza obroniona w brzmieniu
„wcześniej i komplementarnie", nie „czulej"; dodatkowo wynik LSTM wskazuje, że
pełne wykorzystanie trajektorii wymaga architektury sekwencyjnej.

**H3 — potwierdzona.** Maksymalna wartość |DPD|/|EOD| w całej piątce wynosi
0,039 przy limicie 0,10; kontr-eksperyment bez SEX domyka analizę rekomendacją
wdrożeniową.

**Ograniczenia.** (1) Jeden zbiór (Tajwan 2005) i jeden podział — różnice
między modelami drzewiastymi raportowano z przedziałami bootstrap;
generalizacja na inne portfele niezweryfikowana. (2) Monitoring symulowany
retrospektywnie na danych przekrojowych: okna nakładają się, a horyzont
predykcji różni się między oknami (rozdz. 3.3.4). (3) Progi kosztowe
wyznaczane na części kalibracyjnej wspólnej z kalibratorem (kompromis opisany
w 4.7). (4) Wyjaśnienia SHAP operują na skali modeli bazowych, nie
skalibrowanej. (5) Model kosztu FN = 5 × FP jest założeniem eksperckim —
wnioski sekcji 5.4 są funkcją tej asymetrii.

# Zakończenie

Praca postawiła pytanie, czy ocenę ryzyka kredytowego warto traktować jako
proces rozwijający się w czasie, a nie jednorazowy werdykt — i odpowiedziała na
nie konstrukcyjnie oraz empirycznie. Zbudowano kompletny system eksperymentalny
(React / .NET 8 / Flask / PostgreSQL), w którym pięć skalibrowanych modeli
ocenia tę samą ekspozycję na czterech przesuwanych oknach historii płatniczej,
a trajektoria PD zasila regułę wczesnego ostrzegania z progami optymalnymi
kosztowo i wyjaśnieniami predykcji.

Wyniki empiryczne układają się w spójny obraz. Skrócenie okna obserwacji do
trzech miesięcy kosztuje mniej niż 1 pp AUC (H1). Reguła monitorująca nie
przewyższa statycznej pod względem czułości przy stałym budżecie fałszywych
alarmów — z wyjątkiem modelu sekwencyjnego — ale oferuje około dwóch okien
wyprzedzenia i kilkadziesiąt wykryć na model niedostępnych ocenie jednorazowej
(H2, potwierdzona częściowo). Wszystkie modele przechodzą audyt sprawiedliwości
z wielokrotnym zapasem, a eksperyment ablacyjny pokazał, że usunięcie atrybutu
chronionego z cech nie kosztuje nic predykcyjnie i poprawia parytet (H3).
Najlepszym pojedynczym modelem jest CatBoost (AUC 0,779); przewaga metod
drzewiastych nad LSTM na danych tabelarycznych potwierdza literaturę, lecz to
LSTM — jedyny model bez cech demograficznych i jedyny architektonicznie
sekwencyjny — okazuje się najbliższy parytetu i jako jedyny zyskuje na regule
monitorującej także w czułości.

Kierunki dalszych badań wynikają wprost z ograniczeń: walidacja schematu na
prawdziwym panelu podłużnym z etykietami przesuwanymi w czasie; złożenie
predykcji w zespół typu stacking z protokołem out-of-fold; rozszerzenie audytu
sprawiedliwości na pozostałe atrybuty i analiza mitygacji progowej; wreszcie
kalibracja modelu kosztów FN/FP na rzeczywistych stratach portfelowych, od
której zależy bilans reguły monitorującej. Niezależnie od tych rozszerzeń,
zasadniczy wniosek pracy pozostaje: monitoring trajektorii PD jest praktycznie
wykonalnym, audytowalnym i regulacyjnie umocowanym uzupełnieniem oceny
statycznej — wartym wdrożenia tam, gdzie koszt spóźnionej reakcji przewyższa
koszt dodatkowego przeglądu.
