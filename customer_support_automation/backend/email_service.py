"""
email_service.py
-----------------
Handles outgoing email (via smtplib) and optional incoming email
fetching (via imaplib). Credentials are read from environment variables
defined in config.py / .env.

NOTE: For Gmail, you must use an "App Password" (not your normal
password) and enable IMAP access in your account settings.
"""

import smtplib
import imaplib
import email as email_lib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from config import Config


def send_email(to_address: str, subject: str, body: str) -> bool:
    """
    Send a plain-text email via SMTP.

    Returns True on success, False on failure (errors are logged to console
    so the calling route can decide how to inform the user).
    """
    if not Config.SMTP_USERNAME or not Config.SMTP_PASSWORD:
        print("[email_service] SMTP credentials not configured. "
              "Skipping actual send (simulation mode).")
        print(f"--- SIMULATED EMAIL ---\nTo: {to_address}\n"
              f"Subject: {subject}\n\n{body}\n-----------------------")
        return True  # Treat as "sent" in simulation mode for local dev

    try:
        msg = MIMEMultipart()
        msg["From"] = Config.SMTP_FROM_EMAIL
        msg["To"] = to_address
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(Config.SMTP_HOST, Config.SMTP_PORT) as server:
            server.starttls()
            server.login(Config.SMTP_USERNAME, Config.SMTP_PASSWORD)
            server.sendmail(Config.SMTP_FROM_EMAIL, to_address, msg.as_string())

        return True
    except Exception as exc:
        print(f"[email_service] Failed to send email: {exc}")
        return False


def fetch_unread_emails(limit: int = 10):
    """
    OPTIONAL: Fetch unread emails from the configured IMAP inbox.

    Returns a list of dicts: [{"from": ..., "subject": ..., "body": ...}, ...]

    This is provided as a starting point for a background poller that could
    call the /webhook/incoming-email endpoint for each new message. It is
    not wired into the app automatically -- call it from a scheduled job
    or management script if desired.
    """
    if not Config.IMAP_USERNAME or not Config.IMAP_PASSWORD:
        print("[email_service] IMAP credentials not configured. "
              "Returning empty list.")
        return []

    results = []
    try:
        mail = imaplib.IMAP4_SSL(Config.IMAP_HOST, Config.IMAP_PORT)
        mail.login(Config.IMAP_USERNAME, Config.IMAP_PASSWORD)
        mail.select("inbox")

        status, data = mail.search(None, "UNSEEN")
        if status != "OK":
            return []

        email_ids = data[0].split()[:limit]
        for eid in email_ids:
            status, msg_data = mail.fetch(eid, "(RFC822)")
            if status != "OK":
                continue

            raw_email = msg_data[0][1]
            msg = email_lib.message_from_bytes(raw_email)

            from_addr = email_lib.utils.parseaddr(msg.get("From"))[1]
            subject = msg.get("Subject", "(no subject)")

            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode(errors="ignore")
                        break
            else:
                body = msg.get_payload(decode=True).decode(errors="ignore")

            results.append({"from": from_addr, "subject": subject, "body": body})

        mail.logout()
    except Exception as exc:
        print(f"[email_service] Failed to fetch emails: {exc}")

    return results
