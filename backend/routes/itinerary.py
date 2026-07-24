from flask import Blueprint, request, jsonify

from services import destination_service, weather_service, ai_service
from utils.validators import require_fields, parse_int

itinerary_bp = Blueprint("itinerary", __name__)


@itinerary_bp.route("/api/itinerary", methods=["POST"])
def generate_itinerary():
    data = request.get_json(silent=True) or {}
    require_fields(data, ["destination", "days"])

    days = parse_int(data.get("days"), "days", min_value=1)

    details = destination_service.get_destination_details(data["destination"])
    dest_geo = details["destination"]
    weather = weather_service.get_weather(dest_geo["lat"], dest_geo["lon"])

    result = ai_service.generate_itinerary(
        data["destination"], days, details["attractions"], weather["forecast"]
    )
    return jsonify(result)
