"""
seed_data.py
------------
Populates the SQLite database with sample clients (including purchase
history) and loads the FAQ/policy content from knowledge_base.json into
the KnowledgeBase table.

Run with: python data/seed_data.py
"""

import os
import sys
import json

# Allow running this script directly: add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app import create_app
from backend.database import db
from backend.models import Client, KnowledgeBase
from config import Config


SAMPLE_CLIENTS = [
    {
        "name": "Alice Johnson",
        "email": "alice.johnson@example.com",
        "tier": "VIP",
        "purchase_history": [
            {"order_id": "A1001", "item": "Wireless Headphones", "date": "2025-06-01", "price": 59.99},
            {"order_id": "A1002", "item": "USB-C Charging Cable", "date": "2025-06-05", "price": 12.99},
        ],
    },
    {
        "name": "Brian Smith",
        "email": "brian.smith@example.com",
        "tier": "standard",
        "purchase_history": [
            {"order_id": "B2001", "item": "Bluetooth Speaker", "date": "2025-05-20", "price": 39.99},
        ],
    },
    {
        "name": "Carla Mendes",
        "email": "carla.mendes@example.com",
        "tier": "standard",
        "purchase_history": [
            {"order_id": "C3001", "item": "Smart Watch", "date": "2025-04-15", "price": 129.99},
            {"order_id": "C3002", "item": "Watch Band - Leather", "date": "2025-04-15", "price": 19.99},
            {"order_id": "C3003", "item": "Screen Protector Pack", "date": "2025-05-10", "price": 8.99},
        ],
    },
    {
        "name": "David Lee",
        "email": "david.lee@example.com",
        "tier": "VIP",
        "purchase_history": [
            {"order_id": "D4001", "item": "Laptop Stand", "date": "2025-03-02", "price": 45.00},
        ],
    },
    {
        "name": "Emma Wilson",
        "email": "emma.wilson@example.com",
        "tier": "standard",
        "purchase_history": [],
    },
]


def seed():
    app = create_app()
    with app.app_context():
        # --- Seed clients ---
        for c in SAMPLE_CLIENTS:
            existing = Client.query.filter_by(email=c["email"]).first()
            if existing:
                print(f"Client already exists, skipping: {c['email']}")
                continue

            client = Client(
                name=c["name"],
                email=c["email"],
                tier=c["tier"],
                purchase_history=json.dumps(c["purchase_history"]),
            )
            db.session.add(client)
            print(f"Added client: {c['name']} ({c['email']})")

        db.session.commit()

        # --- Seed knowledge base from JSON file ---
        if KnowledgeBase.query.count() > 0:
            print("Knowledge base already populated, skipping.")
        else:
            with open(Config.KNOWLEDGE_BASE_PATH, "r") as f:
                kb_data = json.load(f)

            for faq in kb_data.get("faqs", []):
                db.session.add(KnowledgeBase(topic=faq["topic"], content=faq["content"], type="FAQ"))

            for policy in kb_data.get("policies", []):
                db.session.add(KnowledgeBase(topic=policy["topic"], content=policy["content"], type="Policy"))

            db.session.commit()
            print("Knowledge base seeded with FAQs and policies.")

        print("\nSeeding complete!")


if __name__ == "__main__":
    seed()
