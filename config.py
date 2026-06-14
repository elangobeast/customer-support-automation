"""
config.py
---------
Centralized configuration for the Customer Support Ticket Automation app.
Loads environment variables from .env and exposes them as a Config class
used by the Flask application factory.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file at project root
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))


class Config:
    """Application-wide configuration values."""

    # Flask
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")
    DEBUG = os.environ.get("FLASK_DEBUG", "True") == "True"

    # Database (SQLite by default, stored in /data)
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'data', 'support.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # LLM
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
    OPENAI_MODEL_NAME = os.environ.get("OPENAI_MODEL_NAME", "gpt-4o-mini")
    ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

    # SMTP (outgoing email)
    SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
    SMTP_USERNAME = os.environ.get("SMTP_USERNAME", "")
    SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
    SMTP_FROM_EMAIL = os.environ.get("SMTP_FROM_EMAIL", "support@example.com")

    # IMAP (incoming email, optional)
    IMAP_HOST = os.environ.get("IMAP_HOST", "imap.gmail.com")
    IMAP_PORT = int(os.environ.get("IMAP_PORT", 993))
    IMAP_USERNAME = os.environ.get("IMAP_USERNAME", "")
    IMAP_PASSWORD = os.environ.get("IMAP_PASSWORD", "")

    # Knowledge base file
    KNOWLEDGE_BASE_PATH = os.path.join(BASE_DIR, "data", "knowledge_base.json")
