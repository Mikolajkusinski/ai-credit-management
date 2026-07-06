# Użyj Fable 5, Zanim Zniknie

Wyselekcjonowana lista zadań w **tym** repozytorium, przy których Claude
**Fable 5** naprawdę uzasadnia swój koszt — wraz z niezawodnymi, gotowymi do
wklejenia promptami dla każdego z nich.

Fable 5 to najzdolniejszy model Anthropic: stworzony do najtrudniejszego
rozumowania, długodystansowej pracy autonomicznej oraz kompletnych opracowań
analitycznych (raporty, metodologia, dokumenty). Jest też najbardziej
tokenożernym modelem w planie Pro i pracuje wielominutowymi turami. Dlatego to
nie jest lista „przełącz wszystko na Fable 5" — to garść zadań, w których
głębia analizy zmienia efekt końcowy.

---

## Jak korzystać z tego pliku

1. Przełącz model przez `/model` → **Fable 5** przed uruchomieniem któregoś zadania.
2. Wklej **cały** prompt w jednej wiadomości. Fable 5 najlepiej działa przy
   kompletnym, dobrze wyspecyfikowanym zleceniu i pracuje autonomicznie — **nie**
   podawaj mu kroków po kawałku.
3. Przy trudnych zadaniach analitycznych napisz „pracuj na wysokim wysiłku"
   (ma zapas, którego lżejsze modele nie mają).
4. Spodziewaj się długich tur (kilka minut przy większych zadaniach). To normalne,
   nie zawieszenie.
5. Po ciężkim uruchomieniu wróć do **Opus 4.8** do codziennych edycji.

### Rezerwuj Fable 5 na te zadania — nie marnuj go na
Rutynowe edycje, aktualizacje `CHECKLIST.md` / podsumowań sprintów, wiadomości
commitów, poprawki lintera, drobne bugfixy w jednym pliku, zmiany nazw,
szablonowe testy. Opus 4.8 (albo Sonnet 4.6) da ten sam efekt za ułamek Twojego
tygodniowego limitu.

> ⚠️ **Jedno zastrzeżenie:** klasyfikator bezpieczeństwa Fable 5 odmawia analiz
> nastawionych na cyberbezpieczeństwo. Dla repo o ryzyku kredytowym to nie
> problem — po prostu nie proś go np. o „znajdź sposoby na wykorzystanie luk w API".

---

## Zadanie 1 — Kontradyktoryjny przegląd przed obroną (metodologia vs. implementacja)

**O co chodzi.** Niech Fable 5 wcieli się w wrogiego recenzenta: atakuje
metodologię z pracy w zestawieniu z tym, co *faktycznie* robi kod, i wskazuje
każdą tezę, której implementacja nie potwierdza. To uzupełnia
`DokumentRoznice.md` (różnice praca-vs-projekt, który już zacząłeś), ale idzie
głębiej — szuka *broniących się* słabości, nie tylko różnic tekstowych. To
mocna strona Fable 5: skłonność do kontry i dobre rozumowanie po repo.

**Prompt:**

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

---

## Zadanie 2 — Wyniki sprawiedliwości: interpretacja + rekomendacja mitygacji

**O co chodzi.** Masz DPD/EOD (demographic parity difference / equalized odds
difference) względem SEX dla 5 modeli W3 (Sprint 5, `fairness_audit.py` przez
fairlearn). Same liczby nie obronią pracy — robi to *interpretacja*. Fable 5
jest mocny właśnie w takim otwartym rozumowaniu o wysokiej stawce: który model
najlepiej się broni przy decyzji kredytowej i za którą mitygacją argumentować.

**Prompt:**

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

---

## Zadanie 3 — Polowanie na błędy poprawności przed obroną (kod krytyczny dla ryzyka)

**O co chodzi.** Przed obroną zrób głęboki przegląd ścieżek kodu, których błąd
byłby kompromitujący: inżynieria cech, przygotowanie tensora LSTM `(1, 6, 3)`
oraz stosowanie zapisanych skalerów. Fable 5 ma wyższą wykrywalność błędów niż
lżejsze modele — ale zbyt dosłownie stosuje się do „zgłaszaj tylko poważne
problemy", więc prompt wprost każe mu zgłaszać wszystko i pozwolić Ci filtrować.

**Prompt:**

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

---

## Zadanie 4 — Wariant B okna przesuwnego: projekt + implementacja end-to-end

**O co chodzi.** Twój fokus ze Sprintu 1 (`plan_sprintow_wariant_B.md`): funkcja
3-miesięcznego okna przesuwnego + baza danych, obejmująca usługę Flask ML,
orkiestrator .NET i frontend React. Wieloplikowe, trzy języki, długi dystans —
to dokładnie to, do czego stworzono tryb autonomiczny Fable 5, **o ile** podasz
mu pełną specyfikację z góry.

**Prompt:**

```text
Pracuj na wysokim wysiłku i autonomicznie. Chcę, żebyś zaprojektował, a następnie
zaimplementował funkcję okna przesuwnego "Wariant B" opisaną w
plan_sprintow_wariant_B.md.

Najpierw przeczytaj: plan_sprintow_wariant_B.md, CLAUDE.md oraz istniejący kod
okna przesuwnego (ml-service/sliding_window.py, ml-learing-center/sliding_window.py)
i przepływ monitoringu/snapshotów (backend/WebApi/Services/MonitoringService.cs,
SnapshotRepository.cs oraz frontend SnapshotForm.tsx / TimelineChart.tsx).

Cel: ścieżka predykcji z 3-miesięcznym oknem przesuwnym wsparta bazą danych,
działająca end-to-end przez cały stos:
- Usługa Flask ML (ml-service/): konstrukcja okna + modele _w3.
- Backend .NET (backend/WebApi/): DTO, kontroler, serwis, persystencja.
- Frontend React (frontend/WebApp/src/): UI do sterowania i wyświetlania.

Zrób to po kolei:
1. Podaj krótki projekt: przepływ danych, potrzebne zmiany schematu/BD, nowe/edytowane
   endpointy oraz gdzie zmienia się każda warstwa. Zatrzymaj się i pozwól mi zatwierdzić.
2. Po zatwierdzeniu zaimplementuj to, zachowując istniejące mapowanie 22 pól
   camelCase (.NET) ↔ snake_case (Flask).
3. Zaktualizuj lub dodaj testy (pytest w ml-service/tests, xUnit w
   backend/WebApi.Tests, vitest we frontendzie) i powiedz mi dokładnie, jak je
   uruchomić.

Trzymaj się istniejących wzorców w każdej warstwie. Nie przeinżynierowuj ani nie
dodawaj funkcji poza specyfikacją Wariantu B.
```

---

## Zadanie 5 — Sekcja wyników / dyskusji pracy (głębokie pisanie)

**O co chodzi.** Fable 5 jest wprost dostrojony do kompletnego pisania
analitycznego. Podaj mu swoje faktyczne wyniki ewaluacji i niech napisze prozę
wyników i dyskusji — interpretując, porównując i broniąc — zamiast tylko
formatować. To najwyższy zwrot słowo-w-słowo dla pracy.

**Prompt:**

```text
Pracuj na wysokim wysiłku. Pomóż mi napisać sekcję Wyniki i Dyskusja mojej pracy
magisterskiej o predykcji niewypłacalności kredytowej.

Przeczytaj kod ewaluacji i jego wyniki:
- ml-learing-center/evaluation.py, timeseries_eval.py, static_vs_dynamic.py,
  optimize_thresholds.py, optuna_tuning.py.
- Ich wyniki w ml-learing-center/reports/ i ml-learing-center/thesis_figures/.
- WalidacjaPDFv7.md dla ram walidacji, które już ustaliłem.

Następnie napisz prozę na poziomie pracy (po polsku), która:
1. Raportuje wydajność wszystkich 5 modeli (RF, XGBoost, LSTM, LightGBM, CatBoost)
   na właściwych metrykach i interpretuje — nie tylko wylicza — różnice.
2. Argumentuje porównanie statyczne-vs-dynamiczne (okno przesuwne): czy dowody
   faktycznie uzasadniają podejście dynamiczne? Bądź szczery, jeśli to marginalne.
3. Omawia optymalizację progów i strojenie hiperparametrów (Optuna) oraz co
   zmieniły.
4. Podaje ograniczenia i zagrożenia dla trafności tak, jak zrobiłby to ostrożny
   badacz.

Dopasuj ton do WalidacjaPDFv7.md. Zaczynaj każdą podsekcję od wniosku, potem
dowody. Zaznacz każde miejsce, gdzie dane nie w pełni popierają tezę, którą
mógłbym chcieć postawić.
```

---

## Zadanie 6 — Audyt spójności przez cały stos (kontrakt 22 pól / 5 modeli)

**O co chodzi.** Kontrakt żądania (22 pola) i odpowiedź predykcji 5 modeli
przechodzą przez trzy języki: typy React → DTO .NET → JSON Flask. Rozjazd między
tymi warstwami to klasyczne źródło cichych błędów. Fable 5 potrafi trzymać
wszystkie trzy warstwy naraz w kontekście i porównać je ze sobą — zadanie, które
frustruje lżejsze modele.

**Prompt:**

```text
Pracuj na wysokim wysiłku. Zaudytuj end-to-end kontrakt danych tego systemu pod
kątem niezgodności między trzema warstwami. Prześledź, nie prześlizguj się.

Kontrakt płynie:
- Frontend: frontend/WebApp/src/types/prediction.ts, types/monitoring.ts,
  components/InputForm.tsx, api/predictApi.ts, api/monitoringApi.ts.
- Backend: backend/WebApi/Models/PredictRequest.cs, FlaskPredictRequest.cs,
  PredictResponse.cs oraz DTO monitoringu; Controllers/PredictController.cs,
  MonitoringController.cs; Services/PythonModelClient.cs, PredictionService.cs.
- Usługa ML: ml-service/app.py (parsowanie żądania i odpowiedź JSON ze wszystkimi
  5 modelami).

Zweryfikuj:
1. Wszystkie 22 pola wejściowe zgadzają się pole-w-pole przez React → .NET
   (camelCase) → Flask (snake_case), z poprawnymi typami i udokumentowanymi
   zakresami walidacji (wiek 18–100, limit 10K–1M, edukacja 1–4 itd.).
2. Odpowiedź predykcji 5 modeli (RF, XGBoost, LSTM, LightGBM, CatBoost) jest
   przekazywana wiernie na każdej warstwie — żaden model po cichu nie zgubiony,
   przemianowany ani źle oznaczony.
3. DTO monitoringu/timeseries oraz przekazywania SHAP są spójne end-to-end.

Wypisz tabelę każdej niezgodności lub ryzyka z file:line po obu stronach i
poprawką. Jeśli wszystko się zgadza, powiedz to wprost per sekcja — nie zakładaj.
```

---

## Zadanie 7 — Statyczne vs. dynamiczne: czy teza o oknie przesuwnym jest uzasadniona?

**O co chodzi.** Kluczową tezą pracy jest zapewne to, że podejście dynamiczne
(okno przesuwne) bije statyczne. To teza najbardziej narażona na atak. Niech
Fable 5 podda ją próbie w zestawieniu z faktycznym kodem eksperymentu i wynikami
— jako statystyk, nie kibic.

**Prompt:**

```text
Pracuj na wysokim wysiłku. Wciel się w rygorystycznego, sceptycznego statystyka
recenzującego jedną centralną tezę mojej pracy: że dynamiczne podejście z oknem
przesuwnym przewyższa statyczną bazę dla predykcji niewypłacalności kredytowej.

Przeczytaj ml-learing-center/static_vs_dynamic.py, timeseries_eval.py,
sliding_window.py, sliding_window_test.py oraz wyniki, które produkują w reports/
i thesis_figures/.

Oceń uczciwie:
1. Co eksperyment faktycznie mierzy i czy porównanie jest sprawiedliwe (te same
   podziały danych, te same metryki, brak wycieku z okienkowania)?
2. Czy różnica wydajności jest realna i istotna, czy mieści się w szumie? Odnieś
   się do wielkości efektu i czy testowanie istotności jest zasadne/obecne.
3. Jaki jest najmocniejszy kontrargument, który recenzent mógłby postawić przeciw
   podejściu dynamicznemu, i jak bym go odparł?
4. Daj mi werdykt końcowy: czy teza broni się jak napisana, wymaga złagodzenia,
   czy potrzebuje więcej dowodów? Jeśli złagodzenia — zaproponuj dokładne sformułowanie.

Bądź bezpośredni. Wolę znaleźć dziurę teraz niż na obronie.
```

---

## Szybka ściąga

| # | Zadanie | Zalecany wysiłek | Orientacyjny budżet |
|---|---------|------------------|---------------------|
| 1 | Kontradyktoryjny przegląd przed obroną | wysoki | średni–duży |
| 2 | Interpretacja sprawiedliwości | wysoki | średni |
| 3 | Polowanie na błędy poprawności | wysoki | średni |
| 4 | Wariant B end-to-end | wysoki/xhigh | duży |
| 5 | Pisanie wyników/dyskusji | wysoki | średni |
| 6 | Audyt kontraktu przez stos | wysoki | średni |
| 7 | Test statyczne-vs-dynamiczne | wysoki | mały–średni |

**Kolejność wg budżetu, jeśli uruchomisz tylko kilka:** najpierw 1 i 2 (największy
zwrot dla pracy), potem 3 (tania polisa przed obroną), potem 4, gdy będziesz
gotowy na dużą budowę.