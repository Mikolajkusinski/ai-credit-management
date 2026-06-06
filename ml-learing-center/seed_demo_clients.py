"""seed_demo_clients.py — pre-seed 3 demo clients for the Seminarium dyplomowe 2 live demo.

Posts 4 snapshots for each of 3 clients to the running backend
(`POST /api/v1/monitoring/clients/{ref}/snapshots`), producing 3 visibly
different trajectory alerts on the Monitoring tab:

    demo-rising-001   INCREASING_RISK   (PAY_* climb, BILL climbs, PAY_AMT drops)
    demo-stable-002   STABLE            (healthy features held steady)
    demo-falling-003  DECREASING_RISK   (starts distressed, recovers)

Usage (with docker-compose backend + Flask up):

    python ml-learing-center/seed_demo_clients.py

Idempotent: a duplicate (clientRef, snapshotDate) returns HTTP 409 from the
backend, which we treat as "already seeded for that date" and skip — so running
this twice is safe.
"""
from __future__ import annotations

import sys
from datetime import date, timedelta
from typing import Any, Iterable

try:
    import requests
except ImportError:
    print("[ERROR] `requests` not installed. Run: pip install requests", file=sys.stderr)
    sys.exit(1)


BACKEND_BASE = "http://localhost:5120/api/v1/monitoring"
FLASK_HEALTH = "http://localhost:5001/health"

TODAY = date.today()


def days_ago(n: int) -> date:
    return TODAY - timedelta(days=n)


def _features(
    demo: dict[str, int],
    pays: list[int],
    bills: list[int],
    pay_amts: list[int],
) -> dict[str, Any]:
    """Build the 22-field `features` block for one snapshot.

    `pays`     = [PAY_0, PAY_2, PAY_3, PAY_4, PAY_5, PAY_6]   newest -> oldest
    `bills`    = [BILL_AMT1, BILL_AMT2, ..., BILL_AMT6]       newest -> oldest
    `pay_amts` = [PAY_AMT1, PAY_AMT2, ..., PAY_AMT6]          newest -> oldest

    UCI quirk: `PAY_1` does not exist — sequence is PAY_0, PAY_2, ..., PAY_6.
    """
    return {
        **demo,
        "pay0": pays[0], "pay2": pays[1], "pay3": pays[2],
        "pay4": pays[3], "pay5": pays[4], "pay6": pays[5],
        "billAmt1": bills[0], "billAmt2": bills[1], "billAmt3": bills[2],
        "billAmt4": bills[3], "billAmt5": bills[4], "billAmt6": bills[5],
        "payAmt1": pay_amts[0], "payAmt2": pay_amts[1], "payAmt3": pay_amts[2],
        "payAmt4": pay_amts[3], "payAmt5": pay_amts[4], "payAmt6": pay_amts[5],
    }


# ---------------------------------------------------------------------------
# Client A: demo-rising-001 -> INCREASING_RISK
# ---------------------------------------------------------------------------
# Demographics held constant across snapshots — trajectory reflects behavior
# change, not identity change. LIMIT_BAL=300k so utilization rises naturally.
RISING_DEMO = {"limitBal": 300000, "sex": 1, "education": 2, "marriage": 2, "age": 35}

RISING_SNAPSHOTS: list[tuple[date, dict[str, Any]]] = [
    # 90 days ago — healthy: on-time payments, ~25% utilization, regular pay-down
    (days_ago(90), _features(
        RISING_DEMO,
        pays=[0, 0, 0, 0, 0, 0],
        bills=[80000, 75000, 70000, 65000, 60000, 55000],
        pay_amts=[8000, 7500, 7000, 6500, 6000, 5500],
    )),
    # 60 days ago — slight stress: 1-month delay appears, balance climbing
    (days_ago(60), _features(
        RISING_DEMO,
        pays=[1, 0, 0, 0, 0, 0],
        bills=[140000, 110000, 90000, 80000, 70000, 60000],
        pay_amts=[4000, 6000, 6500, 6500, 6500, 6000],
    )),
    # 30 days ago — clear stress: delays in 3 of last months, utilization ~70%
    (days_ago(30), _features(
        RISING_DEMO,
        pays=[2, 1, 1, 0, 0, 0],
        bills=[220000, 180000, 140000, 100000, 80000, 60000],
        pay_amts=[1500, 3000, 4500, 5500, 6000, 6000],
    )),
    # Today — severe: 3-month delay, near-limit utilization, near-zero payments
    (TODAY, _features(
        RISING_DEMO,
        pays=[3, 2, 2, 1, 0, 0],
        bills=[285000, 240000, 200000, 150000, 100000, 70000],
        pay_amts=[0, 1500, 2500, 4000, 5500, 6000],
    )),
]


# ---------------------------------------------------------------------------
# Client B: demo-stable-002 -> STABLE
# ---------------------------------------------------------------------------
# Healthy baseline held flat across all 4 snapshots. Tiny rolling wiggle in
# bill/pay amounts so the chart isn't a dead-flat line, but no PAY_* delays.
STABLE_DEMO = {"limitBal": 200000, "sex": 2, "education": 1, "marriage": 1, "age": 42}

STABLE_SNAPSHOTS: list[tuple[date, dict[str, Any]]] = [
    (days_ago(90), _features(
        STABLE_DEMO,
        pays=[0, 0, 0, 0, 0, 0],
        bills=[60000, 58000, 62000, 60000, 55000, 57000],
        pay_amts=[6000, 5800, 6200, 6000, 5500, 5700],
    )),
    (days_ago(60), _features(
        STABLE_DEMO,
        pays=[0, 0, 0, 0, 0, 0],
        bills=[62000, 60000, 58000, 62000, 60000, 55000],
        pay_amts=[6200, 6000, 5800, 6200, 6000, 5500],
    )),
    (days_ago(30), _features(
        STABLE_DEMO,
        pays=[0, 0, 0, 0, 0, 0],
        bills=[59000, 62000, 60000, 58000, 62000, 60000],
        pay_amts=[5900, 6200, 6000, 5800, 6200, 6000],
    )),
    (TODAY, _features(
        STABLE_DEMO,
        pays=[0, 0, 0, 0, 0, 0],
        bills=[61000, 59000, 62000, 60000, 58000, 62000],
        pay_amts=[6100, 5900, 6200, 6000, 5800, 6200],
    )),
]


# ---------------------------------------------------------------------------
# Client C: demo-falling-003 -> DECREASING_RISK
# ---------------------------------------------------------------------------
# Mirror of the rising client: starts distressed, recovers toward healthy.
FALLING_DEMO = {"limitBal": 250000, "sex": 1, "education": 3, "marriage": 2, "age": 29}

FALLING_SNAPSHOTS: list[tuple[date, dict[str, Any]]] = [
    # 90 days ago — distressed
    (days_ago(90), _features(
        FALLING_DEMO,
        pays=[3, 2, 2, 1, 0, 0],
        bills=[230000, 200000, 170000, 130000, 90000, 60000],
        pay_amts=[0, 1500, 2500, 4000, 5500, 5500],
    )),
    # 60 days ago — first cure: PAY_0 still elevated but payment effort returns
    (days_ago(60), _features(
        FALLING_DEMO,
        pays=[2, 2, 1, 1, 0, 0],
        bills=[180000, 200000, 170000, 140000, 100000, 70000],
        pay_amts=[3000, 1500, 3000, 4500, 5500, 5500],
    )),
    # 30 days ago — healing: only mild delays, utilization dropping
    (days_ago(30), _features(
        FALLING_DEMO,
        pays=[1, 1, 1, 0, 0, 0],
        bills=[120000, 150000, 170000, 140000, 100000, 70000],
        pay_amts=[5000, 4500, 4000, 5000, 5500, 5500],
    )),
    # Today — recovered: on-time, utilization ~30%
    (TODAY, _features(
        FALLING_DEMO,
        pays=[0, 0, 0, 0, 0, 0],
        bills=[75000, 95000, 130000, 155000, 130000, 95000],
        pay_amts=[7500, 7000, 5500, 4500, 5000, 5500],
    )),
]


CLIENTS: list[tuple[str, str, list[tuple[date, dict[str, Any]]]]] = [
    ("demo-rising-001",  "INCREASING_RISK", RISING_SNAPSHOTS),
    ("demo-stable-002",  "STABLE",          STABLE_SNAPSHOTS),
    ("demo-falling-003", "DECREASING_RISK", FALLING_SNAPSHOTS),
]


# ---------------------------------------------------------------------------
# HTTP driver
# ---------------------------------------------------------------------------

def check_health() -> None:
    """Abort early if Flask or the backend isn't reachable."""
    try:
        r = requests.get(FLASK_HEALTH, timeout=3)
        if r.status_code != 200:
            print(f"[ERROR] Flask /health returned HTTP {r.status_code}", file=sys.stderr)
            sys.exit(1)
        status = r.json().get("status", "unknown")
        print(f"[ok] Flask ML service ({FLASK_HEALTH}): {status}")
    except requests.RequestException as exc:
        print(f"[ERROR] Flask unreachable at {FLASK_HEALTH}: {exc}", file=sys.stderr)
        print("       Start it: cd ml-service && python app.py", file=sys.stderr)
        sys.exit(1)

    try:
        r = requests.get(f"{BACKEND_BASE}/clients", timeout=3)
        if r.status_code != 200:
            print(f"[ERROR] Backend /clients returned HTTP {r.status_code}", file=sys.stderr)
            sys.exit(1)
        existing = len(r.json().get("clients", []))
        print(f"[ok] Backend API ({BACKEND_BASE}): {existing} clients already in DB")
    except requests.RequestException as exc:
        print(f"[ERROR] Backend unreachable at {BACKEND_BASE}: {exc}", file=sys.stderr)
        print("       Start it: docker-compose up -d db backend", file=sys.stderr)
        sys.exit(1)


def post_snapshot(client_ref: str, snap_date: date, features: dict[str, Any]) -> dict | None:
    """POST one snapshot. Returns response JSON, or None on 409 / error."""
    url = f"{BACKEND_BASE}/clients/{client_ref}/snapshots"
    body = {"snapshotDate": snap_date.isoformat(), "features": features}
    try:
        r = requests.post(url, json=body, timeout=20)
    except requests.RequestException as exc:
        print(f"    [ERROR] POST failed for {snap_date.isoformat()}: {exc}", file=sys.stderr)
        return None

    if r.status_code == 201:
        return r.json()
    if r.status_code == 409:
        print(f"    [skip] {snap_date.isoformat()}: already seeded (HTTP 409)")
        return None
    print(
        f"    [ERROR] POST {snap_date.isoformat()} -> HTTP {r.status_code}: {r.text[:200]}",
        file=sys.stderr,
    )
    return None


def summarize_history(client_ref: str, expected_alert: str) -> None:
    """Fetch /history and print per-model slope so we can see if intent matched."""
    url = f"{BACKEND_BASE}/clients/{client_ref}/history"
    try:
        r = requests.get(url, timeout=10)
    except requests.RequestException as exc:
        print(f"    [warn] cannot fetch history: {exc}")
        return
    if r.status_code != 200:
        print(f"    [warn] /history returned HTTP {r.status_code}")
        return
    trends = r.json().get("trends", {}) or {}
    if not trends:
        print("    [warn] no trends in history response (need >=2 snapshots)")
        return
    print(f"    expected alert: {expected_alert}")
    for model in sorted(trends):
        info = trends[model] or {}
        slope = info.get("slope")
        alert = info.get("alert")
        marker = "OK" if alert == expected_alert else "  "
        slope_str = f"{slope:+.3f}" if isinstance(slope, (int, float)) else str(slope)
        print(f"    [{marker}] {model:15s} slope={slope_str} alert={alert}")


def seed_client(
    client_ref: str,
    expected_alert: str,
    snapshots: Iterable[tuple[date, dict[str, Any]]],
) -> None:
    print(f"[client] {client_ref}  (target alert: {expected_alert})")
    created = 0
    skipped = 0
    for snap_date, features in snapshots:
        result = post_snapshot(client_ref, snap_date, features)
        if result is None:
            skipped += 1
            continue
        created += 1
        snap_id = result.get("snapshotId", "?")
        client_created = (result.get("persisted") or {}).get("clientCreated", False)
        tag = " +new client" if client_created else ""
        print(f"    [add ] {snap_date.isoformat()} -> snapshotId={snap_id}{tag}")
    print(f"    summary: {created} created, {skipped} skipped")
    summarize_history(client_ref, expected_alert)
    print()


def main() -> None:
    bar = "=" * 72
    print(bar)
    print("seed_demo_clients.py -- pre-seed Monitoring tab for Seminarium 2 live demo")
    print(bar)
    check_health()
    print()
    for client_ref, expected_alert, snapshots in CLIENTS:
        seed_client(client_ref, expected_alert, snapshots)
    print(bar)
    print("Done. Open http://localhost:5173 -> Monitoring tab to verify trajectories.")
    print(bar)


if __name__ == "__main__":
    main()
