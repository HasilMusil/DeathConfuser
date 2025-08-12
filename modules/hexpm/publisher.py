"""Stub publisher for Hex.pm packages."""
from __future__ import annotations

from ...core.logger import get_logger

log = get_logger(__name__)


async def publish(name: str, payload: str, dry_run: bool = True) -> None:
    """Publish the payload to Hex.pm (placeholder)."""
    if dry_run:
        log.info("[dry-run] would upload %s to Hex.pm", name)
        return
    log.warning("Hex.pm publishing not implemented")
