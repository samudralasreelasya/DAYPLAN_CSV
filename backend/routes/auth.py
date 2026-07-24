from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from database import db
from database.models import User
from utils.validators import require_fields, validate_email, validate_password
from utils.errors import ValidationError

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/api/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    require_fields(data, ["name", "email", "password"])
    validate_email(data["email"])
    validate_password(data["password"])

    if User.query.filter_by(email=data["email"].lower().strip()).first():
        raise ValidationError("An account with this email already exists")

    user = User(name=data["name"].strip(), email=data["email"].lower().strip())
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=str(user.id))
    return jsonify({"token": token, "user": user.to_dict()}), 201


@auth_bp.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    require_fields(data, ["email", "password"])

    user = User.query.filter_by(email=data["email"].lower().strip()).first()
    if not user or not user.check_password(data["password"]):
        raise ValidationError("Invalid email or password", payload={})

    token = create_access_token(identity=str(user.id))
    return jsonify({"token": token, "user": user.to_dict()})


@auth_bp.route("/api/profile", methods=["GET"])
@jwt_required()
def profile():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        raise ValidationError("User not found", payload={})
    return jsonify(user.to_dict())
