"""Merges suitability, export-ranking, and local-price signals into one recommendation.

Includes the diversification guardrail: never recommend 100% allocation to
a single crop.
"""

from typing import Callable

_ALLOCATION_BY_COUNT = {1: [70], 2: [60, 40], 3: [50, 30, 20]}
MAX_RECOMMENDATIONS = 3


def compose_recommendation(
    location: str,
    land_size: float,
    viable_crops: list[str],
    export_ranked: list[tuple[str, float | None, float | None]],
    price_lookup: Callable[[str], dict],
) -> dict:
    viable_set = set(viable_crops)
    ranked_viable = [r for r in export_ranked if r[0] in viable_set]

    top = ranked_viable[:MAX_RECOMMENDATIONS]
    allocations = _ALLOCATION_BY_COUNT.get(len(top), [])

    recommendations = []
    for (crop, growth_pct, export_value), allocation_pct in zip(top, allocations):
        recommendations.append(
            {
                "crop": crop,
                "export_growth_pct": growth_pct,
                "export_value_usd_million": export_value,
                "local_price": price_lookup(crop),
                "suggested_allocation_pct": allocation_pct,
            }
        )

    return {
        "location": location,
        "land_size_acres": land_size,
        "recommendations": recommendations,
        "guardrail_note": (
            "Allocate your land across these crops rather than planting one crop exclusively."
        ),
    }
