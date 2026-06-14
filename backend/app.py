"""
app.py
------
Flask application factory. Creates and configures the Flask app,
initializes the database, and registers blueprints for ticket and
webhook routes.
"""

import os
from flask import Flask

from config import Config
from backend.database import init_db


def create_app():
    """
    Application factory. Returns a configured Flask app instance.

    Templates and static files live in /frontend, so we point Flask's
    template_folder and static_folder there.
    """
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    template_dir = os.path.join(base_dir, "frontend", "templates")
    static_dir = os.path.join(base_dir, "frontend", "static")

    app = Flask(
        __name__,
        template_folder=template_dir,
        static_folder=static_dir,
    )
    app.config.from_object(Config)

    # Initialize database (creates tables on first run)
    init_db(app)

    # Register blueprints
    from backend.routes.tickets import tickets_bp
    from backend.routes.webhooks import webhooks_bp

    app.register_blueprint(tickets_bp)
    app.register_blueprint(webhooks_bp)

    return app
