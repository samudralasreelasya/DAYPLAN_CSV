from flask import Blueprint, request, jsonify

from services import geocoding_service, overpass_service
from utils.validators import require_fields

restaurants_bp = Blueprint("restaurants", __name__)


@restaurants_bp.route("/api/restaurants", methods=["GET"])
def get_restaurants():
    args = request.args
    require_fields(args, ["destination"])
    geo = geocoding_service.geocode(args["destination"])
    restaurants = overpass_service.get_restaurants(geo["lat"], geo["lon"])
    return jsonify({"destination": geo, "restaurants": restaurants})
