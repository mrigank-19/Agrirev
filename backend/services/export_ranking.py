"""Ranks a list of crops by their export growth/value from the static export table."""

from pathlib import Path

import pandas as pd

EXPORT_DATA_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "export_rankings.csv"

_export_df = pd.read_csv(EXPORT_DATA_PATH)


def rank_by_export(crop_list: list[str]) -> list[tuple[str, float | None, float | None]]:
    """Return (crop, growth_pct, export_value_usd_million) tuples, best export growth first.

    Crops with no matching export data get None values and sort last.
    """
    results = []
    for crop in crop_list:
        matches = _export_df[_export_df["matched_crop"] == crop]
        if matches.empty:
            results.append((crop, None, None))
        else:
            best = matches.sort_values("export_value_usd_million", ascending=False).iloc[0]
            results.append((crop, float(best["growth_pct"]), float(best["export_value_usd_million"])))

    results.sort(key=lambda r: (r[1] is None, -(r[1] or 0)))
    return results
