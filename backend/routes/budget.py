from flask import Blueprint, request, jsonify

from services import budget_service
from utils.validators import require_fields, parse_int, parse_float

budget_bp = Blueprint("budget", __name__)


@budget_bp.route("/api/budget", methods=["POST"])
def calculate_budget():
    data = request.get_json(silent=True) or {}
    require_fields(data, ["people", "days"])

    people = parse_int(data.get("people"), "people", min_value=1)
    days = parse_int(data.get("days"), "days", min_value=1)
    preference = data.get("preference", "standard")
    distance_km = parse_float(data.get("distanceKm"), "distanceKm", default=0, min_value=0)

    breakdown = budget_service.estimate_budget(people, days, preference, distance_km)
    return jsonify(breakdown)
