import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Central app configuration. Values are read from environment variables
    so secrets never live in source control."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(basedir, 'dayplan.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-jwt-secret-change-me")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)

    # Free / no-key external APIs
    NOMINATIM_URL = "https://nominatim.openstreetmap.org"
    OSRM_URL = "https://router.project-osrm.org"
    OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
    OVERPASS_URL = "https://overpass-api.de/api/interpreter"

    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "http://localhost:5173").split(",")

    # Required by Nominatim's usage policy: identify the app in requests
    USER_AGENT = "DayPlanApp/1.0 (contact@dayplan.example)"
