from __future__ import annotations
"""Go module proxy search module.

API: https://proxy.golang.org/{module}/@v/list
"""
import aiohttp

API_URL = "https://proxy.golang.org/{name}/@v/list"

async def search_package(package_name: str) -> dict:
    """Query the Go module proxy for ``package_name``."""
    result = {"exists": False, "versions": [], "owner": None}
    try:
        async with aiohttp.ClientSession() as session:
            resp = await session.get(API_URL.format(name=package_name), timeout=10)
            if resp.status != 200:
                return result
            text = await resp.text()
            versions = [v for v in text.splitlines() if v]
            if versions:
                result["exists"] = True
                result["versions"] = versions
    except Exception:  # pragma: no cover - network errors
        return result
    return result
