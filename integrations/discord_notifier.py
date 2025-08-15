"""Simple Discord notifier."""
from __future__ import annotations

import aiohttp

async def send_message(webhook: str, message: str) -> bool:
    async with aiohttp.ClientSession() as session:
        await session.post(webhook, json={"content": message})
        return True
