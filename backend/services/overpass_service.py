import logging
import time

import requests
from flask import current_app
from utils.errors import UpstreamServiceError
from utils.geo import haversine_km

logger = logging.getLogger(__name__)

# --- Fail-fast settings ------------------------------------------------------
# The public Overpass server is shared and sometimes at capacity. Without a
# limit, every one of the (up to 4) Overpass calls in a single trip plan waits
# for its full timeout, so one outage made a trip plan take about a minute.
#
# Rule: after ONE failed call, skip Overpass entirely for COOLDOWN_SECONDS and
# let the callers use their curated CSV fallback straight away. Then try again.
REQUEST_TIMEOUT = (4, 12)   # (connect, read) seconds - fail fast, do not hang
COOLDOWN_SECONDS = 120
_down_until = 0.0           # time.monotonic() value until which Overpass is skipped


def _is_outage(exc):
    """Decide whether a failure means 'Overpass is struggling' (trip the
    cooldown) or 'our own query was wrong' (do not)."""
    response = getattr(exc, "response", None)
    status = getattr(response, "status_code", None)
    if status is None:
        return True                      # timeout, connection error, bad JSON...
    return status >= 500 or status == 429   # server error or rate-limited


def _query_overpass(query):
    global _down_until

    if time.monotonic() < _down_until:
        raise UpstreamServiceError(
            "Overpass API", "skipped after a recent failure - using fallback data"
        )

    url = current_app.config["OVERPASS_URL"]
    headers = {"User-Agent": current_app.config["USER_AGENT"]}
    try:
        resp = requests.post(url, data={"data": query}, headers=headers, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        # Log the REAL reason; the error raised below is deliberately generic.
        status = getattr(getattr(e, "response", None), "status_code", None)
        reason = f"HTTP {status}" if status else type(e).__name__
        if _is_outage(e):
            _down_until = time.monotonic() + COOLDOWN_SECONDS
            logger.warning("Overpass request failed (%s); skipping Overpass for %ss", reason, COOLDOWN_SECONDS)
        else:
            logger.warning("Overpass rejected the query (%s); not treating as an outage", reason)
        raise UpstreamServiceError("Overpass API")


def _diet_status(tags):
    """Map OSM diet:* tags to the same veg_status vocabulary used in the
    curated CSVs (veg / non-veg / both / NA), so live and fallback data
    are consistent for the frontend and don't need two branches of
    display logic downstream."""
    veg = tags.get("diet:vegetarian")
    non_veg = tags.get("diet:vegan") is None and veg in (None, "no")

    if veg == "only":
        return "veg"
    if veg == "yes":
        # Serves veg but tag doesn't say veg-only -> treat as mixed menu
        return "both"
    if veg == "no":
        return "non-veg"
    return "NA"  # tag not present in OSM data for this place


def _elements_to_places(elements, lat, lon, category):
    places = []
    for el in elements:
        tags = el.get("tags", {})
        name = tags.get("name")
        if not name:
            continue
        el_lat = el.get("lat") or el.get("center", {}).get("lat")
        el_lon = el.get("lon") or el.get("center", {}).get("lon")
        if el_lat is None or el_lon is None:
            continue
        distance = round(haversine_km(lat, lon, el_lat, el_lon), 2)
        places.append({
            "id": el.get("id"),
            "name": name,
            "category": category,
            "cuisine": tags.get("cuisine", "").replace(";", ", ") or None,
            "stars": tags.get("stars"),
            "vegStatus": _diet_status(tags) if category == "restaurant" else None,
            "lat": el_lat,
            "lon": el_lon,
            "distanceKm": distance,
            "address": tags.get("addr:street"),
        })
    places.sort(key=lambda p: p["distanceKm"])
    return places[:20]


def get_hotels(lat, lon, radius_m=3000):
    query = f"""
    [out:json][timeout:15];
    (
      node["tourism"="hotel"](around:{radius_m},{lat},{lon});
      node["tourism"="guest_house"](around:{radius_m},{lat},{lon});
    );
    out center 30;
    """
    data = _query_overpass(query)
    return _elements_to_places(data.get("elements", []), lat, lon, "hotel")


def get_restaurants(lat, lon, radius_m=3000):
    query = f"""
    [out:json][timeout:15];
    (
      node["amenity"="restaurant"](around:{radius_m},{lat},{lon});
      node["amenity"="cafe"](around:{radius_m},{lat},{lon});
    );
    out center 30;
    """
    data = _query_overpass(query)
    return _elements_to_places(data.get("elements", []), lat, lon, "restaurant")


def get_attractions(lat, lon, radius_m=5000):
    query = f"""
    [out:json][timeout:15];
    (
      node["tourism"="attraction"](around:{radius_m},{lat},{lon});
      node["tourism"="museum"](around:{radius_m},{lat},{lon});
      node["historic"](around:{radius_m},{lat},{lon});
    );
    out center 30;
    """
    data = _query_overpass(query)
    return _elements_to_places(data.get("elements", []), lat, lon, "attraction")


def get_highlights(lat, lon, radius_m=5000):
    """Notable named 'highlight' spots near a destination - dams,
    viewpoints, forests, scenic bars/parks - a broader, looser category
    than get_attractions() (which is museums/historic sites only).
    Feeds the destination-radius highlights tag feature."""
    query = f"""
    [out:json][timeout:15];
    (
      node["tourism"="viewpoint"](around:{radius_m},{lat},{lon});
      node["natural"="peak"](around:{radius_m},{lat},{lon});
      node["natural"="waterfall"](around:{radius_m},{lat},{lon});
      way["natural"="wood"](around:{radius_m},{lat},{lon});
      way["landuse"="forest"](around:{radius_m},{lat},{lon});
      node["waterway"="dam"](around:{radius_m},{lat},{lon});
      way["waterway"="dam"](around:{radius_m},{lat},{lon});
      node["amenity"="bar"](around:{radius_m},{lat},{lon});
      node["leisure"="park"](around:{radius_m},{lat},{lon});
    );
    out center 30;
    """
    data = _query_overpass(query)
    return _elements_to_places(data.get("elements", []), lat, lon, "highlight")