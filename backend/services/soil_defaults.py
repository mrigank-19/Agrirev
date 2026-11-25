"""Soil/climate defaults for the MVP, layered at two levels of precision.

Rainfall: real, per-district annual normals (data/district_rainfall.csv),
from the Ministry of Earth Sciences' "District Rainfall Normal (mm),
Monthly/Seasonal/Annual, 1951-2000" dataset on data.gov.in — genuine
government data covering 640 districts, not a guess. The suitability
model's "rainfall" feature is on a monthly scale (the Kaggle training data
ranges ~20-300mm), so annual totals are divided by 12 to match.

A handful of district names (4, e.g. "Aurangabad") exist in more than one
state; when the input text also names the state, that's used to disambiguate,
otherwise the first match wins arbitrarily.

N/P/K, temperature, humidity, ph: still state-level approximations, not
per-district. Real per-district soil nutrient and temperature data wasn't
available within the project's timeframe — this is a known simplification,
consistent with the build spec's guidance that a region-level default is
enough for an MVP demo. Don't read these as precise per-district figures.
"""

import csv
from collections import defaultdict
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

# district_lower -> list of (state_lower, monthly-scale rainfall), usually one entry
_DISTRICT_RAINFALL: dict[str, list[tuple[str, float]]] = defaultdict(list)
with open(DISTRICT_RAINFALL_PATH, encoding="utf-8") as f:
    for row in csv.DictReader(f):
        state_key = row["state_name"].strip().lower()
        district_key = row["district_name"].strip().lower()
        monthly_rainfall = float(row["annual_rainfall_mm"]) / 12
        _DISTRICT_RAINFALL[district_key].append((state_key, monthly_rainfall))


def get_soil_inputs(location: str) -> tuple[dict, str | None]:
    """Resolve a free-text location string to soil/climate inputs and a matched state name.

    Checks for a known district name first (real rainfall data layered on
    the district's state profile for the other factors), then falls back to
    a state-only match, then the national default.
    """
    normalized = (location or "").lower()

    for district_key, candidates in _DISTRICT_RAINFALL.items():
        if district_key not in normalized:
            continue

        state_key, monthly_rainfall = candidates[0]
        if len(candidates) > 1:
            for candidate_state, candidate_rainfall in candidates:
                if candidate_state in normalized:
                    state_key, monthly_rainfall = candidate_state, candidate_rainfall
                    break

        base = dict(STATE_DEFAULTS.get(state_key, NATIONAL_DEFAULT))
        base["rainfall"] = round(monthly_rainfall, 1)
        return base, state_key

    for state, values in STATE_DEFAULTS.items():
        if state in normalized:
            return dict(values), state

    return dict(NATIONAL_DEFAULT), None
