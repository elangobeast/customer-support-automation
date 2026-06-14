"""
tasks.py
--------
Defines the CrewAI tasks for the ticket-handling pipeline. Tasks are
chained via `context=` so that the Researcher can see the Triage
Agent's output, and the Responder can see both prior outputs.
"""

from crewai import Task, Agent


def build_triage_task(agent: Agent, subject: str, body: str) -> Task:
    """
    Task 1: Classify the ticket.
    Expected output: a short JSON-like block with `category` and `urgency`.
    """
    return Task(
        description=(
            "A new customer support ticket has arrived.\n\n"
            f"Subject: {subject}\n"
            f"Body:\n{body}\n\n"
            "Classify this ticket. Choose ONE category from: "
            "'Refund Request', 'Technical Issue', 'Billing Question', "
            "'General Inquiry', 'Complaint', 'Other'. "
            "Then assign an urgency level: 'Low', 'Medium', or 'High', "
            "based on the customer's tone and the impact of the issue.\n\n"
            "Also write a one-sentence summary of what the customer wants."
        ),
        expected_output=(
            "A JSON object with exactly these keys: "
            "\"category\" (string), \"urgency\" (string, one of Low/Medium/High), "
            "\"summary\" (one sentence string). "
            "Example: {\"category\": \"Refund Request\", \"urgency\": \"Medium\", "
            "\"summary\": \"Customer wants a refund for defective headphones.\"}"
        ),
        agent=agent,
    )


def build_research_task(agent: Agent, client_id, subject: str, body: str, triage_task: Task) -> Task:
    """
    Task 2: Research client history, policy, and FAQs relevant to the ticket.
    Uses the triage task's output as context.
    """
    return Task(
        description=(
            f"Using the triage classification from the previous task, research "
            f"everything needed to resolve this ticket for client ID "
            f"'{client_id}'.\n\n"
            f"Original ticket subject: {subject}\n"
            f"Original ticket body:\n{body}\n\n"
            "Steps:\n"
            "1. Use the 'Client Purchase History Lookup' tool with the given "
            "client ID to find relevant past orders.\n"
            "2. Use the 'Policy Lookup' tool with a keyword related to the "
            "ticket's category (e.g. 'refund', 'shipping', 'billing') to find "
            "the applicable company policy.\n"
            "3. Use the 'FAQ Search' tool with a keyword from the customer's "
            "issue to find any matching FAQ entries.\n\n"
            "Summarize all findings in clear, organized text that the "
            "response writer can use directly."
        ),
        expected_output=(
            "A structured text summary with three sections: "
            "'Client History:', 'Relevant Policy:', and 'Relevant FAQ:'. "
            "Include specific order IDs, dates, and amounts if found, and "
            "quote the key parts of any policy or FAQ that apply."
        ),
        agent=agent,
        context=[triage_task],
    )


def build_response_task(agent: Agent, client_name: str, subject: str, body: str,
                         triage_task: Task, research_task: Task) -> Task:
    """
    Task 3: Draft the final email response using triage + research context.
    """
    return Task(
        description=(
            f"Write a complete email reply to {client_name} regarding their "
            f"support ticket.\n\n"
            f"Original subject: {subject}\n"
            f"Original message:\n{body}\n\n"
            "Use the category/urgency from the triage task and the findings "
            "from the research task to craft your reply. The email should:\n"
            "- Greet the customer by name\n"
            "- Acknowledge their specific issue (reference order/account "
            "details if available)\n"
            "- Explain the resolution or relevant policy clearly\n"
            "- Provide concrete next steps or instructions\n"
            "- Close with a friendly, professional sign-off from "
            "'The Support Team'\n\n"
            "Match your tone to the urgency level: be especially empathetic "
            "for High urgency or Complaint tickets."
        ),
        expected_output=(
            "A complete, ready-to-send plain-text email including greeting, "
            "body, and sign-off. Do not include subject line or any JSON -- "
            "just the email body text."
        ),
        agent=agent,
        context=[triage_task, research_task],
    )
