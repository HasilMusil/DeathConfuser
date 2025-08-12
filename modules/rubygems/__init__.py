"""RubyGems package manager module."""

from .scanner import Scanner


async def search_package(package_name: str) -> dict:
    """Check if a RubyGems package exists."""

    scanner = Scanner()
    exists = not await scanner.is_unclaimed(package_name)
    return {"exists": exists}


__all__ = ["search_package"]

