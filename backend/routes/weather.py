from flask import Blueprint, request, jsonify

from services import geocoding_service, weather_service
from utils.validators import require_fields

weather_bp = Blueprint("weather", __name__)


@weather_bp.route("/api/weather", methods=["GET"])
def get_weather():
    args = request.args
    require_fields(args, ["destination"])
    geo = geocoding_service.geocode(args["destination"])
    weather = weather_service.get_weather(geo["lat"], geo["lon"])
    return jsonify({"destination": geo, **weather})
