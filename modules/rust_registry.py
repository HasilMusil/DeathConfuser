from __future__ import annotations
"""crates.io registry search module.

API: https://crates.io/api/v1/crates/{crate}
"""
import aiohttp

API_URL = "https://crates.io/api/v1/crates/{name}"

async def search_package(package_name: str) -> dict:
    """Query crates.io for ``package_name``."""
    result = {"exists": False, "versions": [], "owner": None}
    try:
        async with aiohttp.ClientSession() as session:
            resp = await session.get(API_URL.format(name=package_name), timeout=10)
            if resp.status != 200:
                return result
            data = await resp.json()
            crate = data.get("crate", {})
            result["exists"] = True
            result["versions"] = [v.get("num") for v in data.get("versions", []) if v.get("num")]
            owners = data.get("owners", [])
            if owners:
                result["owner"] = owners[0].get("login") or owners[0].get("name")
    except Exception:  # pragma: no cover - network errors
        return result
    return result
