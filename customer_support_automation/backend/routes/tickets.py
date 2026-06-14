"""
tickets.py
----------
Routes for viewing the ticket dashboard, viewing a single ticket,
submitting new tickets, and approving/sending responses.
"""

import threading
from flask import Blueprint, render_template, request, redirect, url_for, jsonify

from backend.database import db
from backend.models import Ticket, Client
from backend.email_service import send_email
from crew.crew_runner import run_ticket_crew

tickets_bp = Blueprint("tickets", __name__)


@tickets_bp.route("/")
def index():
    """Redirect root to the dashboard."""
    return redirect(url_for("tickets.dashboard"))


@tickets_bp.route("/dashboard")
def dashboard():
    """
    Display all tickets, optionally filtered by status or urgency via
    query parameters: /dashboard?status=Drafted&urgency=High
    """
    status_filter = request.args.get("status")
    urgency_filter = request.args.get("urgency")

    query = Ticket.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    if urgency_filter:
        query = query.filter_by(urgency=urgency_filter)

    tickets = query.order_by(Ticket.created_at.desc()).all()
    return render_template(
        "dashboard.html",
        tickets=tickets,
        status_filter=status_filter,
        urgency_filter=urgency_filter,
    )


@tickets_bp.route("/ticket/<int:ticket_id>")
def ticket_detail(ticket_id):
    """Display the full detail view for a single ticket."""
    ticket = Ticket.query.get_or_404(ticket_id)
    return render_template("ticket_detail.html", ticket=ticket)


@tickets_bp.route("/ticket/submit", methods=["GET", "POST"])
def submit_ticket():
    """
    GET: show the client-facing ticket submission form.
    POST: create a new ticket (and client if needed), then kick off the
          CrewAI pipeline in a background thread so the page responds
          immediately.
    """
    if request.method == "GET":
        return render_template("submit_ticket.html")

    name = request.form.get("name", "").strip()
    email_address = request.form.get("email", "").strip()
    subject = request.form.get("subject", "").strip()
    body = request.form.get("message", "").strip()

    if not (name and email_address and subject and body):
        return render_template(
            "submit_ticket.html", error="All fields are required."
        )

    # Find existing client by email, or create a new one
    client = Client.query.filter_by(email=email_address).first()
    if not client:
        client = Client(name=name, email=email_address, tier="standard",
                         purchase_history="[]")
        db.session.add(client)
        db.session.commit()

    ticket = Ticket(
        client_id=client.id,
        subject=subject,
        body=body,
        status="New",
    )
    db.session.add(ticket)
    db.session.commit()

    # Run the CrewAI pipeline asynchronously so the user isn't blocked
    # waiting for the LLM calls to complete.
    thread = threading.Thread(target=run_ticket_crew, args=(ticket.id,))
    thread.daemon = True
    thread.start()

    return render_template("submit_ticket.html",
                            success=f"Ticket #{ticket.id} submitted! "
                                    f"Our AI assistant is processing it now.")


@tickets_bp.route("/ticket/<int:ticket_id>/approve", methods=["POST"])
def approve_ticket(ticket_id):
    """
    Save a support agent's (possibly edited) version of the AI draft as
    the final_response, and mark the ticket as Approved.
    """
    ticket = Ticket.query.get_or_404(ticket_id)
    final_text = request.form.get("final_response", "").strip()

    if not final_text:
        return jsonify({"error": "final_response cannot be empty"}), 400

    ticket.final_response = final_text
    ticket.status = "Approved"
    db.session.commit()

    return redirect(url_for("tickets.ticket_detail", ticket_id=ticket.id))


@tickets_bp.route("/ticket/<int:ticket_id>/send", methods=["POST"])
def send_ticket_response(ticket_id):
    """
    Send the approved final_response to the client's email address via
    the configured SMTP server, and mark the ticket as Sent.
    """
    ticket = Ticket.query.get_or_404(ticket_id)

    if not ticket.final_response:
        return jsonify({"error": "No final response to send. Approve a draft first."}), 400

    if not ticket.client:
        return jsonify({"error": "Ticket has no associated client email."}), 400

    success = send_email(
        to_address=ticket.client.email,
        subject=f"Re: {ticket.subject}",
        body=ticket.final_response,
    )

    if success:
        ticket.status = "Sent"
        db.session.commit()
        return redirect(url_for("tickets.ticket_detail", ticket_id=ticket.id))

    return jsonify({"error": "Failed to send email. Check SMTP configuration."}), 500


@tickets_bp.route("/api/ticket/<int:ticket_id>/status")
def ticket_status(ticket_id):
    """
    Lightweight JSON endpoint used by dashboard.js to poll a ticket's
    processing status (e.g. waiting for 'Drafted' after submission).
    """
    ticket = Ticket.query.get_or_404(ticket_id)
    return jsonify(ticket.to_dict())
