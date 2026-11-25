"""Local mandi price lookup: checks FPO-reported manual prices first, then
the Agmarknet dataset on data.gov.in.

Agmarknet requires a free self-registered data.gov.in API key
(AGMARKNET_API_KEY env var) and has incomplete coverage; manual entries
from backend/services/manual_price_store.py take priority since they're
more likely to be current for a given FPO's own mandi. Per the build spec:
never let a slow/unavailable price API fail the whole response — fall
back to "not available" instead.
"""

import os

import requests

from backend.services.manual_price_store import get_manual_price

AGMARKNET_RESOURCE_ID = "9ef84268-d588-465a-a308-a864a43d0070"
AGMARKNET_URL = f"https://api.data.gov.in/resource/{AGMARKNET_RESOURCE_ID}"
REQUEST_TIMEOUT_SECONDS = 5

_cache: dict[tuple[str, str], dict] = {}


def get_local_price(crop: str, state: str | None) -> dict:
    """Return the latest modal mandi price for a crop in a state, or an unavailable marker."""
    manual = get_manual_price(crop, state)
    if manual:
        return manual

    cache_key = (crop.lower(), (state or "").lower())
    if cache_key in _cache:
        return _cache[cache_key]

    api_key = os.environ.get("AGMARKNET_API_KEY")
    if not api_key or not state:
        result = {"available": False, "reason": "no API key configured" if not api_key else "state unknown"}
        _cache[cache_key] = result
        return result

    try:
        response = requests.get(
            AGMARKNET_URL,
            params={
                "api-key": api_key,
                "format": "json",
                "filters[commodity]": crop,
                "filters[state]": state,
                "limit": 1,
            },
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        records = response.json().get("records", [])
        if not records:
            result = {"available": False, "reason": "no mandi records found"}
        else:
            record = records[0]
            result = {
                "available": True,
                "modal_price_per_quintal": record.get("modal_price"),
                "market": record.get("market"),
                "arrival_date": record.get("arrival_date"),
            }
    except requests.RequestException:
        result = {"available": False, "reason": "price service unavailable"}

    _cache[cache_key] = result
    return result
