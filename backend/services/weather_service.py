import requests
from flask import current_app
from utils.errors import UpstreamServiceError

WEATHER_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Depositing rime fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
    80: "Rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
    95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Severe thunderstorm",
}


def get_weather(lat, lon):
    """Fetch current + 5-day forecast weather from Open-Meteo (free, no key)."""
    url = current_app.config["OPEN_METEO_URL"]
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max,weather_code",
        "timezone": "auto",
        "forecast_days": 5,
    }

    try:
        resp = requests.get(url, params=params, timeout=8)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException:
        raise UpstreamServiceError("Open-Meteo weather")

    current = data.get("current", {})
    daily = data.get("daily", {})

    forecast = []
    for i, date in enumerate(daily.get("time", [])):
        code = daily.get("weather_code", [None] * len(daily["time"]))[i]
        forecast.append({
            "date": date,
            "maxTemp": daily["temperature_2m_max"][i],
            "minTemp": daily["temperature_2m_min"][i],
            "rainChance": daily.get("precipitation_probability_max", [0])[i],
            "condition": WEATHER_CODES.get(code, "Unknown"),
        })

    return {
        "current": {
            "temperature": current.get("temperature_2m"),
            "humidity": current.get("relative_humidity_2m"),
            "windSpeed": current.get("wind_speed_10m"),
            "condition": WEATHER_CODES.get(current.get("weather_code"), "Unknown"),
        },
        "forecast": forecast,
    }
