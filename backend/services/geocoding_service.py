import requests
from flask import current_app
from utils.errors import UpstreamServiceError


def geocode(place_name):
    """Resolve a place name to lat/lon + display name using OpenStreetMap Nominatim."""
    if not place_name:
        raise UpstreamServiceError("Geocoding", "No place name provided")

    url = f"{current_app.config['NOMINATIM_URL']}/search"
    params = {"q": place_name, "format": "json", "limit": 1, "addressdetails": 1}
    headers = {"User-Agent": current_app.config["USER_AGENT"]}

    try:
        resp = requests.get(url, params=params, headers=headers, timeout=8)
        resp.raise_for_status()
        results = resp.json()
    except requests.RequestException:
        raise UpstreamServiceError("Nominatim geocoding")

    if not results:
        raise UpstreamServiceError("Geocoding", f"Could not locate '{place_name}'")

    top = results[0]
    return {
        "name": place_name,
        "displayName": top.get("display_name"),
        "lat": float(top["lat"]),
        "lon": float(top["lon"]),
        "type": top.get("type"),
    }


def reverse_geocode(lat, lon):
    url = f"{current_app.config['NOMINATIM_URL']}/reverse"
    params = {"lat": lat, "lon": lon, "format": "json"}
    headers = {"User-Agent": current_app.config["USER_AGENT"]}

    try:
        resp = requests.get(url, params=params, headers=headers, timeout=8)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException:
        raise UpstreamServiceError("Nominatim reverse geocoding")
