"""Models what a previously-grown crop leaves behind in the soil.

Rather than just excluding the last crop from recommendations, this adjusts
the soil's N/P/K based on well-established agronomic effects of crop
categories: nitrogen-fixing legumes replenish soil nitrogen (via rhizobia),
while heavy-feeding cereals and cash crops deplete it. The adjusted soil
state is what actually gets fed into the suitability model, so a farmer
coming off a legume crop may see different viable crops than one coming
off rice or cotton, even on identical land.

This is a category-level approximation, not measured field soil data.
"""

LEGUME_CROPS = {"blackgram", "chickpea", "kidneybeans", "lentil", "mothbeans", "mungbean", "pigeonpeas"}
HEAVY_FEEDER_CROPS = {"rice", "maize", "cotton", "jute", "banana"}
MELON_VINE_CROPS = {"watermelon", "muskmelon"}
PERENNIAL_FRUIT_CROPS = {"apple", "mango", "orange", "papaya", "pomegranate", "coconut", "grapes", "coffee"}

# Adjustment applied to the field's N/P/K after harvesting a crop in that category.
CATEGORY_EFFECTS = {
    "legume": {"N": 20, "P": -5, "K": -5},
    "heavy_feeder": {"N": -25, "P": -10, "K": -15},
    "melon_vine": {"N": -15, "P": -8, "K": -10},
    "perennial_fruit": {"N": -10, "P": -8, "K": -15},
}

CATEGORY_NOTES = {
    "legume": "your previous legume crop naturally replenished soil nitrogen",
    "heavy_feeder": "your previous crop was a heavy feeder and likely depleted soil nitrogen and potassium",
    "melon_vine": "your previous crop drew moderately on soil nitrogen and potassium",
    "perennial_fruit": "your previous fruit crop drew on soil nitrogen and potassium over its growing cycle",
}

# N: 0-140, P: 5-145, K: 5-205 — matches the suitability model's training data range.
_BOUNDS = {"N": (0, 140), "P": (5, 145), "K": (5, 205)}


def _categorize(crop: str) -> str | None:
    crop = crop.lower().strip()
    if crop in LEGUME_CROPS:
        return "legume"
    if crop in HEAVY_FEEDER_CROPS:
        return "heavy_feeder"
    if crop in MELON_VINE_CROPS:
        return "melon_vine"
    if crop in PERENNIAL_FRUIT_CROPS:
        return "perennial_fruit"
    return None


def apply_rotation_effect(soil_inputs: dict, last_crop: str | None) -> tuple[dict, str | None]:
    """Return (adjusted soil inputs, explanation note or None) based on the last crop grown."""
    if not last_crop:
        return dict(soil_inputs), None

    category = _categorize(last_crop)
    if category is None:
        return dict(soil_inputs), None

    adjusted = dict(soil_inputs)
    for nutrient, delta in CATEGORY_EFFECTS[category].items():
        low, high = _BOUNDS[nutrient]
        adjusted[nutrient] = min(high, max(low, adjusted[nutrient] + delta))

    return adjusted, CATEGORY_NOTES[category]
