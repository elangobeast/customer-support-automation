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
│
├── backend/
│   ├── app.py
│   ├── models.py
│   ├── database.py
│   ├── email_service.py
│   └── routes/
│       ├── tickets.py
│       └── webhooks.py
│
├── crew/
│   ├── agents.py
│   ├── tasks.py
│   ├── tools.py
│   └── crew_runner.py
│
├── data/
│   ├── seed_data.py
│   ├── knowledge_base.json
│   └── support.db
│
├── frontend/
│   ├── templates/
│   └── static/
│
├── config.py
├── run.py
├── requirements.txt
├── runtime.txt
└── README.md
```

# Setup

## 1. Create a Virtual Environment and Install Dependencies

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt
```

## 2. Configure Environment Variables

Create a `.env` file from the sample:

```bash
cp .env.example .env
```

Set the following variables:

* `OPENAI_API_KEY` – Required for CrewAI agents.
* `ANTHROPIC_API_KEY` – Optional alternative to OpenAI.
* `SMTP_USERNAME` – Optional.
* `SMTP_PASSWORD` – Optional.

If SMTP credentials are not provided, the application runs in **simulation mode**, and outgoing emails are printed to the console instead of being sent.

## 3. Seed the Database

Populate the database with sample clients, purchase history, FAQs, and policies:

```bash
python data/seed_data.py
```

## 4. Start the Application

```bash
python run.py
```

The server starts on:

```
http://localhost:5000
```

Dashboard:

```
http://localhost:5000/dashboard

```

# Using the Application

### Submit a Ticket

Open:

```
http://localhost:5000/submit
```

Use one of the sample client emails:

* `alice.johnson@example.com`
* `bob.smith@example.com`

to generate personalized responses based on purchase history.

### AI Processing

The CrewAI pipeline automatically processes tickets using three agents:

1. **Triage Agent**
2. **Research Agent**
3. **Response Agent**

The ticket status changes from:

```
Open → Drafted → Approved → Sent
```

### Review and Approve

Edit the AI-generated response and click:

* **Approve & Save**

### Send Email

Click:

* **Send Email to Client**

If SMTP credentials are missing, the email will be displayed in the console (simulation mode).

---

# Simulating Incoming Emails

Create tickets through the webhook endpoint:

```bash
curl -X POST http://localhost:5000/webhook/incoming-email \
-H "Content-Type: application/json" \
-d '{
      "from_email":"alice.johnson@example.com",
      "from_name":"Alice Johnson",
      "subject":"Refund for headphones",
      "body":"Hi, I bought wireless headphones last week and they stopped working. I would like a refund."
    }'
```

This automatically creates a ticket and triggers the CrewAI workflow.

---

# Notes

* SQLite database:

```
data/support.db
```

* Change `DATABASE_URL` in `.env` to use PostgreSQL or MySQL in production.

* `backend/email_service.py` contains helper functions for SMTP and IMAP integration.

* The CrewAI workflow is defined in:

```
crew/agents.py
crew/tasks.py
crew/crew_runner.py
```

and executes sequentially to generate intelligent customer support responses.
