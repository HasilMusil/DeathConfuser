"""Discord webhook notifications."""
from __future__ import annotations

import aiohttp
import asyncio
from typing import Dict, Any

from ..core.logger import get_logger

log = get_logger(__name__)


class DiscordNotifier:
    def __init__(self, webhook_url: str) -> None:
        self.webhook_url = webhook_url

    async def send(self, content: str) -> bool:
        payload: Dict[str, Any] = {"content": content}
        async with aiohttp.ClientSession() as session:
            async with session.post(self.webhook_url, json=payload) as resp:
                if resp.status >= 400:
                    log.error("discord error %s", resp.status)
                    return False
                return True
