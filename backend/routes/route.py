from flask import Blueprint, request, jsonify

from services import geocoding_service, osrm_service
from utils.validators import require_fields

route_bp = Blueprint("route", __name__)


@route_bp.route("/api/route", methods=["GET"])
def get_route():
    args = request.args
    require_fields(args, ["origin", "destination"])

    origin_geo = geocoding_service.geocode(args["origin"])
    dest_geo = geocoding_service.geocode(args["destination"])
    route = osrm_service.get_route(
        origin_geo["lat"], origin_geo["lon"], dest_geo["lat"], dest_geo["lon"]
    )

    return jsonify({"origin": origin_geo, "destination": dest_geo, "route": route})
