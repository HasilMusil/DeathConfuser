from __future__ import annotations
"""Hackage registry search module.

API: https://hackage.haskell.org/package/{package}/preferred.json
"""
import aiohttp

PREF_URL = "https://hackage.haskell.org/package/{name}/preferred.json"
INFO_URL = "https://hackage.haskell.org/package/{name}/{name}.json"


async def search_package(package_name: str) -> dict:
    """Query Hackage for ``package_name``."""
    result = {"exists": False, "versions": [], "owner": None}
    try:
        async with aiohttp.ClientSession() as session:
            pref = await session.get(PREF_URL.format(name=package_name), timeout=10)
            if pref.status != 200:
                return result
            pref_data = await pref.json()
            versions = pref_data.get("normal-version", [])
            info_resp = await session.get(INFO_URL.format(name=package_name), timeout=10)
            if info_resp.status == 200:
                info = await info_resp.json()
                maintainers = info.get("maintainers", [])
                if maintainers:
                    result["owner"] = maintainers[0]
            result["exists"] = True
            result["versions"] = versions
    except Exception:  # pragma: no cover - network errors
        return result
    return result
