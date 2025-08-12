from __future__ import annotations
"""NPM registry search module.

API: https://registry.npmjs.org/
"""
import aiohttp

API_URL = "https://registry.npmjs.org/{name}"

async def search_package(package_name: str) -> dict:
    """Query the NPM registry for ``package_name``."""
    result = {"exists": False, "versions": [], "owner": None}
    try:
        async with aiohttp.ClientSession() as session:
            resp = await session.get(API_URL.format(name=package_name), timeout=10)
            if resp.status != 200:
                return result
            data = await resp.json()
            result["exists"] = True
            result["versions"] = list(data.get("versions", {}).keys())
            author = data.get("author")
            if isinstance(author, dict):
                result["owner"] = author.get("name")
            elif isinstance(author, str):
                result["owner"] = author
    except Exception:  # pragma: no cover - network errors
        return result
    return result
