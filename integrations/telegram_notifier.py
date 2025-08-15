"""Simple Telegram notifier."""
from __future__ import annotations

import aiohttp

async def send_message(token: str, chat_id: str, message: str) -> bool:
    async with aiohttp.ClientSession() as session:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        await session.post(url, data={"chat_id": chat_id, "text": message})
        return True
