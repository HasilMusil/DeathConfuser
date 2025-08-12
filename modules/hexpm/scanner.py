from __future__ import annotations
"""Hex.pm registry search module.

API: https://hex.pm/api/packages/{package}
"""
import aiohttp

API_URL = "https://hex.pm/api/packages/{name}"


async def search_package(package_name: str) -> dict:
    """Query Hex.pm for ``package_name``."""
    result = {"exists": False, "versions": [], "owner": None}
    try:
        async with aiohttp.ClientSession() as session:
            resp = await session.get(API_URL.format(name=package_name), timeout=10)
            if resp.status != 200:
                return result
            data = await resp.json()
            result["exists"] = True
            result["versions"] = [r.get("version") for r in data.get("releases", []) if r.get("version")]
            maintainers = data.get("meta", {}).get("maintainers", [])
            if maintainers:
                result["owner"] = maintainers[0]
    except Exception:  # pragma: no cover - network errors
        return result
    return result
