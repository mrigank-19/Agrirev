"""Soil/climate defaults for the MVP, layered at two levels of precision.

Rainfall: real, per-district averages computed from IMD-sourced daily/monthly
station records (data/district_rainfall.csv, ~1969-2020, via
indiadataportal.com's open CKAN API) — genuine government data, not a guess.
The suitability model's "rainfall" feature is on a monthly scale (the
Kaggle training data ranges ~20-300mm), so district annual totals are
divided by 12 to match.

N/P/K, temperature, humidity, ph: still state-level approximations, not
per-district. Real per-district soil nutrient and temperature data wasn't
available within the project's timeframe — this is a known simplification,
consistent with the build spec's guidance that a region-level default is
enough for an MVP demo. Don't read these as precise per-district figures.
"""

import csv
from pathlib import Path

NATIONAL_DEFAULT = {
    "N": 70, "P": 50, "K": 45,
    "temperature": 26.0, "humidity": 65.0, "ph": 6.5, "rainfall": 110.0,
}

STATE_DEFAULTS = {
    "punjab": {"N": 90, "P": 55, "K": 40, "temperature": 24.0, "humidity": 60.0, "ph": 7.0, "rainfall": 70.0},
    "maharashtra": {"N": 70, "P": 45, "K": 45, "temperature": 27.0, "humidity": 60.0, "ph": 6.8, "rainfall": 100.0},
    "karnataka": {"N": 75, "P": 50, "K": 50, "temperature": 26.0, "humidity": 65.0, "ph": 6.5, "rainfall": 120.0},
    "west bengal": {"N": 80, "P": 45, "K": 40, "temperature": 26.5, "humidity": 85.0, "ph": 6.2, "rainfall": 180.0},
    "uttar pradesh": {"N": 85, "P": 50, "K": 35, "temperature": 25.5, "humidity": 65.0, "ph": 7.0, "rainfall": 95.0},
    "tamil nadu": {"N": 65, "P": 55, "K": 55, "temperature": 28.0, "humidity": 75.0, "ph": 6.6, "rainfall": 130.0},
    "gujarat": {"N": 60, "P": 40, "K": 40, "temperature": 28.5, "humidity": 55.0, "ph": 7.3, "rainfall": 75.0},
    "madhya pradesh": {"N": 70, "P": 45, "K": 40, "temperature": 26.0, "humidity": 60.0, "ph": 6.9, "rainfall": 100.0},
    "andhra pradesh": {"N": 70, "P": 50, "K": 50, "temperature": 29.0, "humidity": 70.0, "ph": 6.7, "rainfall": 110.0},
    "telangana": {"N": 70, "P": 50, "K": 50, "temperature": 29.0, "humidity": 68.0, "ph": 6.7, "rainfall": 105.0},
    "bihar": {"N": 80, "P": 45, "K": 35, "temperature": 26.0, "humidity": 75.0, "ph": 6.8, "rainfall": 130.0},
    "rajasthan": {"N": 45, "P": 35, "K": 30, "temperature": 29.0, "humidity": 40.0, "ph": 7.5, "rainfall": 45.0},
}

DISTRICT_RAINFALL_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "district_rainfall.csv"

# (state_lower, district_lower) -> monthly-scale rainfall (annual_mm / 12)
_DISTRICT_RAINFALL: dict[tuple[str, str], float] = {}
with open(DISTRICT_RAINFALL_PATH, encoding="utf-8") as f:
    for row in csv.DictReader(f):
        state_key = row["state_name"].strip().lower()
        district_key = row["district_name"].strip().lower()
        _DISTRICT_RAINFALL[(state_key, district_key)] = float(row["annual_rainfall_mm"]) / 12


def get_soil_inputs(location: str) -> tuple[dict, str | None]:
    """Resolve a free-text location string to soil/climate inputs and a matched state name.

    Checks for a known district name first (real rainfall data layered on
    the district's state profile for the other factors), then falls back to
    a state-only match, then the national default.
    """
    normalized = (location or "").lower()

    for (state_key, district_key), monthly_rainfall in _DISTRICT_RAINFALL.items():
        if district_key in normalized:
            base = dict(STATE_DEFAULTS.get(state_key, NATIONAL_DEFAULT))
            base["rainfall"] = round(monthly_rainfall, 1)
            return base, state_key

    for state, values in STATE_DEFAULTS.items():
        if state in normalized:
            return dict(values), state

    return dict(NATIONAL_DEFAULT), None
