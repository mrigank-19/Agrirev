"""Local mandi prices manually entered by FPOs/CSCs, checked before Agmarknet.

Agmarknet coverage is incomplete and requires a registered API key, so this
gives local FPOs a direct way to report the price they're actually seeing
at their own mandi — which is more current and more trustworthy than a
government API lag for many smaller markets anyway.

Stored as flat JSON; fine for an MVP's data volume, not meant for concurrent
writers at scale.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock

STORE_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "manual_mandi_prices.json"
_lock = Lock()


def _load() -> list[dict]:
    if not STORE_PATH.exists():
        return []
    with open(STORE_PATH, encoding="utf-8") as f:
        return json.load(f)


def _save(records: list[dict]) -> None:
    STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(STORE_PATH, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)


def list_prices() -> list[dict]:
    """Most recently updated first."""
    return sorted(_load(), key=lambda r: r["updated_at"], reverse=True)


def add_price(crop: str, state: str, district: str, market: str, price_per_quintal: float, reported_by: str) -> None:
    record = {
        "crop": crop.strip().lower(),
        "state": state.strip().lower(),
        "district": district.strip(),
        "market": market.strip(),
        "price_per_quintal": price_per_quintal,
        "reported_by": reported_by.strip(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    with _lock:
        records = _load()
        records.append(record)
        _save(records)


def get_manual_price(crop: str, state: str | None) -> dict | None:
    """Most recent manual entry for this crop/state, if any."""
    crop_key = crop.strip().lower()
    state_key = (state or "").strip().lower()

    matches = [r for r in _load() if r["crop"] == crop_key and r["state"] == state_key]
    if not matches:
        return None

    latest = max(matches, key=lambda r: r["updated_at"])
    return {
        "available": True,
        "modal_price_per_quintal": latest["price_per_quintal"],
        "market": latest["market"],
        "source": "fpo_reported",
        "reported_by": latest["reported_by"],
        "updated_at": latest["updated_at"],
    }
