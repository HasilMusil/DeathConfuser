from __future__ import annotations
"""Conda (Anaconda) registry search module.

API: https://api.anaconda.org/
"""
import aiohttp

SEARCH_URL = "https://api.anaconda.org/search?q={name}"
PACKAGE_URL = "https://api.anaconda.org/package/{owner}/{name}"


async def search_package(package_name: str) -> dict:
    """Query the Anaconda registry for ``package_name``."""
    result = {"exists": False, "versions": [], "owner": None}
    try:
        async with aiohttp.ClientSession() as session:
            search = await session.get(SEARCH_URL.format(name=package_name), timeout=10)
            if search.status != 200:
                return result
            data = await search.json()
            for pkg in data:
                if pkg.get("name") == package_name:
                    owner = pkg.get("owner")
                    result["owner"] = owner
                    info = await session.get(
                        PACKAGE_URL.format(owner=owner, name=package_name), timeout=10
                    )
                    if info.status == 200:
                        pdata = await info.json()
                        result["versions"] = pdata.get("versions", [])
                    result["exists"] = True
                    break
    except Exception:  # pragma: no cover - network errors
        return result
    return result
