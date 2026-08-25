# Checklista próby obrony (etap wspólny — po v9 i po próbie demo)

> Warunki wejścia: `Praca Magisterska-9.pdf` przechodzi walidator (16/16 🟢),
> demo przeszło próbę generalną, `demo_zapas/` uzupełnione.
> Wynik próby: każdą wykrytą niespójność wpisać do tabeli na dole
> z przypisaniem toru (Tor 1 = tekst/skład, Tor 2 = demo/Q&A/slajdy).

## Przebieg próby (jedna sesja, mierzyć czas)

- [ ] **Slajdy 1–5** (kontekst, architektura, dane, modele, kalibracja) — cel ≤ 8 min.
- [ ] Po slajdzie o modelach: wylosować 1 pytanie z `obrona_QA.md` część B
      (B1/B4/B5) i odpowiedzieć bez zaglądania do części odpowiedziowej.
- [ ] **Slajd 6 ⭐ (dowód tezy)** — sprawdzić, że mówisz wersję PO leakage-fix:
      4 modele przegrywają @FA=10%, LSTM +2,6 pp, unikalne wykrycia 39–74,
      lead ~2 okna. Wylosować B2 i B3.
- [ ] **Slajd fairness** — dekompozycja: luka strukturalna 0,021 + wynik bez SEX.
      Wylosować 2 pytania z części A (obowiązkowo A1 i jedno z A2/A3/A6).
- [ ] **Demo** wg `prezentacja_seminarium/demo_scenariusz.md` — cel ≤ 9 min,
      z narracją „stan bieżący vs droga" przy demo-falling-003.
- [ ] **Puenta + kierunki dalszych badań** — 1 min.

## Spójność trzech artefaktów (spot-check przy próbie)

Dla każdej liczby: praca (v9) ↔ ściąga (`obrona_QA.md` C) ↔ slajdy
(`Slajdy_Seminarium.md`) muszą się zgadzać:

- [ ] AUC ×5 (0,7741 / 0,7761 / 0,7767 / 0,7793 / 0,7614)
- [ ] Progi (0,145 / 0,165 / 0,160 / 0,160 / 0,155)
- [ ] Δ @FA=10% (−10,9 / −5,1 / −5,0 / −6,4 / **+2,6**)
- [ ] DPD/EOD (max 0,039/0,033; LSTM 0,006/0,021)
- [ ] Brier po kalibracji (−19/−24/−25%)
- [ ] Lead ~2 okna; unikalne 39–74; luka strukturalna 0,021
- [ ] H1: −0,51/−0,57/−0,72 pp

## Niespójności wykryte podczas próby

| # | Co się nie zgadza | Gdzie (praca/slajd/ściąga/demo) | Tor | Status |
|---|---|---|---|---|
| 1 | | | | |
| 2 | | | | |

## Kryterium wyjścia

- [ ] Całość ≤ 25 min (prezentacja + demo), bez zaglądania do notatek poza ściągą.
- [ ] Zero niespójności otwartych w tabeli.
- [ ] Odpowiedzi na wylosowane pytania ocenione jako „obronne" przez słuchacza próby.
