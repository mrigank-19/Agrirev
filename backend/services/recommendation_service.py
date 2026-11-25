"""Shared recommendation logic used by both the plain REST endpoint and the WhatsApp webhook."""

from backend.services import composer, crop_rotation, export_ranking, price_check, suitability, weather
from backend.services.soil_defaults import get_soil_inputs


def build_recommendation(location: str, land_size: float, last_crop: str | None = None) -> dict:
    soil_inputs, state = get_soil_inputs(location)

    soil_inputs, rotation_note = crop_rotation.apply_rotation_effect(soil_inputs, last_crop)

    live_weather = weather.get_live_weather(location)
    if live_weather:
        soil_inputs["temperature"] = live_weather["temperature"]
        soil_inputs["humidity"] = live_weather["humidity"]

    viable_crops = suitability.get_viable_crops(soil_inputs)
    ranked = export_ranking.rank_by_export(viable_crops)

    return composer.compose_recommendation(
        location=location,
        land_size=land_size,
        viable_crops=viable_crops,
        export_ranked=ranked,
        price_lookup=lambda crop: price_check.get_local_price(crop, state),
        soil_explainer=lambda crop: suitability.explain_viability(crop, soil_inputs),
        state_matched=state is not None,
        rotation_note=rotation_note,
        weather_is_live=live_weather is not None,
    )
