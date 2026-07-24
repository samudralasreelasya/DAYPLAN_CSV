from flask_sqlalchemy import SQLAlchemy

# Single shared SQLAlchemy instance, imported by app.py and models.py
db = SQLAlchemy()
