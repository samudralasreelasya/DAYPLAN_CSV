"""Finds spots that lie ALONG a driving route ("on the way" highlights).

Two sources, same resilience pattern as restaurants and highlights:
  * live OpenStreetMap data from Overpass (broad coverage, can be down), and
  * the curated Tourist_Spots.csv (small, always available).
Both are merged and put through the same corridor / spread rules. If Overpass
fails, the curated spots alone are used, so the feature never breaks.
"""
import logging

from services import local_data_service, overpass_service
from utils.geo import RouteIndex, haversine_km

logger = logging.getLogger(__name__)

DEFAULT_WIDTH_KM = 5        # how far either side of the road still counts as "on the way"
DEFAULT_LIMIT = 15          # most stops to return
DEFAULT_SKIP_ENDS_KM = 10   # spots this close to the start or end are not "on the way";
                            # the destination ones already live on the Highlights tab
MAX_PER_STRETCH = 2         # a big city must not fill the whole list
SAME_PLACE_KM = 0.25        # two spots this close are treated as the same place

# Hotels, restaurants and cafes in Tourist_Spots.csv are not places to stop and
# see. One shared rule (in local_data_service) keeps this and the destination
# highlights consistent.
EXCLUDED_TAGS = local_data_service.EXCLUDED_TAGS


def _live_spots(coordinates, width_km):
    """Live OSM places along the route, or [] if Overpass is unavailable."""
    try:
        return overpass_service.get_route_places(coordinates, width_km=width_km)
    except Exception as e:
        logger.warning("Live route search unavailable, using curated spots only: %s", e)
        return []


def _same_name(a, b):
    return " ".join(str(a).lower().split()) == " ".join(str(b).lower().split())


def _is_duplicate(name, lat, lon, candidates):
    """True if a candidate with the same name, or sitting on the same spot, exists."""
    for c in candidates:
        if _same_name(c["name"], name):
            return True
        if (abs(c["lat"] - lat) < 0.003 and abs(c["lon"] - lon) < 0.003
                and haversine_km(c["lat"], c["lon"], lat, lon) < SAME_PLACE_KM):
            return True
    return False


def get_route_highlights(route, width_km=DEFAULT_WIDTH_KM, limit=DEFAULT_LIMIT,
                         skip_ends_km=DEFAULT_SKIP_ENDS_KM):
    """route: the dict from osrm_service.get_route (needs geometry.coordinates).

    Returns a list in travel order (nearest the start first), each item:
    name, tags, lat, lon, offRouteKm (gap to the road), alongKm (km from start),
    source ("curated" or "live").
    """
    if not route:
        return []
    coordinates = (route.get("geometry") or {}).get("coordinates")
    if not coordinates or len(coordinates) < 2:
        return []

    index = RouteIndex(coordinates)

    def make_candidate(name, tags, lat, lon, source):
        """A candidate if the spot is inside the corridor and not at either end."""
        off_km, along_km = index.locate(lat, lon)
        if off_km > width_km:
            return None
        if along_km < skip_ends_km or along_km > index.total_km - skip_ends_km:
            return None
        return {
            "name": name, "tags": tags, "lat": lat, "lon": lon, "source": source,
            "offRouteKm": round(off_km, 1), "alongKm": round(along_km, 1),
        }

    # Step 1: every sightseeing spot inside the corridor. Curated spots go in
    # first, so when a live spot is the same place it is the live copy that is dropped.
    candidates = []
    for spot in local_data_service.get_all_tourist_spots():
        if EXCLUDED_TAGS & set(spot["tags"]):
            continue
        c = make_candidate(spot["Name"], spot["tags"], spot["Latitude"], spot["Longitude"], "curated")
        if c:
            candidates.append(c)

    for spot in _live_spots(coordinates, width_km):
        c = make_candidate(spot["name"], spot["tags"], spot["lat"], spot["lon"], "live")
        if c and not _is_duplicate(c["name"], c["lat"], c["lon"], candidates):
            candidates.append(c)

    # Step 2: spread the picks over the whole journey. A big city can have
    # dozens of spots; without a rule they would fill every slot. Cut the route
    # into `limit` equal stretches and keep at most MAX_PER_STRETCH spots per
    # stretch. Inside a stretch curated spots come first (they are hand-checked),
    # then the closest to the road.
    stretch_km = index.total_km / limit
    by_stretch = {}
    for c in candidates:
        by_stretch.setdefault(int(c["alongKm"] // stretch_km), []).append(c)

    ranked = []   # (rank inside its stretch, gap to road, spot)
    for spots in by_stretch.values():
        spots.sort(key=lambda c: (c["source"] != "curated", c["offRouteKm"]))
        for rank, c in enumerate(spots[:MAX_PER_STRETCH]):
            ranked.append((rank, c["offRouteKm"], c))

    # Step 3: every stretch's best spot gets in before any stretch gets a
    # second one; then trim to the limit and present in travel order.
    ranked.sort(key=lambda item: (item[0], item[1]))
    chosen = [c for _, _, c in ranked[:limit]]
    chosen.sort(key=lambda c: c["alongKm"])
    return chosen