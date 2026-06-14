"""
run.py
------
Entry point for the Customer Support Ticket Automation app.
Run with: python run.py
"""

from backend.app import create_app
from config import Config

app = create_app()

if __name__ == "__main__":
    app.run(debug=Config.DEBUG, host="0.0.0.0", port=5000)
