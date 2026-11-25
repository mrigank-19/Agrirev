"""Shared recommendation logic used by both the plain REST endpoint and the WhatsApp webhook."""

from backend.services import composer, export_ranking, price_check, suitability
from backend.services.soil_defaults import get_soil_inputs


def build_recommendation(location: str, land_size: float, last_crop: str | None = None) -> dict:
    soil_inputs, state = get_soil_inputs(location)
    viable_crops = suitability.get_viable_crops(soil_inputs)
    ranked = export_ranking.rank_by_export(viable_crops)

    return composer.compose_recommendation(
        location=location,
        land_size=land_size,
        viable_crops=viable_crops,
        export_ranked=ranked,
        price_lookup=lambda crop: price_check.get_local_price(crop, state),
    )
