# Ścieżka do obrony — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Doprowadzić projekt do stanu „gotowy do obrony": paczka LaTeX z pełną treścią pracy (v9) + automatyczny walidator PDF, materiały obrony (Q&A, ściąga) i przećwiczone demo z planem awaryjnym.

**Architecture:** Dwa niezależne tory ze specu `docs/superpowers/specs/2026-07-07-sciezka-do-obrony-design.md`. Tor 1 (Taski 1–5): figury → walidator → paczka LaTeX. Tor 2 (Taski 6–8): Q&A → higiena DB + demo → materiał awaryjny. Task 9 (wspólny) wymaga v9 od użytkownika. Task 1 uruchamiać NAJPIERW (wielogodzinny sweep w tle), potem Taski 2–8 w dowolnym przeplocie; jedyna twarda zależność: 9 po (v9 ∧ 7 ∧ 8).

**Tech Stack:** Python 3.11 (venv: `ml-learing-center/.venv`), matplotlib/sklearn/xgboost, pypdf, pytest; LaTeX (kompilacja docelowa w Overleafie użytkownika, lokalny smoke test jeśli dostępny `pdflatex`/`tectonic`); docker compose (Postgres/backend/ml-service).

## Global Constraints

- **Zamrożenie artefaktów:** żadnych retrainów nadpisujących `*_w3.pkl` / `lstm_model_w3.keras` / `alert_thresholds.json`. Jedyny dopuszczalny trening: pomocnicze modele figur (Task 1, 2) — wyniki zapisywane WYŁĄCZNIE jako PNG/CSV, nigdy `joblib.dump`/`model.save` na ścieżki artefaktów.
- **Jedno źródło liczb:** `ml-learing-center/reports/*.csv` + `FINAL_REPORT.md`; żadna liczba nie jest wpisywana z pamięci.
- **Interpreter:** zawsze `ml-learing-center/.venv/bin/python` (systemowy python3 = 3.9, nie odczyta artefaktów).
- **Reprodukowalność:** wszędzie `random_state=42` / `set_random_seed(42)`.
- **Podpisy figur po polsku**; zapis przez `thesis_figures/common.save_figure` (PNG 300 DPI + SVG do `thesis_figures/output/rozdzial_N/`).
- **Split kanoniczny:** 60/20/20, `train_test_split(..., test_size=0.2, stratify=y, random_state=42)` → potem `test_size=0.25` na reszcie (jak `main.py`).
- **Commity:** po każdym tasku, bez trailera Co-Authored-By.
- **Poza zakresem planu:** CREDIT-304, F3/F4 (spec: tylko przy zapasie czasu, osobna decyzja).

## File Structure

```
ml-learing-center/
  thesis_figures/rozdzial_4/
    fig_4_1_podzial_zbioru.py        # NOWY — diagram 60/20/20
    fig_4_3_krzywe_uczenia_lstm.py   # NOWY — retrain z history (bez zapisu modelu)
    fig_4_5_heatmapa_rf_cv.py        # NOWY — CV-AUC heatmapa (Task 1, tło)
    fig_4_6_waznosc_cech_rf.py       # NOWY — top-20 importance
    fig_4_7_heatmapa_xgb_cv.py       # NOWY — CV-AUC heatmapa (Task 1, tło)
    fig_4_8_shap_global_xgb.py       # NOWY — beeswarm + bar
  validate_thesis.py                 # NOWY — silnik checków + ekstrakcja PDF
  validate_thesis_test.py            # NOWY — testy silnika na fixtures
docs/thesis/latex/
  rozdzial3.tex, rozdzial4_nowe_sekcje.tex, rozdzial5.tex, zakonczenie.tex
  bibliografia_nowe.tex, main_test.tex
  rozdzial4_instrukcje.md, checklista_skladu.md, FIGURY.md
docs/thesis/obrona_QA.md             # NOWY — Q&A + ściąga liczb
prezentacja_seminarium/demo_scenariusz.md  # NOWY — scenariusz + plan awaryjny
WalidacjaPDFv9.md                    # GENEROWANY przez validate_thesis.py
```

---

### Task 1: Heatmapy CV-AUC (RF + XGB) — uruchomić PIERWSZE, liczy się w tle

**Files:**
- Create: `ml-learing-center/thesis_figures/rozdzial_4/fig_4_5_heatmapa_rf_cv.py`
- Create: `ml-learing-center/thesis_figures/rozdzial_4/fig_4_7_heatmapa_xgb_cv.py`

**Interfaces:**
- Consumes: `features.engineer_features`, `sliding_window.WINDOW_DEFS`, `common.save_figure`
- Produces: `thesis_figures/output/rozdzial_4/fig_4_5_heatmapa_rf_cv.png` i `fig_4_7_heatmapa_xgb_cv.png` + CSV z wynikami sweepa (`reports/heatmap_{rf,xgb}_cv.csv`). Zastępują w pracy stare heatmapy strojone na AUC testowym (finding #7 Fable5_Task1).

- [ ] **Step 1: Napisz `fig_4_5_heatmapa_rf_cv.py`**

```python
"""Rysunek 4.5 — Random Forest: wpływ n_estimators × max_depth na CV-AUC (train, 5-fold).

Zastępuje heatmapę liczoną na AUC testowym. Trenuje WYŁĄCZNIE modele pomocnicze
figur — niczego nie zapisuje poza PNG/CSV.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # thesis_figures/
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))   # ml-learing-center/

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from common import apply_style, save_figure
from features import engineer_features
from sliding_window import WINDOW_DEFS

apply_style()
HERE = Path(__file__).resolve().parents[2]
REPORTS = HERE / "reports"

N_ESTIMATORS = [50, 100, 200, 300, 500]
MAX_DEPTH = [4, 6, 8, 10, 14]
CHOSEN = (500, 10)  # konfiguracja z main.py


def train_split():
    df = pd.read_csv(HERE / "default_of_credit_card_clients.csv", header=1)
    df.rename(columns={"default payment next month": "Default"}, inplace=True)
    df.drop(columns=["ID"], inplace=True)
    for c in ["EDUCATION", "MARRIAGE", "SEX"]:
        df[c] = df[c].astype(int)
    y = df["Default"]
    X, _ = engineer_features(df, WINDOW_DEFS[3])
    X_tmp, _, y_tmp, _ = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
    X_tr, _, y_tr, _ = train_test_split(X_tmp, y_tmp, test_size=0.25, stratify=y_tmp, random_state=42)
    return X_tr.to_numpy(dtype=float), y_tr.to_numpy()


def build():
    X_tr, y_tr = train_split()
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    grid = np.zeros((len(MAX_DEPTH), len(N_ESTIMATORS)))
    rows = []
    for i, depth in enumerate(MAX_DEPTH):
        for j, n_est in enumerate(N_ESTIMATORS):
            model = RandomForestClassifier(
                n_estimators=n_est, max_depth=depth, min_samples_leaf=5,
                class_weight="balanced", random_state=42, n_jobs=-1)
            auc = cross_val_score(model, X_tr, y_tr, cv=cv, scoring="roc_auc").mean()
            grid[i, j] = auc
            rows.append({"n_estimators": n_est, "max_depth": depth, "cv_auc": auc})
            print(f"RF depth={depth} n={n_est}: CV-AUC={auc:.4f}", flush=True)
    pd.DataFrame(rows).to_csv(REPORTS / "heatmap_rf_cv.csv", index=False)

    fig, ax = plt.subplots(figsize=(9, 6))
    im = ax.imshow(grid, cmap="viridis", aspect="auto")
    ax.set_xticks(range(len(N_ESTIMATORS)), N_ESTIMATORS)
    ax.set_yticks(range(len(MAX_DEPTH)), MAX_DEPTH)
    ax.set_xlabel("n_estimators (liczba drzew)")
    ax.set_ylabel("max_depth (głębokość)")
    ax.set_title("Random Forest — CV-AUC (5-fold, zbiór treningowy W3)")
    for i in range(len(MAX_DEPTH)):
        for j in range(len(N_ESTIMATORS)):
            ax.text(j, i, f"{grid[i, j]:.4f}", ha="center", va="center",
                    color="white", fontsize=9)
    ci, cj = MAX_DEPTH.index(CHOSEN[1]), N_ESTIMATORS.index(CHOSEN[0])
    ax.add_patch(plt.Rectangle((cj - .5, ci - .5), 1, 1, fill=False,
                               edgecolor="red", linewidth=2.5))
    fig.colorbar(im, ax=ax, label="CV-AUC")
    return fig


if __name__ == "__main__":
    save_figure(build(), chapter=4, idx="5", name="heatmapa_rf_cv",
                comment="RF: CV-AUC 5-fold na treningu W3; czerwona ramka = konfiguracja z main.py (500, 10).")
```

- [ ] **Step 2: Napisz `fig_4_7_heatmapa_xgb_cv.py`** — identyczna struktura, różnice:

```python
# zamiast N_ESTIMATORS/MAX_DEPTH/CHOSEN/modelu:
LEARNING_RATE = [0.005, 0.01, 0.02, 0.05, 0.1]
MAX_DEPTH = [3, 4, 5, 6, 8]
CHOSEN = (0.02, 4)  # (learning_rate, max_depth) z main.py
# w pętli (i=depth, j=lr):
from xgboost import XGBClassifier
model = XGBClassifier(
    n_estimators=800, learning_rate=lr, max_depth=depth,
    subsample=0.7, colsample_bytree=0.7, reg_alpha=0.1, reg_lambda=1.0,
    scale_pos_weight=(len(y_tr) - y_tr.sum()) / y_tr.sum(),
    random_state=42, eval_metric="auc", n_jobs=-1)
# CSV: reports/heatmap_xgb_cv.csv; osie: xlabel="learning_rate", tytuł XGBoost;
# save_figure(..., chapter=4, idx="7", name="heatmapa_xgb_cv", ...)
# cmap="magma" dla odróżnienia od RF.
```

- [ ] **Step 3: Uruchom oba W TLE (nie blokuj kolejnych tasków)**

Run: `cd ml-learing-center && (.venv/bin/python thesis_figures/rozdzial_4/fig_4_5_heatmapa_rf_cv.py && .venv/bin/python thesis_figures/rozdzial_4/fig_4_7_heatmapa_xgb_cv.py) > /tmp/heatmap_sweep.log 2>&1 &` (run_in_background)
Expected (po godz.): w logu linie `RF depth=... CV-AUC=...`, na końcu `[OK] fig_4_5_heatmapa_rf_cv.png` i `[OK] fig_4_7_heatmapa_xgb_cv.png`.

- [ ] **Step 4: Po zakończeniu sweepa — weryfikacja i commit**

Run: `ls ml-learing-center/thesis_figures/output/rozdzial_4/ | grep -E "4_5|4_7"` → 4 pliki (PNG+SVG ×2). Sanity: w `heatmap_rf_cv.csv` wartości CV-AUC w przedziale 0.76–0.79; konfiguracja (500,10) w top-3.

```bash
git add ml-learing-center/thesis_figures/rozdzial_4/fig_4_{5,7}_*.py ml-learing-center/thesis_figures/output/rozdzial_4/ ml-learing-center/reports/heatmap_*.csv
git commit --no-gpg-sign -m "feat(figures): heatmapy 4.5/4.7 przeliczone na CV-AUC (train, 5-fold) — usuwa strojenie-na-tescie z pracy"
```

---

### Task 2: Pozostałe figury rozdziału 4 (4.1, 4.3, 4.6, 4.8)

**Files:**
- Create: `ml-learing-center/thesis_figures/rozdzial_4/fig_4_1_podzial_zbioru.py`
- Create: `ml-learing-center/thesis_figures/rozdzial_4/fig_4_3_krzywe_uczenia_lstm.py`
- Create: `ml-learing-center/thesis_figures/rozdzial_4/fig_4_6_waznosc_cech_rf.py`
- Create: `ml-learing-center/thesis_figures/rozdzial_4/fig_4_8_shap_global_xgb.py`

**Interfaces:**
- Consumes: artefakty `rf_model_w3.pkl`/`xgb_model_w3.pkl`/`features_w3.pkl`/`scaler_w3.pkl` (tylko odczyt), `features.py`, `common.save_figure`, wzorzec nagłówka jak w Task 1.
- Produces: 4 × PNG/SVG w `thesis_figures/output/rozdzial_4/` o nazwach `fig_4_{1,3,6,8}_*`.

- [ ] **Step 1: `fig_4_1_podzial_zbioru.py`** (szybki, bez treningu)

```python
"""Rysunek 4.1 — podział 60/20/20 (zastępuje błędny 56/14/30)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import matplotlib.pyplot as plt
from common import apply_style, save_figure
apply_style()

SIZES = [18000, 6000, 6000]
LABELS = ["Trening\n18 000 (60%)", "Kalibracja\n6 000 (20%)", "Test\n6 000 (20%)"]
COLORS = ["#1f3a68", "#d4a017", "#a63446"]

def build():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))
    ax1.pie(SIZES, labels=LABELS, colors=COLORS, startangle=90,
            wedgeprops={"width": 0.42, "edgecolor": "white"})
    ax1.set_title("Podział zbioru (30 000 rekordów)")
    left = 0
    for size, lab, col in zip(SIZES, LABELS, COLORS):
        ax2.barh(0, size, left=left, color=col, edgecolor="white")
        ax2.text(left + size / 2, 0, lab.replace("\n", " "), ha="center",
                 va="center", color="white", fontsize=9, fontweight="bold")
        left += size
    ax2.set_xlim(0, 30000); ax2.set_yticks([])
    ax2.set_title("Proporcje na osi liniowej (stratyfikacja, random_state=42)")
    fig.suptitle("Podział train / kalibracja / test — 60/20/20", fontweight="bold")
    fig.tight_layout()
    return fig

if __name__ == "__main__":
    save_figure(build(), chapter=4, idx="1", name="podzial_zbioru",
                comment="Trójdzielny split 60/20/20 z osobną częścią kalibracyjną.")
```

- [ ] **Step 2: `fig_4_3_krzywe_uczenia_lstm.py`** — retrain W3 LSTM z historią, deterministyczny, **bez zapisu modelu**:

```python
"""Rysunek 4.3 — krzywe uczenia LSTM W3 (accuracy + loss, train/val).

Retrenuje LSTM identycznie jak main.py (seed 42) wyłącznie po history.
NIE zapisuje modelu — artefakty produkcyjne nietknięte.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input
from tensorflow.keras.models import Sequential
from common import apply_style, save_figure
from features import prepare_lstm_sequences
from sliding_window import WINDOW_DEFS

apply_style()
HERE = Path(__file__).resolve().parents[2]

def build():
    df = pd.read_csv(HERE / "default_of_credit_card_clients.csv", header=1)
    df.rename(columns={"default payment next month": "Default"}, inplace=True)
    df.drop(columns=["ID"], inplace=True)
    y = df["Default"]
    W3 = WINDOW_DEFS[3]
    idx = np.arange(len(df))
    idx_tmp, _ = train_test_split(idx, test_size=0.2, stratify=y, random_state=42)
    idx_tr, _ = train_test_split(idx_tmp, test_size=0.25, stratify=y.iloc[idx_tmp], random_state=42)
    _, scalers = prepare_lstm_sequences(df.iloc[idx_tr], W3)
    X_seq, _ = prepare_lstm_sequences(df, W3, scalers=scalers)
    Xs_tmp, _, ys_tmp, _ = train_test_split(X_seq, y, test_size=0.2, stratify=y, random_state=42)
    Xs_tr, _, ys_tr, _ = train_test_split(Xs_tmp, ys_tmp, test_size=0.25, stratify=ys_tmp, random_state=42)

    tf.keras.utils.set_random_seed(42)
    model = Sequential([Input(shape=(3, 3)), LSTM(32), Dropout(0.3),
                        Dense(16, activation="relu"), Dense(1, activation="sigmoid")])
    model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy", "AUC"])
    cw = compute_class_weight(class_weight="balanced", classes=np.array([0, 1]), y=ys_tr.values)
    hist = model.fit(Xs_tr, ys_tr, validation_split=0.2, epochs=60, batch_size=256,
                     class_weight={0: cw[0], 1: cw[1]},
                     callbacks=[EarlyStopping(monitor="val_auc", mode="max", patience=5, restore_best_weights=True),
                                ReduceLROnPlateau(monitor="val_auc", mode="max", factor=0.5, patience=3, min_lr=1e-5)],
                     verbose=2).history

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))
    ep = range(1, len(hist["loss"]) + 1)
    ax1.plot(ep, hist["accuracy"], "o-", label="trening")
    ax1.plot(ep, hist["val_accuracy"], "s-", label="walidacja")
    ax1.set_xlabel("Epoka"); ax1.set_ylabel("Accuracy"); ax1.set_title("Krzywa dokładności"); ax1.legend()
    ax2.plot(ep, hist["loss"], "o-", label="trening")
    ax2.plot(ep, hist["val_loss"], "s-", label="walidacja")
    ax2.set_xlabel("Epoka"); ax2.set_ylabel("Binary crossentropy"); ax2.set_title("Krzywa funkcji straty"); ax2.legend()
    fig.suptitle("Krzywe uczenia modelu LSTM (W3, seed=42)", fontweight="bold")
    fig.tight_layout()
    return fig

if __name__ == "__main__":
    save_figure(build(), chapter=4, idx="3", name="krzywe_uczenia_lstm",
                comment="Krzywe uczenia W3 LSTM z EarlyStopping; retrain deterministyczny, model niezapisywany.")
```

- [ ] **Step 3: `fig_4_6_waznosc_cech_rf.py`** — top-20 importance z produkcyjnego artefaktu:

```python
"""Rysunek 4.6 — top-20 ważności cech Random Forest (W3, artefakt produkcyjny)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import joblib
import numpy as np
import matplotlib.pyplot as plt
from common import apply_style, save_figure
apply_style()
HERE = Path(__file__).resolve().parents[2]

def build():
    rf_cal = joblib.load(HERE / "rf_model_w3.pkl")
    base = rf_cal.calibrated_classifiers_[0].estimator
    base = getattr(base, "estimator", base)  # FrozenEstimator unwrap
    feats = joblib.load(HERE / "features_w3.pkl")
    imp = base.feature_importances_
    order = np.argsort(imp)[::-1][:20]
    fig, ax = plt.subplots(figsize=(9, 7))
    ax.barh(range(19, -1, -1), imp[order], color=plt.cm.viridis(np.linspace(0.2, 0.9, 20)))
    ax.set_yticks(range(19, -1, -1), [feats[i] for i in order])
    ax.set_xlabel("Istotność cechy (Gini importance)")
    ax.set_title("Top 20 cech wg istotności — Random Forest (W3)")
    fig.tight_layout()
    return fig

if __name__ == "__main__":
    save_figure(build(), chapter=4, idx="6", name="waznosc_cech_rf",
                comment="Ważności Gini estymatora bazowego RF W3 (spod CalibratedClassifierCV).")
```

- [ ] **Step 4: `fig_4_8_shap_global_xgb.py`** — beeswarm + bar na próbce 1000 z testu:

```python
"""Rysunek 4.8 — globalny SHAP XGBoost (beeswarm + bar, n=1000 z testu)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import shap
from sklearn.model_selection import train_test_split
from common import apply_style, save_figure
from features import engineer_features
from sliding_window import WINDOW_DEFS
apply_style()
HERE = Path(__file__).resolve().parents[2]

def build():
    df = pd.read_csv(HERE / "default_of_credit_card_clients.csv", header=1)
    df.rename(columns={"default payment next month": "Default"}, inplace=True)
    df.drop(columns=["ID"], inplace=True)
    for c in ["EDUCATION", "MARRIAGE", "SEX"]:
        df[c] = df[c].astype(int)
    y = df["Default"]
    X, _ = engineer_features(df, WINDOW_DEFS[3])
    feats = joblib.load(HERE / "features_w3.pkl")
    scaler = joblib.load(HERE / "scaler_w3.pkl")
    _, X_te, _, _ = train_test_split(X[feats], y, test_size=0.2, stratify=y, random_state=42)
    rng = np.random.default_rng(42)
    sample = X_te.iloc[rng.choice(len(X_te), 1000, replace=False)]
    X_s = scaler.transform(sample)

    xgb_cal = joblib.load(HERE / "xgb_model_w3.pkl")
    base = xgb_cal.calibrated_classifiers_[0].estimator
    base = getattr(base, "estimator", base)
    sv = shap.TreeExplainer(base).shap_values(X_s)
    sv = np.asarray(sv)
    if sv.ndim == 3:
        sv = sv[..., -1]

    fig = plt.figure(figsize=(13, 6))
    plt.subplot(1, 2, 1)
    shap.summary_plot(sv, X_s, feature_names=feats, max_display=15, show=False, plot_size=None)
    plt.title("SHAP beeswarm — top 15 cech")
    plt.subplot(1, 2, 2)
    shap.summary_plot(sv, X_s, feature_names=feats, max_display=15, plot_type="bar", show=False, plot_size=None)
    plt.title("Średnia |SHAP| — istotność globalna")
    plt.suptitle("Wyjaśnialność XGBoost (W3) — wartości SHAP, n=1000 z testu", fontweight="bold")
    plt.tight_layout()
    return plt.gcf()

if __name__ == "__main__":
    save_figure(build(), chapter=4, idx="8", name="shap_global_xgb",
                comment="Globalny SHAP estymatora bazowego XGB (skala margin, ranking cech zachowany).")
```

- [ ] **Step 5: Uruchom wszystkie 4 i zweryfikuj**

Run: `cd ml-learing-center && for f in 1_podzial_zbioru 3_krzywe_uczenia_lstm 6_waznosc_cech_rf 8_shap_global_xgb; do .venv/bin/python thesis_figures/rozdzial_4/fig_4_$f.py; done`
Expected: 4 × `[OK] fig_4_..png`. Sanity fig_4_6: na szczycie listy cechy płatnicze (PAY_max/late_count/recent_pay_status), nie demograficzne. Sanity fig_4_3: krzywa val nie eksploduje. Sprawdź też: `git status --short ml-learing-center/*.pkl *.keras` → PUSTO (artefakty nietknięte).

- [ ] **Step 6: Commit**

```bash
git add ml-learing-center/thesis_figures/rozdzial_4/ ml-learing-center/thesis_figures/output/
git commit --no-gpg-sign -m "feat(figures): rys. 4.1 (60/20/20), 4.3 (krzywe LSTM), 4.6 (RF importance), 4.8 (SHAP global XGB)"
```

---

### Task 3: `validate_thesis.py` — automatyczny walidator PDF (TDD)

**Files:**
- Create: `ml-learing-center/validate_thesis.py`
- Create: `ml-learing-center/validate_thesis_test.py`
- Modify: `ml-learing-center/requirements.txt` (dopisać `pypdf>=4.0`)
- Modify: `.github/workflows/ci.yml` (job ml-training-tests: `python -m pytest sliding_window_test.py validate_thesis_test.py -v` + `pip install ... pypdf`)

**Interfaces:**
- Consumes: `reports/metrics_w3.csv`, `../ml-service/alert_thresholds.json` (liczby do checków).
- Produces: `run_checks(text: str, reports_dir: Path) -> list[Check]` gdzie `Check = dataclass(id, ok: bool, description, detail)`; CLI: `validate_thesis.py <pdf>` → pisze `WalidacjaPDFv9.md` w katalogu PDF-a i kończy exit 1 przy czerwonych.

- [ ] **Step 1: Napisz failing testy**

```python
# ml-learing-center/validate_thesis_test.py
"""Testy silnika checków walidatora pracy (na fixtures tekstowych, bez PDF)."""
from pathlib import Path
import pytest
from validate_thesis import run_checks

REPORTS = Path(__file__).parent / "reports"

GOOD = """
Rozdział 3. Metodologia badań """ + "x" * 6000 + """ H1 H2 H3 60/20/20
Rozdział 4. Implementacja pięć klasyfikatorów LightGBM CatBoost
kalibracja izotoniczna 0,145 0,165 DPD EOD
Rozdział 5. Analiza wyników """ + "x" * 9000 + """ 0,7793 0,7741
Zakończenie """ + "x" * 1500 + """
Bibliografia
"""

BAD = """
Rozdział 3. Metodologia badań
Rozdział 4. Implementacja zaimplementowano trzy różne klasyfikatory
wydzielono zbiór testowy o udziale 30%, co odpowiada 9 000 obserwacji
Wejście sieci ma wymiar (6, 3)
Rozdział 5. Analiza wyników
Zakończenie
Bibliografia
"""

def _by_id(checks):
    return {c.id: c for c in checks}

def test_good_text_passes_structural_and_content_checks():
    res = _by_id(run_checks(GOOD, REPORTS))
    for cid in ["ch3_nonempty", "ch5_nonempty", "zakonczenie_nonempty",
                "split_602020", "hipotezy", "five_models", "auc_catboost",
                "thresholds", "fairness_terms", "no_three_classifiers",
                "no_old_split", "no_lstm_63"]:
        assert res[cid].ok, f"{cid}: {res[cid].detail}"

def test_bad_text_fails_relic_checks():
    res = _by_id(run_checks(BAD, REPORTS))
    assert not res["no_three_classifiers"].ok
    assert not res["no_old_split"].ok
    assert not res["no_lstm_63"].ok
    assert not res["ch3_nonempty"].ok      # brak treści po nagłówku
    assert not res["auc_catboost"].ok

def test_check_count_at_least_15():
    assert len(run_checks(GOOD, REPORTS)) >= 15
```

- [ ] **Step 2: Uruchom — musi FAILować**

Run: `cd ml-learing-center && .venv/bin/python -m pytest validate_thesis_test.py -v`
Expected: FAIL `ModuleNotFoundError: No module named 'validate_thesis'`

- [ ] **Step 3: Napisz implementację**

```python
# ml-learing-center/validate_thesis.py
"""Walidator PDF pracy (lista R3 z Fable5_Task1.md).

Użycie: .venv/bin/python validate_thesis.py "../Praca Magisterska-9.pdf"
Zapisuje WalidacjaPDFv9.md obok PDF-a; exit 1 gdy jakikolwiek check czerwony.
"""
from __future__ import annotations
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass
class Check:
    id: str
    ok: bool
    description: str
    detail: str = ""


def _num_variants(v: float, nd: int = 4) -> list[str]:
    """'0.7793' i '0,7793' (+ wariant 3-cyfrowy) — PDF-y używają przecinka."""
    s4 = f"{v:.{nd}f}"
    s3 = f"{v:.3f}"
    return [s4, s4.replace(".", ","), s3, s3.replace(".", ",")]


def _section_len(text: str, start_pat: str, end_pat: str) -> int:
    m1 = re.search(start_pat, text)
    m2 = re.search(end_pat, text)
    if not m1 or not m2 or m2.start() <= m1.end():
        return 0
    return len(text[m1.end():m2.start()].strip())


def run_checks(text: str, reports_dir: Path) -> list[Check]:
    metrics = pd.read_csv(reports_dir / "metrics_w3.csv").set_index("model")
    with open(reports_dir.parent.parent / "ml-service" / "alert_thresholds.json") as f:
        thr = json.load(f)
    checks: list[Check] = []

    def add(cid, ok, desc, detail=""):
        checks.append(Check(cid, bool(ok), desc, detail))

    def contains_any(variants):
        return any(v in text for v in variants)

    # — struktura (niepuste rozdziały) —
    add("ch3_nonempty", _section_len(text, r"Rozdział 3\.", r"Rozdział 4\.") > 5000,
        "Rozdział 3 ma treść (>5000 znaków)")
    add("ch5_nonempty", _section_len(text, r"Rozdział 5\.", r"Zakończenie") > 8000,
        "Rozdział 5 ma treść (>8000 znaków)")
    add("zakonczenie_nonempty", _section_len(text, r"Zakończenie", r"Bibliografia") > 1000,
        "Zakończenie ma treść (>1000 znaków)")
    # — wymagana zawartość —
    add("hipotezy", all(h in text for h in ["H1", "H2", "H3"]), "Hipotezy H1/H2/H3 obecne")
    add("split_602020", "60/20/20" in text, "Podział 60/20/20 opisany")
    add("five_models", text.count("LightGBM") >= 3 and text.count("CatBoost") >= 3,
        "LightGBM i CatBoost wielokrotnie w treści (5 modeli)")
    add("calibration", "izotoniczn" in text, "Kalibracja izotoniczna opisana")
    add("auc_catboost", contains_any(_num_variants(metrics.loc["CatBoost", "AUC"])),
        f"AUC CatBoost ({metrics.loc['CatBoost', 'AUC']:.4f}) w treści")
    add("auc_rf", contains_any(_num_variants(metrics.loc["Random Forest", "AUC"])),
        f"AUC RF ({metrics.loc['Random Forest', 'AUC']:.4f}) w treści")
    add("thresholds", contains_any(_num_variants(thr["randomForest"], 3))
        and contains_any(_num_variants(thr["xgboost"], 3)),
        "Progi kosztowe (RF, XGB) w treści")
    add("fairness_terms", "DPD" in text and "EOD" in text, "Metryki DPD/EOD w treści")
    # — relikty zakazane —
    add("no_three_classifiers", "trzy różne klasyfikatory" not in text,
        "Brak reliktu 'trzy różne klasyfikatory'")
    add("no_old_split", "9 000" not in text and "56% trenowanie" not in text,
        "Brak starego podziału 70/30 (9 000 / 56-14-30)")
    add("no_lstm_63", "ma wymiar (6, 3)" not in text,
        "Brak bezwarunkowego LSTM (6,3) — dopuszczalny tylko jako baseline")
    add("no_old_toc_53", "modeli LSTM, Random Forest i XGBoost" not in text,
        "TOC 5.3 nie wymienia 3 modeli")
    add("no_old_thr", "XGB=0.180" not in text and "LSTM=0.185" not in text,
        "Brak starych progów (0.180/0.185)")
    return checks


def main(pdf_path: str) -> int:
    from pypdf import PdfReader
    pdf = Path(pdf_path)
    text = "\n".join(p.extract_text() or "" for p in PdfReader(pdf).pages)
    checks = run_checks(text, Path(__file__).parent / "reports")
    red = [c for c in checks if not c.ok]
    lines = [f"# Walidacja {pdf.name} — {len(checks) - len(red)}/{len(checks)} OK", ""]
    for c in checks:
        lines.append(f"- {'🟢' if c.ok else '🔴'} `{c.id}` — {c.description}"
                     + (f" — {c.detail}" if c.detail else ""))
    out = pdf.parent / "WalidacjaPDFv9.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"{len(checks) - len(red)}/{len(checks)} OK -> {out}")
    return 1 if red else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
```

- [ ] **Step 4: Testy zielone**

Run: `cd ml-learing-center && .venv/bin/python -m pytest validate_thesis_test.py -v`
Expected: 3 passed.

- [ ] **Step 5: Sanity na v8 (musi wykryć znane braki)**

Run: `.venv/bin/pip install pypdf --quiet && .venv/bin/python validate_thesis.py "../Praca Magisterska-8.pdf"; echo "exit=$?"`
Expected: exit=1; w raporcie czerwone co najmniej: `ch3_nonempty`, `ch5_nonempty`, `zakonczenie_nonempty`, `no_three_classifiers`, `no_old_split`, `auc_catboost`. (Raport dla v8 usunąć po weryfikacji: `rm ../WalidacjaPDFv9.md`.)

- [ ] **Step 6: Dopisz pypdf do requirements + rozszerz CI i commit**

W `ml-learing-center/requirements.txt` dopisz linię `pypdf>=4.0`. W `.github/workflows/ci.yml`, w jobie `ml-training-tests`: `pip install pandas numpy scikit-learn pytest pypdf` oraz `python -m pytest sliding_window_test.py validate_thesis_test.py -v`.

```bash
git add ml-learing-center/validate_thesis.py ml-learing-center/validate_thesis_test.py ml-learing-center/requirements.txt .github/workflows/ci.yml
git commit --no-gpg-sign -m "feat(eval): validate_thesis.py — automatyczny walidator PDF pracy (15+ checkow z listy R3) + testy w CI"
```

---

### Task 4: Paczka LaTeX (`docs/thesis/latex/`)

**Files:**
- Create: `docs/thesis/latex/rozdzial3.tex`, `rozdzial4_nowe_sekcje.tex`, `rozdzial5.tex`, `zakonczenie.tex`, `bibliografia_nowe.tex`, `main_test.tex`
- Create: `docs/thesis/latex/rozdzial4_instrukcje.md`, `checklista_skladu.md`

**Interfaces:**
- Consumes: drafty `docs/thesis/Rozdzial3.md`, `Rozdzial4_poprawki.md` (część A→instrukcje, część B→tex), `Rozdzial5.md`; figury z Tasków 1–2 + istniejące `thesis_figures/output/rozdzial_5/` i `reports/*.png`.
- Produces: pliki `.tex` kompilujące się w `main_test.tex`; klucze bibliografii `hardt2016`, `bird2020`, `zadrozny2002`, `akiba2019`, `grinsztajn2022` używane w `\cite{}`.

- [ ] **Step 1: Konwersja draftów md → tex.** Zasady (stosować mechanicznie):
  - nagłówki: `## 3.1. Tytuł` → `\section{Tytuł}` (numeracja z klasy dokumentu; jeśli szablon użytkownika numeruje inaczej — sekcje bez numerów w tekście), `### 3.3.1.` → `\subsection{...}`;
  - tabele → `\begin{table}[h]\centering\begin{tabular}{...}\toprule ... \bottomrule\end{tabular}\caption{...}\end{table}` (pakiet booktabs); wszystkie tabele z draftów przenieść 1:1;
  - `[RYS: plik.png]` → `\begin{figure}[h]\centering\includegraphics[width=.9\textwidth]{plik}\caption{...}\end{figure}`;
  - `[NOWE: Hardt 2016]` → `\cite{hardt2016}` itd.;
  - polskie cudzysłowy `,,tekst''`; `%` → `\%`; `_` w nazwach cech → `\_` (lub `\texttt{}`);
  - bloki cytatów draftu (fragmenty „do wklejenia") w Rozdzial4_poprawki część B = zwykła proza sekcji 4.6/4.7/4.8;
  - usuń nagłówki-adnotacje draftów („Draft do wklejenia…", uwagi `>`).

- [ ] **Step 2: `bibliografia_nowe.tex`** — format zgodny z [1]–[31] pracy (thebibliography, pozycje numeryczne):

```tex
% Dopisać do środowiska thebibliography pracy (kontynuacja numeracji [32]–[36]):
\bibitem{hardt2016} Hardt M., Price E., Srebro N., ,,Equality of opportunity in supervised learning'' w \textit{Advances in Neural Information Processing Systems 29 (NeurIPS 2016)}, 2016, s. 3315--3323.
\bibitem{bird2020} Bird S. i in., ,,Fairlearn: A toolkit for assessing and improving fairness in AI''. Microsoft, raport techniczny MSR-TR-2020-32, 2020.
\bibitem{zadrozny2002} Zadrozny B., Elkan C., ,,Transforming classifier scores into accurate multiclass probability estimates'' w \textit{Proceedings of the 8th ACM SIGKDD}, 2002, s. 694--699.
\bibitem{akiba2019} Akiba T. i in., ,,Optuna: A next-generation hyperparameter optimization framework'' w \textit{Proceedings of the 25th ACM SIGKDD}, 2019, s. 2623--2631.
\bibitem{grinsztajn2022} Grinsztajn L., Oyallon E., Varoquaux G., ,,Why do tree-based models still outperform deep learning on typical tabular data?'' w \textit{Advances in Neural Information Processing Systems 35 (NeurIPS 2022)}, 2022.
% Miejsca cytowań: hardt2016+bird2020 -> 5.5b; zadrozny2002 -> 4.6; akiba2019 -> 4.4.1; grinsztajn2022 -> 5.2/5.3.
```

- [ ] **Step 3: `main_test.tex`** (wyłącznie smoke test składni — NIE szablon pracy):

```tex
\documentclass[12pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[polish]{babel}
\usepackage{booktabs,graphicx,amsmath}
\graphicspath{{../../..//ml-learing-center/thesis_figures/output/rozdzial_4/}{../../../ml-learing-center/thesis_figures/output/rozdzial_5/}{../../../ml-learing-center/reports/}}
\begin{document}
\input{rozdzial3}
\input{rozdzial4_nowe_sekcje}
\input{rozdzial5}
\input{zakonczenie}
\begin{thebibliography}{99}
\input{bibliografia_nowe}
\end{thebibliography}
\end{document}
```

- [ ] **Step 4: `rozdzial4_instrukcje.md`** — przenieś część A z `Rozdzial4_poprawki.md` jako listę 6 podmian „ZNAJDŹ (fraza z v8) → ZASTĄP (tekst)" + wskazanie plików figur do podmiany (4.1, 4.3, 4.5, 4.6, 4.7, 4.8 → nazwy z `thesis_figures/output/rozdzial_4/`). **`checklista_skladu.md`** — globalne poprawki: TOC 5.2 (+5.2.4/5.2.5), TOC 5.3 („pięciu badanych modeli"), strony TOC rozdz. 3, ZAMIANA podpisów rys. 4.3↔4.4, formatowanie 2.3.4, fraza „trzy badane algorytmy" w 2.1.1 → „pięć badanych algorytmów".

- [ ] **Step 5: Smoke test kompilacji (z fallbackiem)**

Run: `which pdflatex tectonic || echo BRAK`. Jeśli jest: `cd docs/thesis/latex && (pdflatex -interaction=nonstopmode main_test.tex || tectonic main_test.tex)`; Expected: powstaje `main_test.pdf`, zero `! LaTeX Error`. Jeśli BRAK: `brew install tectonic` (jeśli odmowa/offline — oznacz krok jako „smoke test wykona użytkownik w Overleafie", odnotuj w checklista_skladu.md).

- [ ] **Step 6: Commit**

```bash
git add docs/thesis/latex/
git commit --no-gpg-sign -m "feat(thesis): paczka LaTeX — rozdz. 3/4-nowe/5/zakonczenie + bibliografia + instrukcje skladu + smoke test"
```

---

### Task 5: `FIGURY.md` — mapa figur do składu

**Files:**
- Create: `docs/thesis/latex/FIGURY.md`

**Interfaces:**
- Consumes: outputy Tasków 1–2, istniejące PNG w `thesis_figures/output/rozdzial_5/` i `reports/` (roc_comparison_w3, calibration_comparison_w3, static_vs_dynamic_*, fairness_*, fig_5_10, pd_per_window_*).
- Produces: tabela „nr rysunku w pracy → plik → zmiana vs v8 → sekcja".

- [ ] **Step 1: Napisz FIGURY.md.** Tabela markdown z wierszami co najmniej dla: 4.1 (NOWY plik, 60/20/20 — stary pokazywał 56/14/30), 4.3 (NOWY — uwaga: w v8 podpisy 4.3/4.4 były zamienione), 4.5 (CV-AUC zamiast test-AUC; ramka na (500,10) zgodna z tekstem — stara ramka wskazywała depth=8), 4.6 (NOWY z artefaktu), 4.7 (CV-AUC; ramka (0.02, 4)), 4.8 (globalny SHAP), 5.x (roc_comparison_w3.png, pr_comparison_w3.png, calibration_comparison_w3.png → 5.2/5.3; static_vs_dynamic_{5 modeli}_w3.png → 5.4; pd_per_window_{5}.png → 5.4; fig_5_10_audyt_fairness.png → 5.5b; bootstrap_auc_w3.png → 5.3). Kolumna „ścieżka względem repo" dokładna.

- [ ] **Step 2: Weryfikacja — każdy plik z mapy istnieje**

Run: `grep -oE "[a-zA-Z0-9_/.-]+\.(png|svg)" docs/thesis/latex/FIGURY.md | sort -u | while read f; do [ -f "$f" ] || [ -f "ml-learing-center/$f" ] || echo "BRAK: $f"; done`
Expected: brak linii `BRAK:`.

- [ ] **Step 3: Commit**

```bash
git add docs/thesis/latex/FIGURY.md
git commit --no-gpg-sign -m "docs(thesis): mapa figur praca->pliki (FIGURY.md)"
```

**Po Taskach 4–5: przekazanie użytkownikowi** — skład w Overleafie wg `rozdzial4_instrukcje.md` + `checklista_skladu.md`, eksport `Praca Magisterska-9.pdf` do repo. Pętla: `validate_thesis.py` → poprawki → ponowny eksport, aż exit 0.

---

### Task 6: `docs/thesis/obrona_QA.md` — karty Q&A + ściąga liczb

**Files:**
- Create: `docs/thesis/obrona_QA.md`

**Interfaces:**
- Consumes: `Fable5_Task1.md` (pytania Q1–Q5), `Fable5_Task2.md` (§7 prompt F9 + §8), aktualne raporty: `FINAL_REPORT.md`, `fairness_no_sex_report.md`, `pd_per_window_report.md`, `bootstrap_auc_report.md`, `threshold_leakage_fix.md`.
- Produces: dokument z trzema częściami; ściąga zawiera hash `git rev-parse --short HEAD`.

- [ ] **Step 1: Napisz dokument.** Struktura i wymagana treść (odpowiedzi 3–5 zdań, KAŻDA liczba z raportów):
  - **Część A — fairness (8 pytań):** (1) czemu SEX w cechach → cel badawczy + kontr-eksperyment: |ΔAUC|≤0.001, DPD XGB 0.036→0.011, LGBM →0.007 + LSTM jako model „unaware by construction" (DPD 0.006); (2) DPD dodatnie = disparate impact? → dekompozycja: luka strukturalna 0.021 z base rate (M 23.4%/F 21.3%) + wnioskowanie z EOD; (3) czemu EO a nie DP → niekompatybilność DP z trafną oceną przy różnych base rate (idealny klasyfikator ma DPD≈0.021); (4) progi liczone na teście? → NAPRAWIONE, progi na splicie kalibracyjnym, dowód `threshold_leakage_fix.md`, werdykt audytu bez zmian; (5) jeden split, istotność? → bootstrap 40×, wszystkie |DPD/EOD| CI << 0.10; (6) mitygacja → proporcjonalność: audyt-bramka + usunięcie SEX (za darmo) + ThresholdOptimizer jako mechanizm warunkowy w warstwie wczesnego ostrzegania (human-in-the-loop, AI Act art. 10(5)); (7) czemu tylko SEX → standard literatury + DoD; pozostałe atrybuty jako kierunek; (8) LSTM najsprawiedliwszy — czemu nie on → asymetria: −1.8 pp AUC vs +2 pp parytetu; rola ablacyjna.
  - **Część B — ogólne (5 pytań Q1–Q5 z Task1, zaktualizowane):** Q1 strojenie na teście → heatmapy w pracy = CV-AUC (Task 1), Optuna 5-fold, uplift <0.5 pp; Q2 monitoring przegrywa @FA=10% → tak, dla 4 modeli statycznych (−5.0…−10.9 pp), ALE LSTM +2.6 pp; wartość = lead ~2 okna + 39–74 unikalnych wykryć; Q3 symulowany monitoring/horyzonty → ograniczenie jawne w rozdz. 3.3.4 + diagnoza B1: drzewa bez dryfu dla y=0 (Δ −0.002…−0.004), sygnał u y=1 realny (+0.065…0.071 ku W3), dryf tylko LSTM +0.004; Q4 SEX → odsyłacz do części A; Q5 LSTM najsłabszy → bootstrap: trójka drzew nierozróżnialna, CatBoost>RF/XGB rozróżnialne, wszystkie>LSTM; ale LSTM = jedyny wygrywający monitoringiem i najbliższy parytetu.
  - **Część C — ściąga liczb (1 strona):** tabela AUC/Brier/próg/DPD/EOD ×5 modeli; delty static-vs-dyn @FA=5/10/20; lead ~2.0; unikalne 39–74; base rates; luka strukturalna 0.021; bootstrap CI; wyniki no-SEX; stopka: `Artefakty: commit <hash>, 2026-07-07`.

- [ ] **Step 2: Weryfikacja liczb**

Run: `grep -oE "0[.,][0-9]{3,4}" docs/thesis/obrona_QA.md | sort -u | head -30` i porównaj każdą wartość z `reports/*.csv` / `FINAL_REPORT.md` (spot-check WSZYSTKICH unikalnych liczb — to dokument, z którym idzie się na obronę).

- [ ] **Step 3: Commit**

```bash
git add docs/thesis/obrona_QA.md
git commit --no-gpg-sign -m "docs(thesis): karty Q&A na obrone (fairness + ogolne) + sciaga liczb z hashem artefaktow"
```

---

### Task 7: Higiena DB + re-seed + smoke test demo

**Files:**
- Modify: brak (operacyjny; wynik = czysta baza + 3 klientów demo)

**Interfaces:**
- Consumes: `docker-compose.yml`, `ml-learing-center/seed_demo_clients.py`, naprawiony serwis (fix U1).
- Produces: działające środowisko demo z danymi policzonymi na naprawionych artefaktach.

- [ ] **Step 1: Wyczyść skażony wolumen i postaw środowisko**

Run: `cd /Users/gabrielfigur/Documents/GitHub/ai-credit-management && docker compose down -v && docker compose up -d --build`
Expected: 3 kontenery Up; `down -v` kasuje `pg_data` (snapshoty sprzed fixu U1 — decyzja ze specu).

- [ ] **Step 2: Poczekaj na health i sprawdź pustą bazę**

Run: `until curl -sf localhost:5001/health >/dev/null && curl -sf localhost:5120/api/v1/monitoring/clients >/dev/null; do sleep 3; done; curl -s localhost:5120/api/v1/monitoring/clients`
Expected: `{"clients":[]}`

- [ ] **Step 3: Seed + weryfikacja API**

Run: `ml-learing-center/.venv/bin/python ml-learing-center/seed_demo_clients.py` (jeśli `ModuleNotFoundError: requests` → `ml-learing-center/.venv/bin/pip install requests` i powtórz).
Potem: `curl -s localhost:5120/api/v1/monitoring/clients | python3 -m json.tool | grep -E "clientRef|latestAlert"`
Expected: 3 klientów; `demo-rising-001` → `INCREASING_RISK`, `demo-stable-002` → `STABLE`, `demo-falling-003` → `DECREASING_RISK`. Dodatkowo: `curl -s "localhost:5120/api/v1/monitoring/clients/demo-rising-001/history" | python3 -m json.tool | grep -c snapshotId` → 4.

- [ ] **Step 4: Weryfikacja UI (krok użytkownika lub wspólny)**

Run: `cd frontend/WebApp && npm run dev` → w przeglądarce `localhost:5173`, zakładka Monitoring: lista 3 klientów z badge'ami; klik demo-rising-001 → Timeline 5 linii; dodanie snapshotu → SHAP pod formularzem. Odnotuj wynik w commit message kroku 5.

- [ ] **Step 5: Commit znacznika (log operacyjny)**

```bash
git commit --no-gpg-sign --allow-empty -m "chore(demo): pg_data wyczyszczone i re-seed po fixie U1 — 3 klientow demo, alerty rising/stable/falling OK, UI 5 linii + SHAP OK"
```

---

### Task 8: Scenariusz demo + materiał awaryjny

**Files:**
- Create: `prezentacja_seminarium/demo_scenariusz.md`
- Create (user): `prezentacja_seminarium/demo_zapas/` (zrzuty/nagranie)

**Interfaces:**
- Consumes: działające środowisko z Task 7; `Slajdy_Seminarium.md` (sekcja live demo, ~linie 250–260).
- Produces: skrypt krok-po-kroku z timingiem + plan awaryjny; katalog z materiałem zapasowym.

- [ ] **Step 1: Napisz `demo_scenariusz.md`.** Zawartość: (0) pre-flight checklist (docker compose ps → 3×Up; curl health; npm run dev; karta z fallbackiem otwarta); (1) Prediction tab — formularz zdrowego klienta → 3 karty wyników (~2 min); (2) Monitoring — predict-timeseries tego samego klienta → Timeline 5 linii, porównanie okien (~3 min); (3) Stateful — ClientList → demo-rising-001 → historia 4 punktów → dodanie snapshotu z datą → SHAP „why this score?" (~4 min); (4) puenta: karta alertu INCREASING_RISK + odwołanie do progu kosztowego. Dla każdego kroku: dokładny URL/klik, oczekiwany widok, timing, „co powiedzieć" (1 zdanie). Sekcja PLAN B: przy awarii → otwórz `demo_zapas/` (nagranie lub zrzuty w kolejności kroków), narracja identyczna.

- [ ] **Step 2: Próba generalna z pomiarem czasu** (użytkownik przechodzi scenariusz; cel ≤ 10 min). Podczas próby wykonać zrzuty ekranu każdego kroku → `prezentacja_seminarium/demo_zapas/01_prediction.png … 06_shap.png` (i/lub nagranie ekranu `demo.mp4`).

- [ ] **Step 3: Weryfikacja i commit**

Run: `ls prezentacja_seminarium/demo_zapas/ | wc -l` → ≥ 6.

```bash
git add prezentacja_seminarium/demo_scenariusz.md prezentacja_seminarium/demo_zapas/
git commit --no-gpg-sign -m "docs(demo): scenariusz demo z timingiem + material awaryjny (zrzuty/nagranie po probie generalnej)"
```

---

### Task 9: Walidacja v9 + próba obrony (wymaga: PDF v9 od użytkownika, Taski 7–8 zamknięte)

**Files:**
- Create: `WalidacjaPDFv9.md` (generowany)
- Create: `docs/thesis/proba_obrony_checklist.md`

**Interfaces:**
- Consumes: `Praca Magisterska-9.pdf` (od użytkownika, w root repo), `validate_thesis.py` (Task 3), `obrona_QA.md` (Task 6), `demo_scenariusz.md` (Task 8).
- Produces: czysta walidacja (exit 0) + checklista próby obrony z wynikiem.

- [ ] **Step 1: Walidacja automatyczna (pętla)**

Run: `cd ml-learing-center && .venv/bin/python validate_thesis.py "../Praca Magisterska-9.pdf"; echo "exit=$?"`
Expected: `exit=0`, raport 15+/15+ 🟢. Przy czerwonych: lista trafia do użytkownika (poprawki w Overleafie) → ponowny eksport → powtórka kroku. Commit raportu przy każdym przebiegu.

- [ ] **Step 2: Spot-check spójności praca ↔ ściąga ↔ slajdy (10 liczb)**

Run: dla 10 wartości (AUC ×5, progi RF/XGB, DPD CatBoost, delta LSTM +2.6, lead ~2.0): `grep -l "<liczba>" docs/thesis/obrona_QA.md prezentacja_seminarium/Slajdy_Seminarium.md` + obecność w v9 potwierdzona walidatorem. Expected: każda liczba w ≥2 z 3 dokumentów (progi mogą nie występować w slajdach — wtedy 2/3 OK).

- [ ] **Step 3: `proba_obrony_checklist.md` + próba.** Checklista: slajdy 1–N z czasem, pytania z QA losowane po slajdach 6/8 (fairness/dowód tezy), demo wg scenariusza na końcu, rubryka „niespójności wykryte → tor". Użytkownik wykonuje próbę; wykryte problemy = nowe pozycje w checkliście z przypisaniem (Tor 1 = tekst/skład, Tor 2 = demo/QA).

- [ ] **Step 4: Commit końcowy**

```bash
git add WalidacjaPDFv9.md docs/thesis/proba_obrony_checklist.md
git commit --no-gpg-sign -m "docs(thesis): walidacja v9 czysta + checklista proby obrony"
```

---

## Self-Review (wykonany)

1. **Spec coverage:** Tor 1 pkt 1–4 → Taski 1, 2, 4, 5 (figury, .tex, biblio, checklisty); pętla v9 → Task 3 + 9; Tor 2 pkt 1–3 → Taski 6, 7, 8; etap wspólny → Task 9; polish — poza zakresem zgodnie ze specem (Global Constraints). Brak luk.
2. **Placeholdery:** brak TBD/TODO; kod kompletny w każdym kroku kodowym; treści dokumentów opisane zawartością wymaganą per punkt, ze źródłami liczb.
3. **Spójność typów/nazw:** `run_checks(text, reports_dir) -> list[Check]` używane spójnie w teście i CLI; nazwy figur `fig_4_{1,3,5,6,7,8}_*` spójne między Taskami 1/2/5 i FIGURY.md; klucze `\cite` z Task 4 Step 2 = te w konwersji Step 1.
