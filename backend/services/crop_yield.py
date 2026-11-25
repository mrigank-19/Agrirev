"""Typical Indian crop yield, in quintals per acre.

These are published national average yields (approximate, not measured
for any specific field) — used only to turn a price-per-quintal into a
rough revenue estimate. A real field's yield varies a lot with irrigation,
inputs, and management, so treat this as a ballpark, not a forecast.

coconut is excluded — conventionally measured in nuts, not quintals, so a
quintal-based yield figure isn't meaningful for it.
"""

TYPICAL_YIELD_QUINTAL_PER_ACRE = {
    "rice": 10.0,
    "maize": 11.0,
    "chickpea": 4.0,
    "kidneybeans": 5.0,
    "pigeonpeas": 3.0,
    "mothbeans": 2.0,
    "mungbean": 2.5,
    "blackgram": 2.5,
    "lentil": 4.0,
    "pomegranate": 40.0,
    "banana": 150.0,
    "mango": 30.0,
    "grapes": 80.0,
    "watermelon": 100.0,
    "muskmelon": 60.0,
    "apple": 50.0,
    "orange": 40.0,
    "papaya": 200.0,
    "cotton": 6.0,
    "jute": 8.0,
    "coffee": 3.0,
    # Common last-crop answers that aren't suitability-model outputs but
    # still need a yield figure to estimate a baseline revenue.
    "onion": 90.0,
    "wheat": 12.0,
    "sugarcane": 300.0,
    "soybean": 5.0,
    "groundnut": 5.0,
    "tomato": 80.0,
    "potato": 80.0,
    "bajra": 6.0,
    "jowar": 5.0,
    "millet": 5.0,
}


def get_typical_yield(crop: str) -> float | None:
    return TYPICAL_YIELD_QUINTAL_PER_ACRE.get(crop.lower().strip())
