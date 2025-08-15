"""Stub publisher for CPAN packages."""
from __future__ import annotations

from ...core.logger import get_logger
from ...core.concurrency import run_tasks

log = get_logger(__name__)


async def publish(name: str, payload: str, dry_run: bool = True) -> None:
    """Publish the payload to CPAN (placeholder)."""
    if dry_run:
        log.info("[dry-run] would upload %s to CPAN", name)
        return
    log.warning("CPAN publishing not implemented")


async def publish_parallel(packages, limit=5, retries=3, **kwargs):
    async def _single(pkg):
        name, payload = pkg
        backoff = 1
        for _ in range(retries+1):
            try:
                await publish(name, payload, **kwargs)
                break
            except Exception:  # pragma: no cover - network errors
                await asyncio.sleep(backoff)
                backoff *= 2
    coros = [lambda p=p: _single(p) for p in packages]
    await run_tasks(coros, limit=limit)
