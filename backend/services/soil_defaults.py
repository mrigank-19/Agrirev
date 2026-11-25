"""Static state-level soil/climate defaults for the MVP.

Per the build spec: don't try to cover every district precisely — a
reasonable state/region-level default is enough for a convincing demo.
Values are approximate typical N/P/K (kg/ha ratios), temperature (C),
humidity (%), ph, and rainfall (mm) for each state's major growing regions.
"""

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


def get_soil_inputs(location: str) -> tuple[dict, str | None]:
    """Resolve a free-text location string to soil/climate inputs and a matched state name."""
    normalized = (location or "").lower()
    for state, values in STATE_DEFAULTS.items():
        if state in normalized:
            return dict(values), state
    return dict(NATIONAL_DEFAULT), None
