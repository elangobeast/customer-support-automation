"""
tools.py
--------
Custom CrewAI tools used by the Researcher agent to look up:
- A client's purchase history from the database.
- FAQ entries from the knowledge base.
- Policy documents from the knowledge base.

Each tool is a small wrapper around a simple SQLAlchemy query, exposed
to CrewAI via the @tool decorator so the Researcher agent can call it
during its task.
"""

import json
from crewai import LLM
from crewai.tools import tool


@tool("Client Purchase History Lookup")
def client_history_tool(client_id: str) -> str:
    """
    Look up a client's purchase history by client ID.
    Input should be the numeric client ID as a string.
    Returns a JSON string of the client's past orders, or a message
    if no client is found.
    """
    # Imported here to avoid circular imports at module load time
    from backend.app import create_app
    from backend.database import db
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


@tool("FAQ Search")
def faq_search_tool(query: str) -> str:
    """
    Search the knowledge base for FAQ entries whose topic or content
    contains the given query string (case-insensitive substring match).
    Returns matching FAQ entries as formatted text.
    """
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
        # Fall back to returning all FAQs if no direct match, so the
        # agent still has some context to reason over.
        matches = entries

    return "\n\n".join(f"FAQ: {m.topic}\n{m.content}" for m in matches[:5]) or \
        "No FAQ entries found."


@tool("Policy Lookup")
def policy_lookup_tool(topic: str) -> str:
    """
    Look up company policy documents related to a topic (e.g. 'refund',
    'shipping', 'cancellation'). Returns matching policy text.
    """
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

    return "\n\n".join(f"Policy: {m.topic}\n{m.content}" for m in matches[:3]) or \
        "No policy documents found."
