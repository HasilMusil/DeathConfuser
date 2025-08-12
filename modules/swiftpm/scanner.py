from __future__ import annotations
"""Swift Package Index search module.

API: https://swiftpackageindex.com/api/search?query={package}
"""
import aiohttp

API_URL = "https://swiftpackageindex.com/api/search?query={name}"


async def search_package(package_name: str) -> dict:
    """Query the Swift Package Index for ``package_name``."""
    result = {"exists": False, "versions": [], "owner": None}
    try:
        async with aiohttp.ClientSession() as session:
            resp = await session.get(API_URL.format(name=package_name), timeout=10)
            if resp.status != 200:
                return result
            data = await resp.json()
            packages = data.get("results", [])
            for pkg in packages:
                if pkg.get("package_name", "").lower() == package_name.lower():
                    result["exists"] = True
                    result["owner"] = pkg.get("repository_owner")
                    break
    except Exception:  # pragma: no cover - network errors
        return result
    return result
