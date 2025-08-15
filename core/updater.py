"""Self-updating modules from a Git repository."""
from __future__ import annotations

import asyncio
import subprocess
from pathlib import Path


async def update_modules(repo_url: str, dest: Path | str = Path("modules")) -> bool:
    dest = Path(dest)
    proc = await asyncio.create_subprocess_exec(
        "git", "pull", repo_url,
        cwd=str(dest),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    await proc.communicate()
    return proc.returncode == 0
