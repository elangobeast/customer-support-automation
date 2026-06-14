"""
database.py
------------
Database initialization helpers. Exposes a single SQLAlchemy `db` instance
that is shared across models and the Flask app factory (avoids circular
imports).
"""

from flask_sqlalchemy import SQLAlchemy

# Single shared SQLAlchemy instance, initialized later via db.init_app(app)
db = SQLAlchemy()


def init_db(app):
    """
    Bind the SQLAlchemy instance to the Flask app and create all tables
    if they do not already exist.
    """
    db.init_app(app)
    with app.app_context():
        # Import models here so they are registered with SQLAlchemy
        # before create_all() is called.
        from backend import models  # noqa: F401
        db.create_all()
