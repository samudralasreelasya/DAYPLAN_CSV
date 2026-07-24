import json
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from database import db
from database.models import SavedTrip, FavoritePlace
from utils.validators import require_fields
from utils.errors import ValidationError

saved_bp = Blueprint("saved", __name__)


@saved_bp.route("/api/trips", methods=["POST"])
@jwt_required()
def save_trip():
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}
    require_fields(data, ["origin", "destination"])

    trip = SavedTrip(
        user_id=user_id,
        origin=data["origin"],
        destination=data["destination"],
        people=data.get("people", 1),
        days=data.get("days", 1),
        budget=data.get("budget", 0),
        preference=data.get("preference", "standard"),
        itinerary_json=json.dumps(data.get("itinerary", [])),
        budget_json=json.dumps(data.get("budgetBreakdown", {})),
    )
    db.session.add(trip)
    db.session.commit()
    return jsonify(trip.to_dict()), 201


@saved_bp.route("/api/trips", methods=["GET"])
@jwt_required()
def list_trips():
    user_id = int(get_jwt_identity())
    trips = SavedTrip.query.filter_by(user_id=user_id).order_by(SavedTrip.created_at.desc()).all()
    return jsonify([t.to_dict() for t in trips])


@saved_bp.route("/api/trips/<int:trip_id>", methods=["DELETE"])
@jwt_required()
def delete_trip(trip_id):
    user_id = int(get_jwt_identity())
    trip = SavedTrip.query.filter_by(id=trip_id, user_id=user_id).first()
    if not trip:
        raise ValidationError("Trip not found", payload={})
    db.session.delete(trip)
    db.session.commit()
    return jsonify({"message": "Trip deleted"})


@saved_bp.route("/api/favorites", methods=["POST"])
@jwt_required()
def add_favorite():
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}
    require_fields(data, ["name"])

    fav = FavoritePlace(
        user_id=user_id,
        name=data["name"],
        lat=data.get("lat"),
        lon=data.get("lon"),
        category=data.get("category", "place"),
    )
    db.session.add(fav)
    db.session.commit()
    return jsonify(fav.to_dict()), 201


@saved_bp.route("/api/favorites", methods=["GET"])
@jwt_required()
def list_favorites():
    user_id = int(get_jwt_identity())
    favs = FavoritePlace.query.filter_by(user_id=user_id).all()
    return jsonify([f.to_dict() for f in favs])


@saved_bp.route("/api/favorites/<int:fav_id>", methods=["DELETE"])
@jwt_required()
def delete_favorite(fav_id):
    user_id = int(get_jwt_identity())
    fav = FavoritePlace.query.filter_by(id=fav_id, user_id=user_id).first()
    if not fav:
        raise ValidationError("Favorite not found", payload={})
    db.session.delete(fav)
    db.session.commit()
    return jsonify({"message": "Favorite removed"})
