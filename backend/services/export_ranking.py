"""Ranks a list of crops by their export growth/value from the static export table."""

from pathlib import Path

import pandas as pd

EXPORT_DATA_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "export_rankings.csv"

_export_df = pd.read_csv(EXPORT_DATA_PATH)


def rank_by_export(crop_list: list[str]) -> list[dict]:
    """Return per-crop export signals, best export growth first.

    Each entry: {crop, growth_pct, export_value_usd_million, export_price_inr_per_quintal}.
    Crops with no matching export data get None values and sort last.
    """
    results = []
    for crop in crop_list:
        matches = _export_df[_export_df["matched_crop"] == crop]
        if matches.empty:
            results.append(
                {
                    "crop": crop,
                    "growth_pct": None,
                    "export_value_usd_million": None,
                    "export_price_inr_per_quintal": None,
                }
            )
        else:
            best = matches.sort_values("export_value_usd_million", ascending=False).iloc[0]
            results.append(
                {
                    "crop": crop,
                    "growth_pct": float(best["growth_pct"]),
                    "export_value_usd_million": float(best["export_value_usd_million"]),
                    "export_price_inr_per_quintal": float(best["export_price_inr_per_quintal"]),
                }
            )

    results.sort(key=lambda r: (r["growth_pct"] is None, -(r["growth_pct"] or 0)))
    return results


def get_export_signal(crop: str) -> dict | None:
    """Single-crop lookup, used e.g. for a farmer's last_crop (not from get_viable_crops)."""
    matches = _export_df[_export_df["matched_crop"] == crop.lower().strip()]
    if matches.empty:
        return None
    best = matches.sort_values("export_value_usd_million", ascending=False).iloc[0]
    return {
        "crop": crop,
        "growth_pct": float(best["growth_pct"]),
        "export_value_usd_million": float(best["export_value_usd_million"]),
        "export_price_inr_per_quintal": float(best["export_price_inr_per_quintal"]),
    }
