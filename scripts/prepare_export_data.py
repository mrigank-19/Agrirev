"""Clean the raw APEDA export statement into a ranked, crop-matched export table.

Source: APEDA AgriXchange "APEDA Products Export Statement (3 years)" report
(data/apeda_export_raw.csv), figures sourced from DGCIS, FY2023-24 to FY2025-26.

Growth is year-over-year, latest two years (FY2024-25 -> FY2025-26).
Commodity names are normalized to match the suitability model's crop labels
where a direct match exists; APEDA's product groupings don't cover every
crop in the suitability dataset (e.g. pulses are reported as one aggregate
line, not split into lentil/chickpea/kidneybeans/etc.), so many rows are
kept with no matched_crop for reference but excluded from crop-level ranking.
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW_PATH = ROOT / "data" / "apeda_export_raw.csv"
OUT_PATH = ROOT / "data" / "export_rankings.csv"

# Approximate, indicative rate -- not a live FX feed. Only used to turn the
# export value/quantity figures into a rupees-per-quintal estimate.
USD_TO_INR = 83.5
MT_TO_QUINTAL = 10

# Maps raw APEDA product names to the suitability model's crop labels.
# Only mapped where the product is clearly the same crop (not just related).
CROP_NAME_MAP = {
    "NON BASMATI RICE": "rice",
    "BASMATI RICE": "rice",
    "MAIZE": "maize",
    "FRESH GRAPES": "grapes",
    "FRESH MANGOES": "mango",
    "MANGO PULP": "mango",
}


def main():
    df = pd.read_csv(RAW_PATH)

    df["growth_pct"] = (
        (df["value_usd_million_2025_26"] - df["value_usd_million_2024_25"])
        / df["value_usd_million_2024_25"]
        * 100
    ).round(2)

    df["matched_crop"] = df["product"].map(CROP_NAME_MAP)

    # Implied export-market price: export value / export quantity, converted
    # to INR per quintal. This is what export markets are effectively paying
    # per unit, distinct from (and often higher than) the local mandi price.
    df["export_price_inr_per_quintal"] = (
        df["value_usd_million_2025_26"] * 1_000_000 * USD_TO_INR
        / (df["qty_mt_2025_26"] * MT_TO_QUINTAL)
    ).round(2)

    df = df.rename(columns={"value_usd_million_2025_26": "export_value_usd_million"})
    df = df[
        [
            "product_group",
            "product",
            "matched_crop",
            "export_value_usd_million",
            "export_price_inr_per_quintal",
            "growth_pct",
        ]
    ]
    df = df.sort_values("export_value_usd_million", ascending=False).reset_index(drop=True)

    df.to_csv(OUT_PATH, index=False)
    print(f"Wrote {len(df)} rows to {OUT_PATH}")
    print(f"Rows matched to a suitability-model crop: {df['matched_crop'].notna().sum()}")


if __name__ == "__main__":
    main()
