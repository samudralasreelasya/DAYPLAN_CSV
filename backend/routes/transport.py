from flask import Blueprint, request, jsonify

from services import geocoding_service, osrm_service
from utils.validators import require_fields

transport_bp = Blueprint("transport", __name__)


@transport_bp.route("/api/transport", methods=["GET"])
def get_transport():
    """Returns estimated transport mode availability and durations.
    No free, keyless API exposes live flight/train/bus schedules, so
    availability + timing are heuristically derived from great-circle /
    driving distance. This is clearly labeled as an estimate in the response."""
    args = request.args
    require_fields(args, ["origin", "destination"])

    origin_geo = geocoding_service.geocode(args["origin"])
    dest_geo = geocoding_service.geocode(args["destination"])
    route = osrm_service.get_route(
        origin_geo["lat"], origin_geo["lon"], dest_geo["lat"], dest_geo["lon"]
    )
    distance_km = route["distanceKm"]

    options = []

    # Car: always available, use actual OSRM driving time
    options.append({
        "mode": "car",
        "available": True,
        "estimatedDurationMinutes": route["durationMinutes"],
        "estimatedCost": round(distance_km * 0.1, 2),
    })

    # Bus: available for reasonable regional distances
    bus_available = distance_km <= 1200
    options.append({
        "mode": "bus",
        "available": bus_available,
        "estimatedDurationMinutes": round((distance_km / 55) * 60) if bus_available else None,
        "estimatedCost": round(distance_km * 0.05, 2) if bus_available else None,
    })

    # Train: available if distance suggests a viable rail corridor
    train_available = distance_km <= 2000
    options.append({
        "mode": "train",
        "available": train_available,
        "estimatedDurationMinutes": round((distance_km / 80) * 60) if train_available else None,
        "estimatedCost": round(distance_km * 0.07, 2) if train_available else None,
    })

    # Flight: worthwhile beyond ~300km
    flight_available = distance_km >= 300
    options.append({
        "mode": "flight",
        "available": flight_available,
        "estimatedDurationMinutes": round((distance_km / 700) * 60 + 90) if flight_available else None,
        "estimatedCost": round(distance_km * 0.15, 2) if flight_available else None,
    })

    return jsonify({
        "origin": origin_geo,
        "destination": dest_geo,
        "distanceKm": distance_km,
        "options": options,
        "note": "Durations and costs are estimates; verify with a live booking provider.",
    })
