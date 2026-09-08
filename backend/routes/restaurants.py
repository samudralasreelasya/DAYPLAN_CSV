from flask import Blueprint, request, jsonify

from services import geocoding_service, restaurant_service
from utils.validators import require_fields

restaurants_bp = Blueprint("restaurants", __name__)


@restaurants_bp.route("/api/restaurants", methods=["GET"])
def get_restaurants():
    args = request.args
    require_fields(args, ["destination"])
    geo = geocoding_service.geocode(args["destination"])

    # ?veg=true lets the frontend request veg-only results without a
    # separate endpoint - same query-param style as the rest of your API.
    veg_only = args.get("veg", "false").lower() == "true"

    result = restaurant_service.get_restaurant_details(
        args["destination"], geo["lat"], geo["lon"], veg_only=veg_only
    )
    return jsonify(result)
