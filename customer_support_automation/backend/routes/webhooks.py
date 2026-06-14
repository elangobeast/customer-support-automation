"""
webhooks.py
-----------
Endpoint to simulate or receive incoming support emails from an external
email service / forwarding integration. In production, this could be
called by a service like SendGrid Inbound Parse, Mailgun Routes, or a
scheduled job that polls IMAP via email_service.fetch_unread_emails().
"""

import threading
from flask import Blueprint, request, jsonify

from backend.database import db
from backend.models import Ticket, Client
from crew.crew_runner import run_ticket_crew

webhooks_bp = Blueprint("webhooks", __name__)


@webhooks_bp.route("/webhook/incoming-email", methods=["POST"])
def incoming_email():
    """
    Accepts JSON payload:
    {
        "from_email": "client@example.com",
        "from_name": "Jane Doe",
        "subject": "Refund request",
        "body": "I would like a refund for..."
    }

    Creates (or matches) a Client, creates a new Ticket, and triggers the
    CrewAI pipeline in the background.
    """
    data = request.get_json(silent=True) or {}

    from_email = data.get("from_email", "").strip()
    from_name = data.get("from_name", "Unknown Customer").strip()
    subject = data.get("subject", "(no subject)").strip()
    body = data.get("body", "").strip()

    if not from_email or not body:
        return jsonify({"error": "from_email and body are required"}), 400

    client = Client.query.filter_by(email=from_email).first()
    if not client:
        client = Client(name=from_name, email=from_email, tier="standard",
                         purchase_history="[]")
        db.session.add(client)
        db.session.commit()

    ticket = Ticket(client_id=client.id, subject=subject, body=body, status="New")
    db.session.add(ticket)
    db.session.commit()

    thread = threading.Thread(target=run_ticket_crew, args=(ticket.id,))
    thread.daemon = True
    thread.start()

    return jsonify({"message": "Ticket created", "ticket_id": ticket.id}), 201
