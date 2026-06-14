# Customer Support Ticket Automation

An end-to-end customer support automation system built with **Flask** and
**CrewAI**. Incoming support tickets are automatically:

1. **Triaged** — categorized (Refund Request, Technical Issue, Billing
   Question, General Inquiry, Complaint, Other) and assigned an urgency
   level (Low / Medium / High).
2. **Researched** — relevant client purchase history, company policies,
   and FAQ entries are gathered.
3. **Responded to** — a personalized draft email is generated for a
   human support agent to review, edit, approve, and send.

## Project Structure

```
customer_support_automation/
├── README.md
├── requirements.txt
├── .env.example
├── run.py
├── config.py
├── backend/
│   ├── app.py              # Flask app factory + routes registration
│   ├── models.py           # Client, Ticket, KnowledgeBase models
│   ├── database.py         # SQLAlchemy init helpers
│   ├── email_service.py     # SMTP send / IMAP fetch
│   └── routes/
│       ├── tickets.py       # dashboard, ticket detail, submit, approve, send
│       └── webhooks.py      # /webhook/incoming-email
├── crew/
│   ├── agents.py            # Triage, Researcher, Responder agents
│   ├── tasks.py              # Task definitions (chained via context)
│   ├── tools.py              # Client history / FAQ / policy lookup tools
│   └── crew_runner.py        # Assembles and runs the crew per ticket
├── data/
│   ├── seed_data.py           # Seeds clients + knowledge base
│   ├── knowledge_base.json    # Sample FAQs & policies
│   └── support.db             # SQLite DB (created on first run)
└── frontend/
    ├── templates/             # base, dashboard, ticket_detail, submit_ticket
    └── static/css, static/js
```

## Setup

1. **Create a virtual environment and install dependencies**

   ```bash
   python -m venv venv
   source venv/bin/activate    # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure environment variables**

   ```bash
   cp .env.example .env
   ```

   Edit `.env` and set at least:
   - `OPENAI_API_KEY` — required for the CrewAI agents (or set
     `ANTHROPIC_API_KEY` instead — see `crew/agents.py`)
   - `SMTP_USERNAME` / `SMTP_PASSWORD` — optional. If left blank, the app
     runs in **simulation mode**: emails are printed to the console
     instead of actually sent.

3. **Seed the database** (sample clients, purchase history, FAQs, policies)

   ```bash
   python data/seed_data.py
   ```

4. **Run the app**

   ```bash
   python run.py
   ```

5. Open your browser to **http://localhost:5000/dashboard**

## Using the App

- **Submit a ticket**: Go to "Submit Ticket" in the nav bar. Use one of
  the seeded client emails (e.g. `alice.johnson@example.com`) to see
  purchase-history-aware responses.
- **Watch it process**: The ticket detail page polls automatically and
  refreshes once the AI crew finishes (status changes to "Drafted").
- **Review & edit**: Edit the AI-generated draft in the text box, then
  click **Approve & Save**.
- **Send**: Once approved, click **Send Email to Client**. If SMTP
  credentials aren't configured, the email is printed to the console
  instead of actually sent (simulation mode).

## Simulating Incoming Emails

You can simulate an inbound support email via the webhook endpoint:

```bash
curl -X POST http://localhost:5000/webhook/incoming-email \
  -H "Content-Type: application/json" \
  -d '{
        "from_email": "alice.johnson@example.com",
        "from_name": "Alice Johnson",
        "subject": "Refund for headphones",
        "body": "Hi, I bought wireless headphones last week and they stopped working. I would like a refund."
      }'
```

This creates a ticket and kicks off the CrewAI pipeline in the background,
just like the web form.

## Notes

- The database is SQLite by default (`data/support.db`), suitable for
  local development. Swap `DATABASE_URL` in `.env` for Postgres/MySQL in
  production.
- `email_service.fetch_unread_emails()` is provided as a starting point
  for polling a real inbox via IMAP — wire it into a scheduled job to
  automatically create tickets from real customer emails.
- All three CrewAI agents (Triage, Researcher, Responder) and their tasks
  are defined in `crew/agents.py` and `crew/tasks.py` and run sequentially
  via `crew/crew_runner.py`.
