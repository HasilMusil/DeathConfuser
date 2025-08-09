"""Simple webhook pinger used for notifications and callbacks."""

from __future__ import annotations

import asyncio
from typing import Any, Dict, Iterable, Optional

import aiohttp

from core.logger import get_logger


async def _post(session: aiohttp.ClientSession, url: str, payload: Dict[str, Any], headers: Optional[Dict[str, str]], retries: int) -> int:
    log = get_logger(__name__)
    for attempt in range(1, retries + 1):
        try:
            async with session.post(url, json=payload, headers=headers) as resp:
                log.debug("Webhook %s responded with %s", url, resp.status)
                return resp.status
        except Exception as exc:  # pragma: no cover - network errors
            log.error("Webhook error (%s) %s: %s", attempt, url, exc)
            await asyncio.sleep(attempt)
    return -1


async def send(url: str, payload: Dict[str, Any], headers: Optional[Dict[str, str]] = None, retries: int = 3) -> int:
    """POST the payload to a webhook URL and return the HTTP status."""
    async with aiohttp.ClientSession() as session:
        return await _post(session, url, payload, headers, retries)


async def broadcast(urls: Iterable[str], payload: Dict[str, Any], headers: Optional[Dict[str, str]] = None, retries: int = 3) -> Dict[str, int]:
    """Send the payload to all ``urls`` and return a mapping of status codes."""
    results: Dict[str, int] = {}
    async with aiohttp.ClientSession() as session:
        for url in urls:
            results[url] = await _post(session, url, payload, headers, retries)
    return results
