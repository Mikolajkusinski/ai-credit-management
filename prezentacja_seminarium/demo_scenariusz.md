# Scenariusz demo na obronę (~9 min) + PLAN B

> Środowisko: naprawione artefakty W3 (po fixie U1 i leakage-fix, commit ≥ `023056c`),
> baza zseedowana `seed_demo_clients.py`. Materiał awaryjny: `demo_zapas/`.

## 0. Pre-flight (przed wejściem na salę, ~5 min wcześniej)

- [ ] `docker compose ps` → 3 kontenery `Up` (db healthy).
- [ ] `curl -s localhost:5001/health` → `{"status":"healthy"}`.
- [ ] `curl -s localhost:5120/api/v1/monitoring/clients | grep -c clientRef` → `3`.
- [ ] `cd frontend/WebApp && npm run dev` → `localhost:5173` otwarte w przeglądarce.
- [ ] Druga karta przeglądarki: folder `demo_zapas/` (PLAN B) otwarty.
- [ ] Ściąga liczb (`docs/thesis/obrona_QA.md` część C) wydrukowana obok.

## 1. Zakładka Prediction — klasyczna ocena jednorazowa (~2 min)

**Klik:** zakładka *Prediction* → formularz 22 cech (użyć „zdrowego" profilu:
LIMIT_BAL 120000, PAY_* = 0, bilans ~50k, wpłaty 5k) → **Predict**.
**Oczekiwany widok:** karty modeli z PD i gauge'ami.
**Powiedzieć:** „To jest punkt wyjścia — klasyczny scoring: jedna ocena, jeden
werdykt, zero informacji o kierunku zmian."

## 2. Ocena trajektorii — ten sam klient, cztery okna (~3 min)

**Klik:** zakładka *Monitoring* → (formularz stateless predict-timeseries lub
od razu krok 3, jeśli UI nie ma ścieżki stateless) — alternatywnie pokazać
`POST /api/v1/monitoring/predict-timeseries` w Swaggerze (`localhost:5120/swagger`).
**Oczekiwany widok:** trajektoria 4 punktów × 5 linii (RF/XGB/LGBM/CatBoost/LSTM).
**Powiedzieć:** „Te same 22 cechy, ale system czyta je jako 4 nakładające się
okna 3-miesięczne — każdy model daje trajektorię PD zamiast punktu. Progi
alarmów nie są umownym 0.5, tylko optymalnymi kosztowo wartościami 0.145–0.165."

## 3. Monitoring stanowy — historia klienta z bazy (~3 min)

**Klik:** *Monitoring* → lista klientów → `demo-rising-001` (badge INCREASING_RISK).
**Oczekiwany widok:** historia 4 migawek, Timeline 5 linii rosnących, karty
alertów: semafor czerwony (INCREASING_RISK).
**Powiedzieć:** „Klient oceniany czterokrotnie w czasie — trajektoria zapisana
w Postgresie. Nachylenie W3−W0 przekracza próg 0.10 → alert. Dla kontrastu…"
**Klik:** wróć → `demo-stable-002` (STABLE, płaska linia) → `demo-falling-003`
(badge STABLE przy OPADAJĄCEJ trajektorii między migawkami — klient wyszedł
z kłopotów i się ustabilizował; powiedzieć: „badge opisuje stan bieżący,
wykres — drogę do niego; w szczytowej migawce kryzysowej ten klient miał
alert, dziś system raportuje stabilizację").

## 4. Migawka + wyjaśnienie SHAP (~1.5 min)

**Klik:** w `demo-rising-001` → **+ Add snapshot** → data = dziś, „kopiuj
z poprzedniej migawki" → pogorszyć PAY_0 do 3 → **Submit**.
**Oczekiwany widok:** nowy punkt na Timeline + panel SHAP pod formularzem
(rozbieżne słupki; czerwone = podnosi PD, na szczycie PAY_max/recent_pay_status).
**Powiedzieć:** „Każda ocena ma wyjaśnienie: top-5 cech per model. Analityk
widzi nie tylko »ile«, ale »dlaczego« — wymóg wyjaśnialności z AI Act."

## 5. Puenta (~30 s)

„Statyka odpowiada na pytanie »jaki jest klient dzisiaj«. Monitoring — »dokąd
klient zmierza«. W eksperymencie reguła monitorująca daje ~2 okna wyprzedzenia
i kilkadziesiąt wykryć na model, których pojedyncza ocena nie złapie nigdy."

---

## PLAN B (awaria na sali)

Objaw: biały ekran / błąd sieci / kontener padł.
1. NIE debugować na sali. Przełączyć na kartę `demo_zapas/`.
2. Przejść zrzuty w kolejności `01_…` → `06_…` (lub odtworzyć `demo.mp4`),
   z TĄ SAMĄ narracją co wyżej (punkty 1–5).
3. Zdanie ratunkowe: „Pokażę Państwu przebieg zarejestrowany na tym samym
   środowisku — wersja na żywo dostępna po prezentacji."

## Materiał awaryjny — do zebrania podczas próby generalnej

- `demo_zapas/01_prediction.png` — karty wyników Prediction
- `demo_zapas/02_trajektoria.png` — Timeline 5 linii (predict-timeseries)
- `demo_zapas/03_lista_klientow.png` — ClientList z badge'ami 3 alertów
- `demo_zapas/04_rising_historia.png` — historia demo-rising-001
- `demo_zapas/05_snapshot_form.png` — formularz migawki z datą
- `demo_zapas/06_shap.png` — panel SHAP po dodaniu migawki
- (opcjonalnie) `demo_zapas/demo.mp4` — nagranie całego przebiegu
