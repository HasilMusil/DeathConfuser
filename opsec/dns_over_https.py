"""DNS over HTTPS resolver used for stealth queries.

This resolver hides DNS lookups behind HTTPS requests. It supports both
synchronous and asynchronous queries using either Google's or
Cloudflare's public resolvers. Failures are logged and empty results are
returned so calling code can gracefully handle network restrictions.
"""
from __future__ import annotations

import asyncio
import random
from typing import List, Sequence

import aiohttp

from ..core.logger import get_logger

RESOLVERS: Sequence[str] = (
    "https://dns.google/resolve",
    "https://cloudflare-dns.com/dns-query",
)


async def resolve_async(name: str, record_type: str = "A") -> List[str]:
    """Perform an asynchronous DNS query over HTTPS."""
    log = get_logger(__name__)
    url = random.choice(RESOLVERS)
    params = {"name": name, "type": record_type}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=10) as resp:
                data = await resp.json()
    except Exception as exc:  # pragma: no cover - network errors
        log.warning("DoH query failed: %s", exc)
        return []

    answers = data.get("Answer", [])
    results = [a.get("data") for a in answers if "data" in a]
    log.debug("DoH results for %s: %s", name, results)
    return results


def resolve(name: str, record_type: str = "A") -> List[str]:
    """Synchronous helper to perform a DoH query."""
    try:
        return asyncio.run(resolve_async(name, record_type))
    except RuntimeError:
        # already running in loop
        return []
