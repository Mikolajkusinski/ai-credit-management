# Karty Q&A na obronę + ściąga liczb

> Stan artefaktów: commit `023056c`, 2026-07-07 (po naprawach metodologicznych).
> Każda liczba pochodzi z `ml-learing-center/reports/` (`FINAL_REPORT.md` agreguje).
> Część A: fairness. Część B: pytania ogólne. Część C: ściąga (1 strona do druku).

---

## CZĘŚĆ A — fairness (8 pytań)

**A1. Dlaczego SEX jest cechą wejściową modeli, skoro prawo UE zakazuje różnicowania po płci?**
To decyzja badawcza, nie wdrożeniowa: celem było *skwantyfikowanie* wpływu atrybutu zamiast zakładania go a priori. Domknięciem jest kontr-eksperyment: cztery modele drzewiaste przetrenowane bez kolumn SEX tracą co najwyżej 0,001 AUC, a parytet się poprawia (DPD XGBoost 0,036→0,011, LightGBM 0,035→0,007). Wniosek wdrożeniowy jest w pracy wprost: w produkcji SEX usuwamy z cech, zostaje w danych wyłącznie do audytu — na co pozwala art. 10 ust. 5 AI Act. Dodatkowo LSTM, który konstrukcyjnie nie widzi demografii (tensor 3×3: PAY/BILL/AMT), osiąga DPD 0,006 — naturalny dowód ablacyjny.

**A2. Dodatnie DPD dla wszystkich modeli to disparate impact — czemu Pan to bagatelizuje?**
Nie bagatelizuję — dekomponuję. Base rate defaultu różni się między grupami (M 23,4% vs F 21,3% w teście), więc nawet bezbłędny klasyfikator miałby DPD ≈ +0,021. Obserwowane DPD 0,035–0,039 to luka strukturalna plus 0,014–0,018 od modeli; po usunięciu SEX nadwyżka modelowa niemal znika. Wnioskuję z EOD (równość ciężaru błędów), a DPD raportuję jako miarę przesiewową — wszystkie wartości ≤ 0,039 przy limicie 0,10.

**A3. Dlaczego equalized odds, a nie demographic parity?**
Bo przy różnych base rate'ach parytet demograficzny jest niekompatybilny z trafną oceną ryzyka: wymuszenie DPD=0 wymagałoby traktowania osób o identycznym profilu ryzyka różnie ze względu na płeć — czyli dyskryminacji bezpośredniej, sprzecznej z art. 70 Prawa bankowego. Equalized odds warunkuje na prawdzie: żąda równej wykrywalności faktycznych defaultów (TPR) i równej częstości fałszywych alarmów u spłacających (FPR). W kredytowaniu to FPR jest miarą krzywdy klienta, TPR — równości ochrony.

**A4. Progi binaryzacji audytu były liczone na zbiorze testowym — czy audyt nie jest skażony?**
Był to realny wyciek i został naprawiony: progi kosztowe są teraz optymalizowane na splicie kalibracyjnym, test pozostaje zamrożony. Przeliczyliśmy cały łańcuch (`reports/threshold_leakage_fix.md`): progi zmieniły się umiarkowanie (XGB 0,180→0,165, CatBoost 0,130→0,160, LSTM 0,175→0,155), a werdykt audytu pozostał jakościowo identyczny — wszystkie |DPD|/|EOD| ≤ 0,04.

**A5. Jeden podział, n=6000 — skąd pewność, że różnice nie są szumem?**
Wariancję kwantyfikuje bootstrap (40 repróbkowań testu): odchylenie AUC ~0,006 per model; luki fairness (≤0,039) leżą wielokrotnie poniżej limitu 0,10, więc nawet dwusigmowe wahnięcie nie zmienia werdyktu. Różnice DPD *między* modelami drzewiastymi (0,035–0,039) traktuję jako nierozróżnialne — w pracy nie buduję na nich rankingu.

**A6. Co z mitygacją — czemu nie zastosowano reweightingu / ThresholdOptimizera?**
Proporcjonalność: wszystkie modele przechodzą audyt z ≥3× marginesem, a aktywna ingerencja ma koszty. Reweighting celuje w parytet demograficzny (metrykę uznaną za niewłaściwą przy różnych base rate'ach) i wymaga retrenu z kaskadą kalibracji. Przyjęta strategia: audyt DPD/EOD jako bramka wydaniowa po każdym retreningu + usunięcie SEX (za darmo) + ThresholdOptimizer(equalized_odds) jako udokumentowany mechanizm warunkowy — post-processing nie narusza skalibrowanych PD (rdzenia trajektorii) i wpina się w istniejącą warstwę progową. Prawnie broni się dlatego, że system jest wczesnym ostrzeganiem z człowiekiem w pętli: wyrównujemy ciężar przeglądu, nie warunki oferty.

**A7. Czemu audyt tylko po SEX, a nie AGE/EDUCATION/MARRIAGE?**
SEX jest standardowym atrybutem chronionym w literaturze credit scoringu i jedynym binarnym w zbiorze, co czyni DPD/EOD jednoznacznymi; definicja ukończenia zadania wprost wskazywała SEX. Pozostałe atrybuty wymagają decyzji o binningu (np. progi wieku) i są wskazane w pracy jako rozszerzenie — infrastruktura audytu (fairlearn, MetricFrame) jest na to gotowa bez zmian kodu modeli.

**A8. LSTM jest najsprawiedliwszy — czemu nie on jest modelem rekomendowanym?**
Asymetria stawek: przewaga parytetu LSTM nad drzewami to ~0,02–0,03 DPD, podczas gdy strata dyskryminacji to 1,3–1,8 pp AUC (bootstrap: rozróżnialna, CI różnic nie zawiera zera) i najgorszy Brier. Po usunięciu SEX drzewa zbliżają się do parytetu LSTM niemal za darmo — więc właściwy ruch to nie wybór słabszego modelu, tylko odchudzenie cech mocniejszego. Rola LSTM w pracy jest inna: dowód ablacyjny i jedyny model wygrywający regułą monitorującą.

---

## CZĘŚĆ B — pytania ogólne (5)

**B1. Heatmapy strojenia w pracy — na jakich danych? Czy nie stroił Pan na teście?**
W finalnej wersji pracy heatmapy 4.5/4.7 prezentują CV-AUC (5-fold, stratyfikowany) liczone wyłącznie na 18 000 obserwacji treningowych; konfiguracje produkcyjne leżą na plateau (RF o 0,0008, XGB o 0,0034 od optimum CV). Niezależnie strojenie Optuna (30 prób/model, 5-fold) potwierdziło uplift < 0,5 pp — strojone warianty świadomie nie weszły do systemu. Zbiór testowy uczestniczy wyłącznie w finalnej ewaluacji.

**B2. Monitoring przegrywa ze statyką przy FA=10% — jak Pan broni tezy?**
Raportuję to wprost: −5,0 do −10,9 pp dla czterech modeli statycznych; agregator max po skorelowanych oknach widzi więcej szumu. Ale teza (H2) postuluje wczesność i komplementarność, nie wyższą czułość: monitoring daje średnio ~2 okna wyprzedzenia i 39–74 wykryć/model, których statyka nie flaguje nigdy. Kluczowy wyjątek: LSTM — jedyny model sekwencyjny — wygrywa monitoringiem także na czułości (+2,6 pp), co wskazuje, że pełne wykorzystanie trajektorii wymaga architektury sekwencyjnej. Bilans zależy od modelu kosztów instytucji.

**B3. Wszystkie okna przewidują tę samą etykietę październikową — czy to nie jest po prostu zmiana horyzontu predykcji? I skąd dominacja W0 w lead time?**
Ograniczenie jest jawnie opisane w rozdz. 3.3.4: zbiór jest przekrojowy, monitoring symulowany, W0 to horyzont 4-miesięczny, W3 — 1-miesięczny. Diagnoza PD-per-okno rozstrzyga drugą część: u drzew PD spłacających jest płaskie między oknami (Δ −0,002…−0,004; częstość alarmów stabilna), więc nie ma przesunięcia rozkładu — dominacja W0 w histogramie to artefakt zliczania *pierwszego* przekroczenia. U defaultujących PD rośnie ku W3 o 0,065–0,071 — sygnał narastania jest rzeczywisty. Jedyny dryf: LSTM (+0,004 dla y=0), a porównanie przy stałym FA go neutralizuje.

**B4. Skoro trzy boostery są nierozróżnialne, po co pięć modeli?**
Bootstrap potwierdza: RF/XGB/LGBM nierozróżnialne, CatBoost rozróżnialnie lepszy od RF i XGB (nie od LGBM), wszystkie drzewa rozróżnialnie lepsze od LSTM. Pięć modeli to nie redundancja, tylko kontrola wniosków: zbieżność rankingu cech między rodzinami algorytmów pokazuje, że struktura zależności siedzi w danych; rozrzut zachowań w regule monitorującej (LSTM vs drzewa) i w fairness (LSTM przy parytecie) byłby niewidoczny przy jednym modelu.

**B5. Dlaczego LSTM w ogóle, skoro sekwencja ma 3 kroki?**
Świadomy wybór reprezentanta ujęcia sekwencyjnego przy krótkim oknie — i wynik jest informatywny w obie strony: na czystej dyskryminacji przegrywa z drzewami (spójnie z literaturą o danych tabelarycznych), ale jako jedyny (a) zyskuje na regule monitorującej (+2,6 pp @FA=10%, 74 unikalne wykrycia — najwięcej), (b) działa bez cech demograficznych i bez ręcznej inżynierii cech, (c) jest przy parytecie. To trzy niezależne argumenty, że wymiar sekwencyjny niesie sygnał, którego agregaty nie widzą.

---

## CZĘŚĆ C — ściąga liczb (druk, 1 strona)

**Modele W3 (test 6 000; 1 327 defaultów) — po kalibracji izotonicznej:**

| Model | AUC | Brier | Próg | DPD | EOD | Δ mon−stat @FA=10% |
|---|---:|---:|---:|---:|---:|---:|
| Random Forest | 0,7741 | 0,1374 | 0,145 | +0,035 | +0,028 | −10,9 pp |
| XGBoost | 0,7761 | 0,1360 | 0,165 | +0,036 | +0,028 | −5,1 pp |
| LightGBM | 0,7767 | 0,1363 | 0,160 | +0,035 | +0,027 | −5,0 pp |
| **CatBoost** | **0,7793** | **0,1357** | 0,160 | +0,039 | +0,033 | −6,4 pp |
| LSTM | 0,7614 | 0,1388 | 0,155 | **+0,006** | +0,021 | **+2,6 pp** |

- Split: 60/20/20 (18k/6k/6k), `random_state=42`; skalery fit na train; progi na calib (FN=5×FP).
- Kalibracja: Brier −19% (RF 0,1689→0,1374), −24% (XGB), −25% (LSTM 0,1850→0,1385).
- Bootstrap 40×: std AUC ~0,006; rozróżnialne: CatBoost>RF (+0,0051), CatBoost>XGB (+0,0035), wszystkie drzewa>LSTM (+0,013…0,018); nierozróżnialne: RF↔XGB↔LGBM, CatBoost↔LGBM.
- Static vs monitoring @FA=5%: wszystkie modele NA PLUS (+0,7…+10,0 pp); @FA=20%: mieszane.
- Lead time: średnio 1,96–2,09 okna; unikalne wykrycia (tylko-monitoring): RF 48, XGB 47, LGBM 52, CatBoost 39, **LSTM 74**.
- PD-per-okno (drzewa): y=0 płaskie (Δ −0,002…−0,004), y=1 rośnie ku W3 (+0,065…0,071); LSTM: dryf y=0 +0,004 (alert rate 45,4% vs 39,6%).
- Base rate: M 23,4% / F 21,3% (test); pełny zbiór 24,2%/20,8%; **luka strukturalna DPD ≈ 0,021**; n grup: M 2 402 / F 3 598.
- Bez SEX (retrain 4 drzew): |ΔAUC| ≤ 0,001; DPD: RF 0,027, XGB **0,011**, LGBM **0,007**, CatBoost 0,022; EOD: XGB 0,004, LGBM 0,002.
- H1 (strata vs 6-mies.): RF −0,51 pp, XGB −0,57, LSTM −0,72 (wszystkie < 1 pp).
- Reguła alertu trendu: slope = PD_W3 − PD_W0, próg 0,10 (INCREASING/DECREASING/STABLE).

**Naprawy metodologiczne 2026-07-07 (gdyby padło pytanie o rygor):** train/serve
parity one-hot (test 0,0 różnicy), progi test→calib, skalery po splicie
(|ΔAUC| ≤ 0,0009), transakcja atomowa zapisu. Dowody: `reports/*_leakage_fix.md`.

*Artefakty: commit `023056c`, 2026-07-07.*
