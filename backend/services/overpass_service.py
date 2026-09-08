import requests
from flask import current_app
from utils.errors import UpstreamServiceError
from utils.geo import haversine_km


def _query_overpass(query):
    url = current_app.config["OVERPASS_URL"]
    headers = {"User-Agent": current_app.config["USER_AGENT"]}
    try:
        resp = requests.post(url, data={"data": query}, headers=headers, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException:
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
