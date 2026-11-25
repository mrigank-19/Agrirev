"""Rough revenue projection: allocated land * typical yield * known price.

Only computed when both a price (FPO-reported or Agmarknet) and a typical
yield figure are available for the crop — otherwise returns None rather
than guessing, consistent with the rest of the app's "never fabricate a
number you don't have a basis for" approach.
"""

from typing import Callable

from backend.services.crop_yield import get_typical_yield


def estimate_revenue(crop: str, allocated_acres: float, price_per_quintal: float | None) -> float | None:
    if price_per_quintal is None:
        return None
    yield_per_acre = get_typical_yield(crop)
    if yield_per_acre is None:
        return None
    return allocated_acres * yield_per_acre * price_per_quintal


def estimate_baseline_revenue(last_crop: str | None, land_size: float, price_lookup: Callable[[str], dict]) -> float | None:
    """What the farmer's full land would have earned sticking with last_crop, if estimable."""
    if not last_crop:
        return None
    price = price_lookup(last_crop)
    if not price.get("available"):
        return None
    return estimate_revenue(last_crop, land_size, price["modal_price_per_quintal"])
