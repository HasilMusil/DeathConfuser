from __future__ import annotations
"""Maven Central search module.

API: https://search.maven.org/solrsearch/select
"""
import aiohttp

API_URL = "https://search.maven.org/solrsearch/select?q=a:%22{name}%22&rows=20&wt=json"

async def search_package(package_name: str) -> dict:
    """Query Maven Central for ``package_name``."""
    result = {"exists": False, "versions": [], "owner": None}
    try:
        async with aiohttp.ClientSession() as session:
            resp = await session.get(API_URL.format(name=package_name), timeout=10)
            if resp.status != 200:
                return result
            data = await resp.json()
            docs = data.get("response", {}).get("docs", [])
            if not docs:
                return result
            result["exists"] = True
            result["versions"] = [doc.get("latestVersion") for doc in docs if doc.get("latestVersion")]
    except Exception:  # pragma: no cover - network errors
        return result
    return result
