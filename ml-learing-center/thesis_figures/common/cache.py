"""Cache wyników kosztownych obliczeń (retrening, grid search, SHAP)."""
from pathlib import Path
import json
import pickle
import os

CACHE_DIR = Path(__file__).resolve().parents[1] / "cache"
CACHE_DIR.mkdir(exist_ok=True)

FORCE_REFRESH = os.environ.get("THESIS_NO_CACHE", "0") == "1"


def cached_json(name: str):
    """Dekorator: @cached_json('lstm_history') — zapisuje return jako JSON."""
    path = CACHE_DIR / f"{name}.json"

    def decorator(fn):
        def wrapper(*args, **kwargs):
            if path.exists() and not FORCE_REFRESH:
                with path.open("r") as f:
                    return json.load(f)
            result = fn(*args, **kwargs)
            with path.open("w") as f:
                json.dump(result, f, indent=2, default=str)
            return result
        return wrapper
    return decorator


def cached_pickle(name: str):
    path = CACHE_DIR / f"{name}.pkl"

    def decorator(fn):
        def wrapper(*args, **kwargs):
            if path.exists() and not FORCE_REFRESH:
                with path.open("rb") as f:
                    return pickle.load(f)
            result = fn(*args, **kwargs)
            with path.open("wb") as f:
                pickle.dump(result, f)
            return result
        return wrapper
    return decorator
