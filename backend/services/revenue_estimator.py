"""Rough revenue projection: allocated land * typical yield * known price.

Only computed when both a price and a typical yield figure are available
for the crop — otherwise returns None rather than guessing, consistent
with the rest of the app's "never fabricate a number you don't have a
basis for" approach. Callers decide which price to use (export-market
price is preferred when available, since this product's whole premise is
export demand; local mandi price is the fallback).
"""

from backend.services.crop_yield import get_typical_yield


def estimate_revenue(crop: str, allocated_acres: float, price_per_quintal: float | None) -> float | None:
    if price_per_quintal is None:
        return None
    yield_per_acre = get_typical_yield(crop)
    if yield_per_acre is None:
        return None
    return allocated_acres * yield_per_acre * price_per_quintal
