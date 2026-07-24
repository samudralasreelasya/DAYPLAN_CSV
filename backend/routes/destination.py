from flask import Blueprint, request, jsonify

from services import destination_service
from utils.validators import require_fields

destination_bp = Blueprint("destination", __name__)


@destination_bp.route("/api/destination", methods=["GET"])
def get_destination():
    data = request.args
    require_fields(data, ["name"])
    result = destination_service.get_destination_details(data["name"])
    return jsonify(result)
