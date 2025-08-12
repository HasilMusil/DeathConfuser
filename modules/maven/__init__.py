"""Maven package manager module."""

from .scanner import Scanner


async def search_package(package_name: str) -> dict:
    """Check if a Maven artifact exists."""

    scanner = Scanner()
    if ":" in package_name:
        group, artifact = package_name.split(":", 1)
    elif "/" in package_name:
        group, artifact = package_name.split("/", 1)
    else:
        group, artifact = "", package_name
    exists = not await scanner.is_unclaimed(group, artifact)
    return {"exists": exists}


__all__ = ["search_package"]

