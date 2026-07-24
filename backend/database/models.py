from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from database import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    trips = db.relationship("SavedTrip", backref="user", cascade="all, delete-orphan")
    favorites = db.relationship("FavoritePlace", backref="user", cascade="all, delete-orphan")

    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "email": self.email}


class SavedTrip(db.Model):
    __tablename__ = "saved_trips"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    origin = db.Column(db.String(200))
    destination = db.Column(db.String(200))
    people = db.Column(db.Integer, default=1)
    days = db.Column(db.Integer, default=1)
    budget = db.Column(db.Float, default=0)
    preference = db.Column(db.String(50))
    itinerary_json = db.Column(db.Text)  # JSON-serialized itinerary
    budget_json = db.Column(db.Text)     # JSON-serialized budget breakdown
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "origin": self.origin,
            "destination": self.destination,
            "people": self.people,
            "days": self.days,
            "budget": self.budget,
            "preference": self.preference,
            "itinerary": self.itinerary_json,
            "budgetBreakdown": self.budget_json,
            "createdAt": self.created_at.isoformat(),
        }


class FavoritePlace(db.Model):
    __tablename__ = "favorite_places"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    lat = db.Column(db.Float)
    lon = db.Column(db.Float)
    category = db.Column(db.String(80))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "lat": self.lat,
            "lon": self.lon,
            "category": self.category,
        }
