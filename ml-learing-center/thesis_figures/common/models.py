"""Ładowanie wytrenowanych modeli z ml-service/."""
from pathlib import Path
import joblib

MODELS_DIR = Path(__file__).resolve().parents[3] / "ml-service"


def _require(path: Path):
    if not path.exists():
        raise FileNotFoundError(
            f"Brak pliku modelu: {path}\n"
            f"Uruchom najpierw ml-learing-center/main.py aby wygenerować modele."
        )
    return path


def load_rf():
    return joblib.load(_require(MODELS_DIR / "rf_model.pkl"))


def load_xgb():
    return joblib.load(_require(MODELS_DIR / "xgb_model.pkl"))


def load_lstm():
    from tensorflow.keras.models import load_model
    return load_model(_require(MODELS_DIR / "lstm_model.keras"))


def load_static_scaler():
    return joblib.load(_require(MODELS_DIR / "scaler.pkl"))


def load_lstm_scalers():
    return joblib.load(_require(MODELS_DIR / "lstm_scalers.pkl"))


def load_feature_list():
    return joblib.load(_require(MODELS_DIR / "features.pkl"))
