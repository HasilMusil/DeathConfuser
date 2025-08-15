"""Email notifications using SMTP."""
from __future__ import annotations

import asyncio
from email.message import EmailMessage
import smtplib


class EmailNotifier:
    """Async email notifier using SMTP."""
    def __init__(self, host: str, sender: str, recipient: str) -> None:
        self.host = host
        self.sender = sender
        self.recipient = recipient

    async def send(self, subject: str, body: str) -> None:
        msg = EmailMessage()
        msg["From"] = self.sender
        msg["To"] = self.recipient
        msg["Subject"] = subject
        msg.set_content(body)
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._send_sync, msg)

    def _send_sync(self, msg: EmailMessage) -> None:
        with smtplib.SMTP(self.host) as smtp:  # pragma: no cover
            smtp.send_message(msg)


# Simple functional helper
def send_email(smtp_server: str, sender: str, recipient: str, subject: str, body: str) -> None:
    notifier = EmailNotifier(smtp_server, sender, recipient)
    asyncio.run(notifier.send(subject, body))


__all__ = ["EmailNotifier", "send_email"]
