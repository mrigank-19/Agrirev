"""Live temperature/humidity via OpenWeatherMap's free tier.

Requires a free self-registered API key (OPENWEATHERMAP_API_KEY env var).
Without one, or if the lookup fails, callers should fall back to the
static seasonal averages in soil_defaults.py — never let a weather API
hiccup break the whole recommendation.
"""

import os

import requests

OPENWEATHERMAP_URL = "https://api.openweathermap.org/data/2.5/weather"
REQUEST_TIMEOUT_SECONDS = 5

_cache: dict[str, dict | None] = {}


def get_live_weather(location: str) -> dict | None:
    """Return {"temperature": C, "humidity": %} for a location, or None if unavailable."""
    cache_key = location.lower().strip()
    if cache_key in _cache:
        return _cache[cache_key]

    api_key = os.environ.get("OPENWEATHERMAP_API_KEY")
    if not api_key:
        _cache[cache_key] = None
        return None

    city = location.split(",")[0].strip()
    try:
        response = requests.get(
            OPENWEATHERMAP_URL,
            params={"q": f"{city},IN", "appid": api_key, "units": "metric"},
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        data = response.json()
        result = {
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
        }
    except (requests.RequestException, KeyError):
        result = None

    _cache[cache_key] = result
    return result
