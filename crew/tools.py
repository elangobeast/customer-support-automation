"""
tools.py
--------
Custom tools used by the Researcher agent.
"""

import json


def client_history_tool(client_id: str) -> str:
    from backend.app import create_app
    from backend.models import Client

    app = create_app()

    with app.app_context():
        try:
            client = Client.query.get(int(client_id))
        except (ValueError, TypeError):
            return "Invalid client_id provided."

        if not client:
            return f"No client found with ID {client_id}."

        return json.dumps({
            "name": client.name,
            "email": client.email,
            "tier": client.tier,
            "purchase_history": client.get_purchase_history(),
        }, indent=2)


def faq_search_tool(query: str) -> str:
    from backend.app import create_app
    from backend.models import KnowledgeBase

    app = create_app()

    with app.app_context():
        entries = KnowledgeBase.query.filter_by(type="FAQ").all()

    query_lower = query.lower()
    matches = [
        e for e in entries
        if query_lower in e.topic.lower() or query_lower in e.content.lower()
    ]

    if not matches:
        matches = entries

    return "\n\n".join(
        f"FAQ: {m.topic}\n{m.content}"
        for m in matches[:5]
    ) or "No FAQ entries found."


def policy_lookup_tool(topic: str) -> str:
    from backend.app import create_app
    from backend.models import KnowledgeBase

    app = create_app()

    with app.app_context():
        entries = KnowledgeBase.query.filter_by(type="Policy").all()

    topic_lower = topic.lower()
    matches = [
        e for e in entries
        if topic_lower in e.topic.lower() or topic_lower in e.content.lower()
    ]

    if not matches:
        matches = entries

    return "\n\n".join(
        f"Policy: {m.topic}\n{m.content}"
        for m in matches[:3]
    ) or "No policy documents found."