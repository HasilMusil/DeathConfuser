from __future__ import annotations
"""PyPI registry search module.

API: https://pypi.org/pypi/{package}/json
"""
import aiohttp

API_URL = "https://pypi.org/pypi/{name}/json"

async def search_package(package_name: str) -> dict:
    """Query the PyPI registry for ``package_name``."""
    result = {"exists": False, "versions": [], "owner": None}
    try:
        async with aiohttp.ClientSession() as session:
            resp = await session.get(API_URL.format(name=package_name), timeout=10)
            if resp.status != 200:
                return result
            data = await resp.json()
            result["exists"] = True
            result["versions"] = list(data.get("releases", {}).keys())
            info = data.get("info", {})
            result["owner"] = info.get("author") or info.get("maintainer")
    except Exception:  # pragma: no cover - network errors
        return result
    return result
