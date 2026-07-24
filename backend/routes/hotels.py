from flask import Blueprint, request, jsonify

from services import geocoding_service, overpass_service
from utils.validators import require_fields

hotels_bp = Blueprint("hotels", __name__)


@hotels_bp.route("/api/hotels", methods=["GET"])
def get_hotels():
    args = request.args
    require_fields(args, ["destination"])
    geo = geocoding_service.geocode(args["destination"])
    hotels = overpass_service.get_hotels(geo["lat"], geo["lon"])
    return jsonify({"destination": geo, "hotels": hotels})
