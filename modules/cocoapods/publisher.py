"""Stub publisher for CocoaPods."""
from __future__ import annotations

from ...core.logger import get_logger

log = get_logger(__name__)


async def publish(name: str, payload: str, dry_run: bool = True) -> None:
    """Publish the payload to CocoaPods (placeholder)."""
    if dry_run:
        log.info("[dry-run] would upload %s to CocoaPods", name)
        return
    log.warning("CocoaPods publishing not implemented")
