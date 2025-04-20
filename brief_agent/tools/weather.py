import os
import requests
from datetime import date
from brief_agent.schema import Weather

def get_weather(iso_date: str) -> Weather:
    """
    Fetch weather forecast for the given ISO date using WeatherAPI.com.
    Requires WEATHER_API_KEY and optional LOCATION in .env (default: Melbourne).
    """
    # Validate date
    _ = date.fromisoformat(iso_date)

    api_key = os.getenv("WEATHER_API_KEY")
    if not api_key:
        raise RuntimeError("WEATHER_API_KEY not set in environment")

    # Location can be city name or "lat,lon" string
    location = os.getenv("LOCATION", "Melbourne")
    params = {
        "key": api_key,
        "q": location,
        "days": 1,
        "aqi": "no",
        "alerts": "no"
    }
    resp = requests.get("http://api.weatherapi.com/v1/forecast.json", params=params)
    resp.raise_for_status()
    data = resp.json()
    day = data.get("forecast", {}).get("forecastday", [])[0].get("day", {})
    return Weather(
        min_c=day.get("mintemp_c", 0.0),
        max_c=day.get("maxtemp_c", 0.0),
        rain_chance_pct=day.get("daily_chance_of_rain", 0)
    )