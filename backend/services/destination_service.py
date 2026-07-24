import logging
from services import geocoding_service, overpass_service, local_data_service

logger = logging.getLogger(__name__)

BEST_TIME_BY_HEMISPHERE = {
    "north": "October to March (cooler, dry season)",
    "south": "April to September (cooler, dry season)",
}


def get_attractions_with_fallback(place_name, lat, lon):
    """Fetch attractions from Overpass; fall back to / blend in curated CSV
    data when Overpass fails entirely or returns too little. Shared by both
    the /api/destination route and the /api/plan-trip orchestrator."""
    try:
        attractions = overpass_service.get_attractions(lat, lon)
    except Exception as e:
        logger.error("Overpass get_attractions failed for %s: %s", place_name, e)
        attractions = []

    local_spots = local_data_service.get_city_spots(place_name, lat, lon)
    if len(attractions) < 5 and local_spots:
        attractions += [
            {
                "name": s["Name"],
                "category": "Attraction (curated)",
                "distanceKm": s["distanceKm"],
                "lat": s["Latitude"],
                "lon": s["Longitude"],
            }
            for s in local_spots
        ]

    attractions.sort(key=lambda a: a["distanceKm"] if a["distanceKm"] is not None else float("inf"))
    return attractions


def get_destination_details(place_name):
    """Resolve a destination and enrich it with nearby attractions."""
    geo = geocoding_service.geocode(place_name)
    attractions = get_attractions_with_fallback(place_name, geo["lat"], geo["lon"])

    hemisphere = "north" if geo["lat"] >= 0 else "south"

    return {
        "destination": geo,
        "bestTimeToVisit": BEST_TIME_BY_HEMISPHERE[hemisphere],
        "attractions": [
            {
                "name": a["name"],
                "category": a.get("cuisine") or a.get("category") or "Attraction",
                "distanceKm": a["distanceKm"],
                "lat": a["lat"],
                "lon": a["lon"],
            }
            for a in attractions
        ],
    }