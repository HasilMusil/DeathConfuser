"""Slack notification helper."""

from __future__ import annotations

import asyncio
from typing import Any, Dict, Optional

import aiohttp

from core.logger import get_logger


class SlackNotifier:
    """Send messages to Slack via webhook."""

    def __init__(self, webhook_url: str) -> None:
        self.webhook_url = webhook_url
        self.log = get_logger(__name__)

    async def _post(self, payload: Dict[str, Any]) -> bool:
        async with aiohttp.ClientSession() as session:
            async with session.post(self.webhook_url, json=payload) as resp:
                if resp.status >= 400:
                    self.log.error("Slack error %s", resp.status)
                    return False
                return True

    async def send(self, message: str, *, success: bool = True, extra: Optional[str] = None) -> bool:
        color = "#36a64f" if success else "#ff0000"
        payload = {
            "attachments": [
                {
                    "color": color,
                    "title": "DeathConfuser Alert",
                    "text": message,
                }
            ]
        }
        if extra:
            payload["attachments"][0]["footer"] = extra
        for attempt in range(3):
            if await self._post(payload):
                self.log.debug("Slack message sent: %s", message)
                return True
            await asyncio.sleep(attempt + 1)
        return False
