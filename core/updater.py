"""Self-updating modules from a Git repository or local loader."""
from __future__ import annotations

import asyncio
from pathlib import Path
from .logger import get_logger

log = get_logger(__name__)


async def update_modules(repo_url: str, dest: Path | str = Path("modules")) -> bool:
    """Functional updater using `git pull`."""
    dest = Path(dest)
    proc = await asyncio.create_subprocess_exec(
        "git", "pull", repo_url,
        cwd=str(dest),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    await proc.communicate()
    return proc.returncode == 0


class Updater:
    """Class-based updater for easier testing or mocking."""
    def __init__(self, repo: str | Path) -> None:
        self.repo = Path(repo)

    async def pull(self) -> None:
        # In tests we just simulate a pull
        await asyncio.sleep(0)
        if not (self.repo / ".git").exists():
            log.debug("repo %s is not a git checkout", self.repo)
        else:
            log.info("update checked for %s", self.repo)


__all__ = ["update_modules", "Updater"]
