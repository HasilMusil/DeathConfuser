from __future__ import annotations
"""RubyGems registry search module.

API: https://rubygems.org/api/v1/gems/{gem}.json
"""
import aiohttp

API_URL = "https://rubygems.org/api/v1/gems/{name}.json"

async def search_package(package_name: str) -> dict:
    """Query RubyGems for ``package_name``."""
    result = {"exists": False, "versions": [], "owner": None}
    try:
        async with aiohttp.ClientSession() as session:
            resp = await session.get(API_URL.format(name=package_name), timeout=10)
            if resp.status != 200:
                return result
            data = await resp.json()
            result["exists"] = True
            result["versions"] = [data.get("version")] if data.get("version") else []
            result["owner"] = data.get("authors")
    except Exception:  # pragma: no cover - network errors
        return result
    return result
