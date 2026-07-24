import requests
from flask import current_app
from utils.errors import UpstreamServiceError


def get_route(origin_lat, origin_lon, dest_lat, dest_lon, profile="driving"):
    """Fetch a driving route + geometry between two points via OSRM (free, no key)."""
    base = current_app.config["OSRM_URL"]
    coords = f"{origin_lon},{origin_lat};{dest_lon},{dest_lat}"
    url = f"{base}/route/v1/{profile}/{coords}"
    params = {"overview": "full", "geometries": "geojson"}

    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException:
        raise UpstreamServiceError("OSRM routing")

    if data.get("code") != "Ok" or not data.get("routes"):
        raise UpstreamServiceError("OSRM routing", "No route found between locations")

    route = data["routes"][0]
    return {
        "distanceKm": round(route["distance"] / 1000, 1),
        "durationMinutes": round(route["duration"] / 60),
        "geometry": route["geometry"],  # GeoJSON LineString for Leaflet
    }
