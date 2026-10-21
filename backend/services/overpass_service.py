import logging
import time

import requests
from flask import current_app
from utils.errors import UpstreamServiceError
from utils.geo import RouteIndex, haversine_km

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


class OverpassRuntimeError(requests.RequestException):
    """Overpass accepted the query but gave up on it (out of time or memory).
    It reports this as HTTP 200 with an empty list and a "remark", which would
    otherwise look exactly like "there is nothing here"."""


def _is_outage(exc):
    """Decide whether a failure means 'Overpass is struggling' (trip the
    cooldown) or 'our own query was wrong' (do not)."""
    response = getattr(exc, "response", None)
    status = getattr(response, "status_code", None)
    if status is None:
        return True                      # timeout, connection error, bad JSON...
    return status >= 500 or status == 429   # server error or rate-limited


def _query_overpass(query, timeout=REQUEST_TIMEOUT, trip_cooldown=True):
    """timeout / trip_cooldown let the heavy along-route search use a longer
    timeout and avoid starting the global cooldown (see get_route_places)."""
    global _down_until

    if time.monotonic() < _down_until:
        raise UpstreamServiceError(
            "Overpass API", "skipped after a recent failure - using fallback data"
        )

    url = current_app.config["OVERPASS_URL"]
    headers = {"User-Agent": current_app.config["USER_AGENT"]}
    try:
        resp = requests.post(url, data={"data": query}, headers=headers, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        remark = data.get("remark", "") if isinstance(data, dict) else ""
        if "runtime error" in remark:
            raise OverpassRuntimeError(remark)
        return data
    except requests.RequestException as e:
        # Log the REAL reason; the error raised below is deliberately generic.
        status = getattr(getattr(e, "response", None), "status_code", None)
        reason = f"HTTP {status}" if status else type(e).__name__
        if isinstance(e, OverpassRuntimeError):
            reason = f"Overpass gave up: {str(e)[:100]}"
        if _is_outage(e) and trip_cooldown:
            _down_until = time.monotonic() + COOLDOWN_SECONDS
            logger.warning("Overpass request failed (%s); skipping Overpass for %ss", reason, COOLDOWN_SECONDS)
        elif not trip_cooldown:
            logger.warning("Overpass route query failed (%s); cooldown not started", reason)
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
    viewpoints, forests, parks - a broader, looser category
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

      node["leisure"="park"](around:{radius_m},{lat},{lon});
    );
    out center 30;
    """
    data = _query_overpass(query)
    return _elements_to_places(data.get("elements", []), lat, lon, "highlight")


# --- Along-the-route search --------------------------------------------------
# A driving route can be ~1,000 km and 15,000 points long, far too big for one
# Overpass query. We thin it to a waypoint every few km, cut it into pieces of
# about 200 km, and query the pieces one after another.
ROUTE_REQUEST_TIMEOUT = (4, 15)   # a bigger query gets a longer read timeout
ROUTE_STEP_KM = 4.0               # keep one waypoint about every 4 km
ROUTE_POINTS_PER_QUERY = 50       # ~200 km of road per query
ROUTE_MAX_QUERIES = 6             # more than this and the waypoints get thinner instead
ROUTE_TIME_BUDGET_S = 30          # stop starting new queries after this long
ROUTE_MAX_ELEMENTS = 150          # most places Overpass returns per query

_ROUTE_TAG_KEYS = ("tourism", "historic", "natural", "waterway")


def _route_waypoints(coordinates, step_km):
    """Thin a [[lon, lat], ...] route to roughly one point every step_km,
    always keeping the first and last points."""
    kept = [coordinates[0]]
    last = coordinates[0]
    for point in coordinates[1:]:
        if haversine_km(last[1], last[0], point[1], point[0]) >= step_km:
            kept.append(point)
            last = point
    if kept[-1] != coordinates[-1]:
        kept.append(coordinates[-1])
    return kept


def _route_query(waypoints, radius_m):
    """Overpass query for notable named places within radius_m of a polyline.
    Overpass wants the polyline as lat,lon pairs - the OPPOSITE order to the
    [lon, lat] points OSRM gives us."""
    line = ",".join(f"{lat},{lon}" for lon, lat in waypoints)
    around = f"(around:{radius_m},{line})"
    return f"""
    [out:json][timeout:25];
    (
      nwr["tourism"~"^(attraction|viewpoint|museum|zoo|theme_park)$"]["name"]{around};
      nwr["historic"~"^(castle|fort|monument|ruins|archaeological_site|palace)$"]["name"]{around};
      nwr["natural"~"^(waterfall|peak|cave_entrance|beach|hot_spring)$"]["name"]{around};
      nwr["waterway"~"^(waterfall|dam)$"]["name"]{around};
    );
    out center {ROUTE_MAX_ELEMENTS};
    """


def _route_elements_to_places(elements):
    places = []
    for el in elements:
        tags = el.get("tags", {})
        name = tags.get("name")
        lat = el.get("lat") or el.get("center", {}).get("lat")
        lon = el.get("lon") or el.get("center", {}).get("lon")
        if not name or lat is None or lon is None:
            continue
        kind = next((tags[k] for k in _ROUTE_TAG_KEYS if tags.get(k)), None)
        places.append({
            "key": (el.get("type"), el.get("id")),
            "name": name,
            "tags": [kind] if kind else [],
            "lat": lat,
            "lon": lon,
        })
    return places


def get_route_places(coordinates, width_km=5):
    """Notable named places within width_km of a route, from live OSM data.

    coordinates: [[lon, lat], ...] as returned by OSRM.
    Returns dicts with name, tags, lat, lon (not yet in travel order).

    Raises UpstreamServiceError if the FIRST query fails, so the caller can use
    its curated fallback. If a LATER query fails (or time runs out) it returns
    what it already has - part of the route beats nothing.
    These queries never start the global cooldown: a slow big query is not
    proof that Overpass is down, and must not switch off hotels and restaurants.
    """
    if not coordinates or len(coordinates) < 2:
        return []

    total_km = RouteIndex(coordinates).total_km
    step_km = max(ROUTE_STEP_KM, total_km / (ROUTE_POINTS_PER_QUERY * ROUTE_MAX_QUERIES))
    waypoints = _route_waypoints(coordinates, step_km)

    found = {}
    started = time.monotonic()
    pieces = range(0, len(waypoints) - 1, ROUTE_POINTS_PER_QUERY - 1)
    for n, start in enumerate(pieces):
        if n > 0 and time.monotonic() - started > ROUTE_TIME_BUDGET_S:
            logger.warning("Route search out of time after %s queries; using partial results", n)
            break
        query = _route_query(waypoints[start:start + ROUTE_POINTS_PER_QUERY], int(width_km * 1000))
        try:
            data = _query_overpass(query, timeout=ROUTE_REQUEST_TIMEOUT, trip_cooldown=False)
        except UpstreamServiceError:
            if n == 0:
                raise
            logger.warning("Route search stopped after %s queries; using partial results", n)
            break
        for place in _route_elements_to_places(data.get("elements", [])):
            found.setdefault(place["key"], place)

    return [{k: v for k, v in p.items() if k != "key"} for p in found.values()]