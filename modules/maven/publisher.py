"""Publish Maven artifacts (simulated)."""
from __future__ import annotations

import asyncio
import random
import shutil
from typing import Optional

from ...core.logger import get_logger
from .scanner import Scanner
from ...opsec import load_profiles
from ...utils.fs_utils import temporary_directory

log = get_logger(__name__)


async def publish(group: str, artifact: str, payload: str, repository: str = "https://oss.sonatype.org/service/local/staging/deploy/maven2/", dry_run: bool = True) -> None:
    """Publish a Maven artifact using ``mvn`` if unclaimed."""

    scanner = Scanner()
    if not await scanner.is_unclaimed(group, artifact):
        log.info("Artifact %s:%s already exists", group, artifact)
        return

    profile = random.choice(load_profiles()) if load_profiles() else {"name": "test", "email": "test@example.com"}
    log.info("Using identity %s <%s>", profile.get("name"), profile.get("email"))

    if dry_run or not shutil.which("mvn"):
        log.info("[dry-run] would deploy %s:%s", group, artifact)
        return

    with temporary_directory("mvn") as tmp:
        (tmp / "pom.xml").write_text(payload)
        proc = await asyncio.create_subprocess_exec(
            "mvn",
            "deploy:deploy-file",
            f"-Durl={repository}",
            f"-DgroupId={group}",
            f"-DartifactId={artifact}",
            "-Dversion=0.0.1",
            "-Dpackaging=pom",
            f"-Dfile={tmp/'pom.xml'}",
            cwd=str(tmp),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        _, err = await proc.communicate()
        if proc.returncode == 0:
            log.info("Deployed %s:%s", group, artifact)
        else:
            log.error("mvn deploy failed: %s", err.decode().strip())
