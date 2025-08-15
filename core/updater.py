"""Self updating module loader."""
from __future__ import annotations

import asyncio
from pathlib import Path

from .logger import get_logger

log = get_logger(__name__)


class Updater:
    def __init__(self, repo: str | Path) -> None:
        self.repo = Path(repo)

    async def pull(self) -> None:
        """Pretend to pull updates from a git repository."""

        # In tests we simply wait a tick; real implementation would call
        # out to ``git``.
        await asyncio.sleep(0)
        if not (self.repo / ".git").exists():
            log.debug("repo %s is not a git checkout", self.repo)
        else:
            log.info("update checked for %s", self.repo)


__all__ = ["Updater"]
