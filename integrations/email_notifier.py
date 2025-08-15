"""Simple email notifier using SMTP."""
from __future__ import annotations

import smtplib
from email.message import EmailMessage


def send_email(smtp_server: str, sender: str, recipient: str, subject: str, body: str) -> None:
    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.set_content(body)
    with smtplib.SMTP(smtp_server) as s:  # pragma: no cover - network
        s.send_message(msg)
