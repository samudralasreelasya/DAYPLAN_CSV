import logging
from services import overpass_service, local_data_service

logger = logging.getLogger(__name__)


def get_restaurants_with_fallback(place_name, lat, lon, veg_only=False):
    """Fetch restaurants from Overpass; fall back to / blend in curated CSV
    data when Overpass fails entirely or returns too little.

    Mirrors destination_service.get_attractions_with_fallback exactly:
    same try/except for total failure, same len(...) < 5 sparse check,
    same "blend in, don't replace" behaviour when live data is thin.
    """
    try:
        restaurants = overpass_service.get_restaurants(lat, lon)
    except Exception as e:
        logger.error("Overpass get_restaurants failed for %s: %s", place_name, e)
        restaurants = []

    if veg_only:
        restaurants = [
            r for r in restaurants
            if r.get("vegStatus") in ("veg", "both", "NA")
            # "NA" is kept here (not excluded) because OSM frequently has
            # no diet tag at all even for genuinely veg-friendly places -
            # excluding untagged results would make the live path look
            # emptier than it really is. The curated CSV fallback below
            # has explicit VegStatus for every row, so it doesn't have
            # this ambiguity.
        ]

    local_restaurants = local_data_service.get_city_restaurants(
        place_name, lat, lon, veg_only=veg_only
    )

    if len(restaurants) < 5 and local_restaurants:
        restaurants += [
            {
                "name": r["Name"],
                "category": r.get("Category", "Restaurant (curated)"),
                "vegStatus": r.get("VegStatus"),
                "openingHours": r.get("OpeningHours"),
                "notes": r.get("Notes"),
                "distanceKm": r["distanceKm"],
                "lat": r.get("Latitude"),
                "lon": r.get("Longitude"),
            }
            for r in local_restaurants
        ]

    restaurants.sort(
        key=lambda r: r["distanceKm"] if r["distanceKm"] is not None else float("inf")
    )
    return restaurants


def get_restaurant_details(place_name, lat, lon, veg_only=False):
    """Route-facing shape, parallel to destination_service.get_destination_details."""
    restaurants = get_restaurants_with_fallback(place_name, lat, lon, veg_only=veg_only)

    return {
        "place": place_name,
        "vegFilterApplied": veg_only,
        "restaurants": [
            {
                "name": r["name"],
                "category": r.get("category", "Restaurant"),
                "vegStatus": r.get("vegStatus", "NA"),
                "openingHours": r.get("openingHours"),
                "distanceKm": r["distanceKm"],
                "lat": r["lat"],
                "lon": r["lon"],
            }
            for r in restaurants
        ],
    }
