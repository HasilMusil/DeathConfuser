"""Notification helpers."""

from __future__ import annotations

import json
import smtplib
from email.message import EmailMessage
from typing import Any, Dict, Iterable

import requests

from .logger import get_logger


def send_webhook(url: str, payload: Dict[str, Any]) -> bool:
    """Send a JSON payload to the given webhook URL."""

    log = get_logger(__name__)
    try:
        resp = requests.post(url, json=payload, timeout=10)
        log.debug("Webhook %s responded with %s", url, resp.status_code)
        return resp.status_code < 300
    except requests.RequestException as exc:  # pragma: no cover - network
        log.error("Webhook failed: %s", exc)
        return False


def send_slack(webhook: str, text: str) -> bool:
    return send_webhook(webhook, {"text": text})


def send_discord(webhook: str, content: str) -> bool:
    return send_webhook(webhook, {"content": content})


def send_email(smtp_server: str, from_addr: str, to_addrs: Iterable[str], subject: str, body: str) -> bool:
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = ",".join(to_addrs)
    msg.set_content(body)

    try:
        with smtplib.SMTP(smtp_server) as s:
            s.send_message(msg)
        return True
    except Exception as exc:  # pragma: no cover - network
        get_logger(__name__).error("Email failed: %s", exc)
        return False


def should_notify(event: Dict[str, Any], levels: Iterable[str]) -> bool:
    return event.get("level", "info").lower() in {l.lower() for l in levels}

