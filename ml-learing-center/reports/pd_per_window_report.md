# B1: Diagnoza PD per okno — narastanie ryzyka czy przesunięcie rozkładu?

Pytanie: czy dominacja pierwszych alertów w najstarszym oknie W0 (`lead_time_report.md`) to realny sygnał wczesnego ryzyka, czy artefakt aplikowania modelu trenowanego na W3 do danych W0?

Kryterium: jeśli średnie PD na W0 jest podwyższone względem W3 **także dla klientów spłacających (y=0)** — mamy przesunięcie rozkładu; jeśli tylko dla defaultujących (y=1) — sygnał jest merytoryczny.

| Model | ΔPD W0−W3 (y=0) | ΔPD W0−W3 (y=1) | Alert rate y=0: W0 vs W3 | Werdykt |
|---|---:|---:|---|---|
| Random Forest | -0.0023 | -0.0685 | 34.6% vs 35.8% | brak istotnego dryfu / mieszany |
| XGBoost | -0.0039 | -0.0705 | 33.2% vs 35.2% | brak istotnego dryfu / mieszany |
| LightGBM | -0.0024 | -0.0689 | 34.1% vs 35.4% | brak istotnego dryfu / mieszany |
| CatBoost | -0.0032 | -0.0712 | 36.0% vs 37.4% | brak istotnego dryfu / mieszany |
| LSTM | +0.0040 | -0.0646 | 45.4% vs 39.6% | brak istotnego dryfu / mieszany |

Pełne rozkłady: `pd_per_window_diagnostic.csv` + `pd_per_window_<model>.png`.

**Jak używać na obronie:** jeśli dla części modeli PD na W0 jest zawyżone również dla klasy y=0, histogram lead time należy interpretować ostrożnie: część 'wczesnych' alertów to koszt przesunięcia rozkładu, nie narastanie ryzyka — i dokładnie dlatego porównanie static-vs-dynamic wykonujemy przy stałym budżecie fałszywych alarmów, który ten efekt neutralizuje.
