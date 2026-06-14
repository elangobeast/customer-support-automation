"""
models.py
---------
SQLAlchemy ORM models for the Customer Support Ticket Automation app.

Models:
- Client: a customer/account, with purchase history stored as JSON text.
- Ticket: a single support ticket / email, with triage, research, and
  response data filled in by the CrewAI crew.
- KnowledgeBase: FAQ entries and policy documents used by the Researcher agent.
"""

import json
from datetime import datetime
from backend.database import db


class Client(db.Model):
    """Represents a customer/account in the CRM."""

    __tablename__ = "clients"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    tier = db.Column(db.String(20), default="standard")  # standard / VIP
    # Purchase history stored as a JSON string, e.g.:
    # [{"order_id": "A123", "item": "Wireless Headphones",
    #   "date": "2025-06-01", "price": 59.99}, ...]
    purchase_history = db.Column(db.Text, default="[]")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    tickets = db.relationship("Ticket", backref="client", lazy=True)

    def get_purchase_history(self):
        """Return purchase history as a Python list of dicts."""
        try:
            return json.loads(self.purchase_history)
        except (ValueError, TypeError):
            return []

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "tier": self.tier,
            "purchase_history": self.get_purchase_history(),
        }


class Ticket(db.Model):
    """Represents a single customer support ticket / email thread."""

    __tablename__ = "tickets"

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=True)

    subject = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)

    # Filled in by the Ticket Triage Agent
    category = db.Column(db.String(50), default="Uncategorized")
    urgency = db.Column(db.String(20), default="Low")  # Low / Medium / High

    # Filled in by the Researcher Agent (stored as plain text summary)
    research_notes = db.Column(db.Text, default="")

    # Filled in by the Responder Agent
    ai_draft = db.Column(db.Text, default="")

    # Final response, possibly edited by a human support agent
    final_response = db.Column(db.Text, default="")

    # New -> Triaged -> Researched -> Drafted -> Approved -> Sent
    status = db.Column(db.String(20), default="New")

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "client_id": self.client_id,
            "client_name": self.client.name if self.client else "Unknown",
            "client_email": self.client.email if self.client else None,
            "subject": self.subject,
            "body": self.body,
            "category": self.category,
            "urgency": self.urgency,
            "research_notes": self.research_notes,
            "ai_draft": self.ai_draft,
            "final_response": self.final_response,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class KnowledgeBase(db.Model):
    """Represents an FAQ entry or policy document used for research."""

    __tablename__ = "knowledge_base"

    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(20), nullable=False)  # "FAQ" or "Policy"

    def to_dict(self):
        return {
            "id": self.id,
            "topic": self.topic,
            "content": self.content,
            "type": self.type,
        }
