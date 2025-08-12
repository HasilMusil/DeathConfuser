from __future__ import annotations
"""Meteor package registry search module.

API: https://atmospherejs.com/a/packages?search={package}
"""
import aiohttp

API_URL = "https://atmospherejs.com/a/packages?search={name}"


async def search_package(package_name: str) -> dict:
    """Search Atmosphere (Meteor) for ``package_name``."""
    result = {"exists": False, "versions": [], "owner": None}
    try:
        async with aiohttp.ClientSession() as session:
            resp = await session.get(API_URL.format(name=package_name), timeout=10)
            if resp.status != 200:
                return result
            data = await resp.json()
            for pkg in data.get("packages", []):
                if pkg.get("name", "").lower() == package_name.lower():
                    result["exists"] = True
                    result["owner"] = pkg.get("maintainer")
                    result["versions"] = pkg.get("versions", [])
                    break
    except Exception:  # pragma: no cover - network errors
        return result
    return result
