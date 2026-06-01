"""Smoke test for ml-service test infrastructure.

Intentionally does NOT import ``app`` — ``app.py`` loads model artifacts
(``.pkl``/``.keras``) at import time, and those files are not stored in
git nor available in CI. Verifying that the core scientific stack is
importable is enough to prove the pytest runner works.
"""


def test_core_dependencies_importable():
    import flask
    import numpy
    import pandas

    assert flask.__name__ == "flask"
    assert numpy.__name__ == "numpy"
    assert pandas.__name__ == "pandas"
