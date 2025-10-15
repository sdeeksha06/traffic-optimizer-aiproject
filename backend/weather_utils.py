import os
import random
import requests
from typing import Dict, Tuple

try:
    # Optional: load from .env if python-dotenv is installed
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass


OWM_URL = "https://api.openweathermap.org/data/2.5/weather"


def _category_to_delay_and_risk(category: str) -> Tuple[int, float]:
    c = category or ""
    c = c.strip().title()

    if c in {"Extreme", "Squall", "Tornado"}:
        return random.randint(25, 30), round(random.uniform(1.15, 1.30), 2)
    if c in {"Thunderstorm", "Rain"}:
        return random.randint(10, 20), round(random.uniform(1.08, 1.12), 2)
    if c in {"Drizzle", "Mist", "Fog", "Haze", "Smoke"}:
        return random.randint(5, 10), round(random.uniform(1.03, 1.06), 2)
    if c in {"Snow"}:
        return random.randint(10, 20), round(random.uniform(1.07, 1.12), 2)
    # Default fair weather
    return random.randint(0, 3), round(random.uniform(1.00, 1.02), 2)


def get_weather_delay(city_name: str, lat: float, lon: float) -> Dict[str, object]:
    """
    Fetch current weather for the given coordinates and return delay and risk.

    Returns:
        {
            "condition": str,
            "delay_min": int,
            "risk": float,
        }
    """
    api_key = os.getenv("WEATHER_API_KEY", "").strip()

    # If no API key, fall back to a mocked response for testing
    if not api_key:
        # Randomly choose a plausible condition for variability
        possible = ["Clear", "Clouds", "Rain", "Drizzle", "Thunderstorm", "Mist", "Fog"]
        condition = random.choice(possible)
        delay, risk = _category_to_delay_and_risk(condition)
        return {"condition": condition, "delay_min": delay, "risk": risk}

    params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key,
        # Units don't affect 'weather[0].main' category; keeping default.
    }

    try:
        resp = requests.get(OWM_URL, params=params, timeout=8)
        resp.raise_for_status()
        data = resp.json()
        # OpenWeatherMap returns an array, take the first weather condition
        condition = ""
        if isinstance(data, dict):
            weather_list = data.get("weather")
            if isinstance(weather_list, list) and weather_list:
                main = weather_list[0].get("main")
                if isinstance(main, str):
                    condition = main
        delay, risk = _category_to_delay_and_risk(condition)
        return {"condition": condition or "Clear", "delay_min": delay, "risk": risk}
    except Exception:
        # Network/API failure fallback: conservative mild delay
        delay, risk = _category_to_delay_and_risk("Clouds")
        return {"condition": "Unknown", "delay_min": delay, "risk": risk}
