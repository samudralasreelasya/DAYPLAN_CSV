import logging
from services import overpass_service, local_data_service

logger = logging.getLogger(__name__)


def get_highlights_with_fallback(place_name, lat, lon, radius_km=10):
    """Fetch highlight spots from Overpass; fall back to / blend in the
    curated Tourist_Spots.csv dataset when Overpass fails entirely or
    returns too little. Mirrors restaurant_service.get_restaurants_with_fallback
    exactly: same try/except for total failure, same len(...) < 5 sparse
    check, same "blend in, do not replace" behaviour.
    """
    try:
        highlights = overpass_service.get_highlights(lat, lon, radius_m=int(radius_km * 1000))
    except Exception as e:
        logger.error("Overpass get_highlights failed for %s: %s", place_name, e)
        highlights = []

    local_highlights = local_data_service.get_nearby_highlights(lat, lon, radius_km=radius_km)

    if len(highlights) < 5 and local_highlights:
        highlights += [
            {
                "name": h["Name"],
                "category": "highlight (curated)",
                "tags": h.get("tags", []),
                "distanceKm": h["distanceKm"],
                "lat": h.get("Latitude"),
                "lon": h.get("Longitude"),
            }
            for h in local_highlights
        ]

    highlights.sort(
        key=lambda h: h["distanceKm"] if h["distanceKm"] is not None else float("inf")
    )
    return highlights


def get_highlight_details(place_name, lat, lon, radius_km=10):
    """Route-facing shape, parallel to restaurant_service.get_restaurant_details."""
    highlights = get_highlights_with_fallback(place_name, lat, lon, radius_km=radius_km)

    return {
        "place": place_name,
        "highlights": [
            {
                "name": h["name"],
                "category": h.get("category", "highlight"),
                "tags": h.get("tags", []),
                "distanceKm": h["distanceKm"],
                "lat": h["lat"],
                "lon": h["lon"],
            }
            for h in highlights
        ],
    }
