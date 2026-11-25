"""Merges suitability, export-ranking, and local-price signals into one recommendation.

Includes the diversification guardrail (never recommend 100% allocation to a
single crop), a plain-language "why" explanation per crop, and a local-buyer
reality check flag for crops with strong export growth but no confirmed
local market access.
"""

from typing import Callable

from backend.services.revenue_estimator import estimate_baseline_revenue, estimate_revenue

_ALLOCATION_BY_COUNT = {1: [70], 2: [60, 40], 3: [50, 30, 20]}
MAX_RECOMMENDATIONS = 3

DATA_COVERAGE_NOTE = (
    "We didn't have exact soil data for your district, so this uses a general "
    "regional estimate — treat it as a starting point, not a precise reading."
)


def compose_recommendation(
    location: str,
    land_size: float,
    viable_crops: list[str],
    export_ranked: list[tuple[str, float | None, float | None]],
    price_lookup: Callable[[str], dict],
    soil_explainer: Callable[[str], str],
    state_matched: bool,
    rotation_note: str | None = None,
    weather_is_live: bool = False,
    last_crop: str | None = None,
) -> dict:
    viable_set = set(viable_crops)
    ranked_viable = [r for r in export_ranked if r[0] in viable_set]

    top = ranked_viable[:MAX_RECOMMENDATIONS]
    allocations = _ALLOCATION_BY_COUNT.get(len(top), [])

    recommendations = []
    total_projected_revenue = 0.0
    any_revenue_missing = False

    for (crop, growth_pct, export_value), allocation_pct in zip(top, allocations):
        price = price_lookup(crop)
        allocated_acres = land_size * allocation_pct / 100

        projected_revenue = estimate_revenue(
            crop, allocated_acres, price.get("modal_price_per_quintal") if price.get("available") else None
        )
        if projected_revenue is None:
            any_revenue_missing = True
        else:
            total_projected_revenue += projected_revenue

        soil_factor = soil_explainer(crop)
        if growth_pct is not None:
            export_reason = f"export demand grew {growth_pct:+.1f}% last year"
        else:
            export_reason = "no recent export-growth data available for this crop"
        why = f"Favorable {soil_factor} for your area; {export_reason}."

        local_market_flag = bool(growth_pct is not None and growth_pct > 0 and not price.get("available"))

        recommendations.append(
            {
                "crop": crop,
                "export_growth_pct": growth_pct,
                "export_value_usd_million": export_value,
                "local_price": price,
                "suggested_allocation_pct": allocation_pct,
                "allocated_acres": round(allocated_acres, 2),
                "projected_revenue_inr": round(projected_revenue, 0) if projected_revenue is not None else None,
                "why": why,
                "local_market_flag": local_market_flag,
                "local_market_note": (
                    "Strong export demand, but we couldn't confirm local mandi/FPO access — "
                    "check with your local APMC or FPO before committing a large share of land."
                    if local_market_flag
                    else None
                ),
            }
        )

    baseline_revenue = estimate_baseline_revenue(last_crop, land_size, price_lookup)
    revenue_comparison = None
    if baseline_revenue and total_projected_revenue > 0:
        revenue_comparison = {
            "baseline_crop": last_crop,
            "baseline_revenue_inr": round(baseline_revenue, 0),
            "projected_total_revenue_inr": round(total_projected_revenue, 0),
            "partial": any_revenue_missing,
            # Only a fair comparison when every recommended crop's revenue is known —
            # otherwise the total understates what full diversified land use would earn.
            "revenue_increase_pct": (
                None if any_revenue_missing
                else round((total_projected_revenue - baseline_revenue) / baseline_revenue * 100, 1)
            ),
        }

    return {
        "location": location,
        "land_size_acres": land_size,
        "recommendations": recommendations,
        "guardrail_note": (
            "Allocate your land across these crops rather than planting one crop exclusively."
        ),
        "data_coverage_note": None if state_matched else DATA_COVERAGE_NOTE,
        "rotation_note": rotation_note,
        "weather_source": "live" if weather_is_live else "seasonal average",
        "revenue_comparison": revenue_comparison,
    }
