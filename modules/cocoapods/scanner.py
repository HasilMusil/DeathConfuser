from __future__ import annotations
"""CocoaPods registry search module.

API: https://cocoapods.org/api/v1/pods/{pod}.json
"""
import aiohttp

API_URL = "https://cocoapods.org/api/v1/pods/{name}.json"


async def search_package(package_name: str) -> dict:
    """Query CocoaPods for ``package_name``."""
    result = {"exists": False, "versions": [], "owner": None}
    try:
        async with aiohttp.ClientSession() as session:
            resp = await session.get(API_URL.format(name=package_name), timeout=10)
            if resp.status != 200:
                return result
            data = await resp.json()
            result["exists"] = True
            result["versions"] = data.get("versions", [])
            authors = data.get("authors")
            if isinstance(authors, dict):
                result["owner"] = next(iter(authors.keys()), None)
    except Exception:  # pragma: no cover - network errors
        return result
    return result
