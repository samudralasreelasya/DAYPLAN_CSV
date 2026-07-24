import logging
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from config import Config
from database import db
from utils.errors import register_error_handlers

from routes.auth import auth_bp
from routes.trip import trip_bp
from routes.destination import destination_bp
from routes.transport import transport_bp
from routes.route import route_bp
from routes.hotels import hotels_bp
from routes.restaurants import restaurants_bp
from routes.weather import weather_bp
from routes.budget import budget_bp
from routes.itinerary import itinerary_bp
from routes.saved import saved_bp
from routes.local_attractions import local_bp
from services import local_data_service

logging.basicConfig(level=logging.INFO)


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    JWTManager(app)
    CORS(app, origins=app.config["CORS_ORIGINS"], supports_credentials=True)

    register_error_handlers(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(trip_bp)
    app.register_blueprint(destination_bp)
    app.register_blueprint(transport_bp)
    app.register_blueprint(route_bp)
    app.register_blueprint(hotels_bp)
    app.register_blueprint(restaurants_bp)
    app.register_blueprint(weather_bp)
    app.register_blueprint(budget_bp)
    app.register_blueprint(itinerary_bp)
    app.register_blueprint(saved_bp)
    app.register_blueprint(local_bp)

    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok", "service": "DayPlan API"})

    local_data_service.load_all()

    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)