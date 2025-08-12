from __future__ import annotations
"""CPAN registry search module.

API: https://fastapi.metacpan.org/v1/distribution/{package}
"""
import aiohttp

API_URL = "https://fastapi.metacpan.org/v1/distribution/{name}"


async def search_package(package_name: str) -> dict:
    """Query CPAN for ``package_name``."""
    result = {"exists": False, "versions": [], "owner": None}
    try:
        async with aiohttp.ClientSession() as session:
            resp = await session.get(API_URL.format(name=package_name), timeout=10)
            if resp.status != 200:
                return result
            data = await resp.json()
            result["exists"] = True
            if "version" in data:
                result["versions"] = [data["version"]]
            result["owner"] = data.get("author")
    except Exception:  # pragma: no cover - network errors
        return result
    return result
