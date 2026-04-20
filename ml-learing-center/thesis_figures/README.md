# Wykresy do pracy magisterskiej

Kompletny zestaw ~38 wykresów akademickich do pracy dyplomowej
„Zastosowanie uczenia maszynowego w ocenie zdolności kredytowej".

## Szybki start

```bash
# Zależności systemowe
brew install graphviz          # macOS
# sudo apt-get install graphviz  # Linux

# Zależności Python
pip install -r requirements.txt

# Uruchom wszystkie wykresy
python generate_all.py

# Albo tylko wybrany rozdział
python generate_all.py --chapter 3

# Wymuś retrening (ignoruj cache)
THESIS_NO_CACHE=1 python generate_all.py
```

Wyniki pojawią się w `output/rozdzial_{1..5}/` jako PNG (300 DPI) + SVG.
Opisy wszystkich figur automatycznie trafiają do `output/README.md`.

## Struktura

- `common/` — wspólny styl, dostęp do danych, modeli i cache
- `rozdzial_1..5/` — osobny skrypt na każdą figurę
- `cache/` — artefakty eksperymentów (krzywe uczenia, SHAP, grid search)
- `output/` — gotowe wykresy PNG + SVG
- `generate_all.py` — master script

## Wykorzystane źródła

- Dane: `../default_of_credit_card_clients.csv` (UCI: default of credit card clients)
- Modele: `../../ml-service/{rf_model.pkl,xgb_model.pkl,lstm_model.keras}` wytrenowane przez `../main.py`
