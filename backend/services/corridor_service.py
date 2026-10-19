"""Finds curated spots that lie ALONG a driving route ("on the way" highlights).

Works purely from the local Tourist_Spots.csv, so it needs no live API call and
keeps working when Overpass is down.
"""
import logging

from services import local_data_service
from utils.geo import RouteIndex

logger = logging.getLogger(__name__)

DEFAULT_WIDTH_KM = 5        # how far either side of the road still counts as "on the way"
DEFAULT_LIMIT = 15          # most stops to return
DEFAULT_SKIP_ENDS_KM = 10   # spots this close to the start or end are not "on the way";
                            # the destination ones already live on the Highlights tab
MAX_PER_STRETCH = 2         # a big city must not fill the whole list

# Tourist_Spots.csv also contains hotels, restaurants and cafes. They are not
# places to stop and see, so a spot carrying any of these tags is left out.
EXCLUDED_TAGS = {"hotel", "hospitality", "restaurant", "restaurants", "cafe", "cuisine"}


def get_route_highlights(route, width_km=DEFAULT_WIDTH_KM, limit=DEFAULT_LIMIT,
                         skip_ends_km=DEFAULT_SKIP_ENDS_KM):
    """route: the dict from osrm_service.get_route (needs geometry.coordinates).

    Returns a list in travel order (nearest the start first), each item:
    name, tags, lat, lon, offRouteKm (gap to the road), alongKm (km from start).
    """
    if not route:
        return []
    coordinates = (route.get("geometry") or {}).get("coordinates")
    if not coordinates or len(coordinates) < 2:
        return []

    index = RouteIndex(coordinates)

    # Step 1: every sightseeing spot inside the corridor.
    candidates = []
    for spot in local_data_service.get_all_tourist_spots():
        if EXCLUDED_TAGS & set(spot["tags"]):
            continue
        off_km, along_km = index.locate(spot["Latitude"], spot["Longitude"])
        if off_km > width_km:
            continue
        if along_km < skip_ends_km or along_km > index.total_km - skip_ends_km:
            continue
        candidates.append({
            "name": spot["Name"],
            "tags": spot["tags"],
            "lat": spot["Latitude"],
            "lon": spot["Longitude"],
            "offRouteKm": round(off_km, 1),
            "alongKm": round(along_km, 1),
        })

    # Step 2: spread the picks over the whole journey. A big city can have
    # dozens of spots; without a rule they would fill every slot. Cut the route
    # into `limit` equal stretches and keep at most MAX_PER_STRETCH spots per
    # stretch, preferring the ones closest to the road.
    stretch_km = index.total_km / limit
    by_stretch = {}
    for c in candidates:
        by_stretch.setdefault(int(c["alongKm"] // stretch_km), []).append(c)

    ranked = []   # (rank inside its stretch, gap to road, spot)
    for spots in by_stretch.values():
        spots.sort(key=lambda c: c["offRouteKm"])
        for rank, c in enumerate(spots[:MAX_PER_STRETCH]):
            ranked.append((rank, c["offRouteKm"], c))

    # Step 3: every stretch's best spot gets in before any stretch gets a
    # second one; then trim to the limit and present in travel order.
    ranked.sort(key=lambda item: (item[0], item[1]))
    chosen = [c for _, _, c in ranked[:limit]]
    chosen.sort(key=lambda c: c["alongKm"])
    return chosen