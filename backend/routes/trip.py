import logging
from flask import Blueprint, request, jsonify

from services import geocoding_service, osrm_service, weather_service
from services import overpass_service, destination_service, budget_service, ai_service
from utils.validators import require_fields, parse_int, parse_float

logger = logging.getLogger(__name__)

trip_bp = Blueprint("trip", __name__)


@trip_bp.route("/api/plan-trip", methods=["POST"])
def plan_trip():
    """Orchestrates the full planning flow in one call: geocode both points,
    fetch route, destination details, hotels, restaurants, weather, budget
    and an AI itinerary — so the frontend can render everything from a single
    search action."""
    data = request.get_json(silent=True) or {}
    require_fields(data, ["origin", "destination"])

    people = parse_int(data.get("people"), "people", default=1, min_value=1)
    days = parse_int(data.get("days"), "days", default=1, min_value=1)
    budget_pref = data.get("preference", "standard")
    user_budget = parse_float(data.get("budget"), "budget", default=0, min_value=0)

    origin_geo = geocoding_service.geocode(data["origin"])
    dest_geo = geocoding_service.geocode(data["destination"])

    try:
        route = osrm_service.get_route(
            origin_geo["lat"], origin_geo["lon"], dest_geo["lat"], dest_geo["lon"]
        )
    except Exception as e:
        logger.error("OSRM get_route failed: %s", e)
        route = None

    attractions = destination_service.get_attractions_with_fallback(
        data["destination"], dest_geo["lat"], dest_geo["lon"]
    )

    try:
        hotels = overpass_service.get_hotels(dest_geo["lat"], dest_geo["lon"])
    except Exception as e:
        logger.error("Overpass get_hotels failed: %s", e)
        hotels = []

    try:
        restaurants = overpass_service.get_restaurants(dest_geo["lat"], dest_geo["lon"])
    except Exception as e:
        logger.error("Overpass get_restaurants failed: %s", e)
        restaurants = []

    try:
        weather = weather_service.get_weather(dest_geo["lat"], dest_geo["lon"])
    except Exception as e:
        logger.error("Open-Meteo get_weather failed: %s", e)
        weather = None

    budget_breakdown = budget_service.estimate_budget(
        people, days, budget_pref, distance_km=route["distanceKm"] if route else None
    )

    itinerary = ai_service.generate_itinerary(
        data["destination"], days, attractions, weather["forecast"] if weather else None
    )

    return jsonify({
        "origin": origin_geo,
        "destination": dest_geo,
        "route": route,
        "attractions": attractions[:12],
        "hotels": hotels[:10],
        "restaurants": restaurants[:10],
        "weather": weather,
        "budget": budget_breakdown,
        "userBudget": user_budget,
        "itinerary": itinerary["itinerary"],
        "packingSuggestions": itinerary["packingSuggestions"],
        "people": people,
        "days": days,
        "preference": budget_pref,
    })