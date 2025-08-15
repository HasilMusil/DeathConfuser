"""Telegram bot notifications."""
from __future__ import annotations

import aiohttp
from typing import Any
from ..core.logger import get_logger

log = get_logger(__name__)


class TelegramNotifier:
    """Async Telegram notifier using Bot API."""
    def __init__(self, token: str, chat_id: str) -> None:
        self.token = token
        self.chat_id = chat_id

    async def send(self, message: str) -> bool:
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        data = {"chat_id": self.chat_id, "text": message}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data) as resp:
                if resp.status >= 400:
                    log.error("telegram error %s", resp.status)
                    return False
                return True


# Functional helper
async def send_message(token: str, chat_id: str, message: str) -> bool:
    notifier = TelegramNotifier(token, chat_id)
    return await notifier.send(message)


__all__ = ["TelegramNotifier", "send_message"]
