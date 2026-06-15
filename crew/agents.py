"""
agents.py
---------
Defines the three CrewAI agents used by the Customer Support Ticket
Automation system:

1. Ticket Triage Agent - categorizes and prioritizes incoming tickets.
2. Researcher Agent - gathers client history, policies, and FAQ context.
3. Responder Agent - drafts the final customer-facing reply.

Each agent is given a clear role, goal, and backstory as required by
CrewAI best practices, which strongly influences the quality and tone
of the LLM's output for that agent's tasks.
"""

import os
from crewai import Agent
from config import Config
from crew.tools import client_history_tool, faq_search_tool, policy_lookup_tool


def get_llm():
    if Config.OPENAI_API_KEY:
        os.environ["OPENAI_API_KEY"] = Config.OPENAI_API_KEY
        return Config.OPENAI_MODEL_NAME

    if Config.ANTHROPIC_API_KEY:
        os.environ["ANTHROPIC_API_KEY"] = Config.ANTHROPIC_API_KEY
        return "anthropic/claude-3-5-haiku-20241022"

    raise EnvironmentError(
        "No LLM API key configured. Set OPENAI_API_KEY or ANTHROPIC_API_KEY in .env"
    )

def build_triage_agent() -> Agent:
    """
    The Ticket Triage Agent reads the raw email subject/body and decides:
    - category: Refund Request, Technical Issue, Billing Question,
                 General Inquiry, Complaint, or Other
    - urgency: Low, Medium, or High
    """
    return Agent(
        role="Customer Support Triage Specialist",
        goal=(
            "Quickly and accurately classify each incoming support ticket "
            "into the correct category and assign an urgency level "
            "(Low, Medium, High) based on the customer's tone, keywords, "
            "and the nature of their request."
        ),
        backstory=(
            "You have spent years on the front lines of customer support, "
            "reading thousands of emails. You have an instinct for spotting "
            "frustrated or urgent customers versus routine questions, and "
            "you know how to sort tickets so the right team can act fast."
        ),
        llm=get_llm(),
        verbose=True,
        allow_delegation=False,
    )


def build_researcher_agent() -> Agent:
    """
    The Researcher Agent gathers all context needed to answer the ticket:
    client purchase history, relevant company policy, and matching FAQ
    entries. It uses the custom tools defined in crew/tools.py.
    """
    return Agent(
        role="Customer History & Knowledge Researcher",
        goal=(
            "Given a ticket's category and the client's ID, gather all "
            "relevant supporting information: the client's purchase "
            "history, any applicable company policy (e.g. refund or "
            "shipping policy), and FAQ entries that address similar "
            "questions. Summarize these findings clearly for the "
            "response writer."
        ),
        backstory=(
            "You are a meticulous internal analyst with full access to the "
            "CRM and knowledge base. Support agents rely on your research "
            "to make sure every response is accurate and grounded in real "
            "account data and official policy."
        ),
        tools=[client_history_tool, faq_search_tool, policy_lookup_tool],
        llm=get_llm(),
        verbose=True,
        allow_delegation=False,
    )


def build_responder_agent() -> Agent:
    """
    The Responder Agent writes the final email reply to the customer,
    using the triage classification and the researcher's findings.
    """
    return Agent(
        role="Customer Response Writer",
        goal=(
            "Write a warm, professional, and personalized email response "
            "to the customer. Reference their specific order or account "
            "details where relevant, explain the resolution clearly using "
            "the researched policy/FAQ information, and provide clear "
            "next steps. Match the tone to the ticket's urgency -- be "
            "extra empathetic for high-urgency or complaint tickets."
        ),
        backstory=(
            "You are a skilled customer service writer known across the "
            "company for replies that are concise, empathetic, and make "
            "customers feel heard while clearly resolving their issue."
        ),
        llm=get_llm(),
        verbose=True,
        allow_delegation=False,
    )
