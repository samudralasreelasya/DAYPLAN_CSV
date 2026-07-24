from flask import Blueprint, request, jsonify
from services import local_data_service

local_bp = Blueprint("local_attractions", __name__)


@local_bp.route("/api/local-attractions", methods=["GET"])
def city_attractions():
    city = request.args.get("city", "")
    if not city:
        return jsonify({"error": "city query param required"}), 400
    return jsonify({"city": city, "spots": local_data_service.get_city_spots(city)})


@local_bp.route("/api/trending", methods=["GET"])
def trending_places():
    limit = request.args.get("limit", default=10, type=int)
    return jsonify({"trending": local_data_service.get_trending_places(limit)})