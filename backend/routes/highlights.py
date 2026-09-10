from flask import Blueprint, request, jsonify

from services import geocoding_service, highlight_service
from utils.validators import require_fields

highlights_bp = Blueprint("highlights", __name__)


@highlights_bp.route("/api/highlights", methods=["GET"])
def get_highlights():
    args = request.args
    require_fields(args, ["destination"])
    geo = geocoding_service.geocode(args["destination"])

    # ?radius_km=15 lets the frontend widen/narrow the search radius,
    # same query-param style as the rest of your API.
    radius_km = float(args.get("radius_km", 10))

    result = highlight_service.get_highlight_details(
        args["destination"], geo["lat"], geo["lon"], radius_km=radius_km
    )
    return jsonify(result)
