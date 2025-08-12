from __future__ import annotations
"""NuGet registry search module.

API: https://api.nuget.org/v3/registration5-semver1/{package}/index.json
"""
import aiohttp

API_URL = "https://api.nuget.org/v3/registration5-semver1/{name}/index.json"

async def search_package(package_name: str) -> dict:
    """Query NuGet for ``package_name``."""
    result = {"exists": False, "versions": [], "owner": None}
    try:
        async with aiohttp.ClientSession() as session:
            resp = await session.get(API_URL.format(name=package_name.lower()), timeout=10)
            if resp.status != 200:
                return result
            data = await resp.json()
            result["exists"] = True
            versions = []
            for item in data.get("items", []):
                for release in item.get("items", []):
                    ver = release.get("catalogEntry", {}).get("version")
                    if ver:
                        versions.append(ver)
            result["versions"] = versions
            # owners often stored in catalogEntry["owners"] as comma-separated
            for item in data.get("items", []):
                for release in item.get("items", []):
                    owners = release.get("catalogEntry", {}).get("owners")
                    if owners:
                        result["owner"] = owners.split(",")[0].strip()
                        break
                if result["owner"]:
                    break
    except Exception:  # pragma: no cover - network errors
        return result
    return result
