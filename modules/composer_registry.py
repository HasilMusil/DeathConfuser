from __future__ import annotations
"""Packagist registry search module.

API: https://packagist.org/packages/{package}.json
"""
import aiohttp

API_URL = "https://packagist.org/packages/{name}.json"

async def search_package(package_name: str) -> dict:
    """Query Packagist for ``package_name``."""
    result = {"exists": False, "versions": [], "owner": None}
    try:
        async with aiohttp.ClientSession() as session:
            resp = await session.get(API_URL.format(name=package_name), timeout=10)
            if resp.status != 200:
                return result
            data = await resp.json()
            package = data.get("package", {})
            result["exists"] = True
            result["versions"] = list(package.get("versions", {}).keys())
            maintainers = package.get("maintainers", [])
            if maintainers:
                result["owner"] = maintainers[0].get("name")
    except Exception:  # pragma: no cover - network errors
        return result
    return result
