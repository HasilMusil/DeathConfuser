"""Stub publisher for CPAN packages."""
from __future__ import annotations

from ...core.logger import get_logger

log = get_logger(__name__)


async def publish(name: str, payload: str, dry_run: bool = True) -> None:
    """Publish the payload to CPAN (placeholder)."""
    if dry_run:
        log.info("[dry-run] would upload %s to CPAN", name)
        return
    log.warning("CPAN publishing not implemented")
