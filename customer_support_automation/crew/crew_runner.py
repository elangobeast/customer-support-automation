"""
crew_runner.py
--------------
Assembles the CrewAI Crew (Triage -> Researcher -> Responder) and runs it
for a given ticket. Updates the Ticket row in the database with the
results at each stage.

The main entry point is `run_ticket_crew(ticket_id)`, which is called
from the Flask backend (typically in a background thread) whenever a
new ticket is created.
"""

import json
import re
from crewai import Crew, Process

from crew.agents import build_triage_agent, build_researcher_agent, build_responder_agent
from crew.tasks import build_triage_task, build_research_task, build_response_task


def _extract_json(text: str) -> dict:
    """
    Best-effort extraction of a JSON object from an LLM's text output,
    in case it wraps the JSON in markdown code fences or extra prose.
    """
    # Try direct parse first
    try:
        return json.loads(text)
    except (ValueError, TypeError):
        pass

    # Try to find a {...} block within the text
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except (ValueError, TypeError):
            pass

    return {}


def run_ticket_crew(ticket_id: int):
    """
    Run the full Triage -> Research -> Respond pipeline for the given
    ticket ID, persisting results to the database as each stage completes.

    This function creates its own Flask app context so it can be safely
    called from a background thread.
    """
    # Imported here to avoid circular imports (app <-> crew_runner)
    from backend.app import create_app
    from backend.database import db
    from backend.models import Ticket

    app = create_app()
    with app.app_context():
        ticket = Ticket.query.get(ticket_id)
        if not ticket:
            print(f"[crew_runner] Ticket {ticket_id} not found.")
            return

        subject = ticket.subject
        body = ticket.body
        client_id = ticket.client_id
        client_name = ticket.client.name if ticket.client else "Valued Customer"

        # --- Build agents ---
        triage_agent = build_triage_agent()
        researcher_agent = build_researcher_agent()
        responder_agent = build_responder_agent()

        # --- Build tasks (chained via context) ---
        triage_task = build_triage_task(triage_agent, subject, body)
        research_task = build_research_task(
            researcher_agent, client_id, subject, body, triage_task
        )
        response_task = build_response_task(
            responder_agent, client_name, subject, body, triage_task, research_task
        )

        # --- Assemble and run the crew sequentially ---
        crew = Crew(
            agents=[triage_agent, researcher_agent, responder_agent],
            tasks=[triage_task, research_task, response_task],
            process=Process.sequential,
            verbose=True,
        )

        try:
            crew.kickoff()
        except Exception as exc:
            print(f"[crew_runner] Crew execution failed for ticket {ticket_id}: {exc}")
            ticket.status = "New"
            db.session.commit()
            return

        # --- Parse and persist results from each task ---
        triage_output = _extract_json(str(triage_task.output))
        category = triage_output.get("category", "Other")
        urgency = triage_output.get("urgency", "Low")

        research_output = str(research_task.output)
        response_output = str(response_task.output)

        ticket.category = category
        ticket.urgency = urgency
        ticket.research_notes = research_output
        ticket.ai_draft = response_output
        ticket.status = "Drafted"

        db.session.commit()
        print(f"[crew_runner] Ticket {ticket_id} processed successfully -> "
              f"category={category}, urgency={urgency}")
