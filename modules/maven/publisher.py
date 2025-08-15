"""Publish Maven artifacts (simulated)."""
from __future__ import annotations

import asyncio
import random
import shutil
from typing import Optional

from ...core.logger import get_logger
from ...core.concurrency import run_tasks
from .scanner import Scanner
from ...opsec.infra_manager import InfraManager
from ...utils.fs_utils import temporary_directory

log = get_logger(__name__)


async def publish(group: str, artifact: str, payload: str, repository: str = "https://oss.sonatype.org/service/local/staging/deploy/maven2/", dry_run: bool = True) -> None:
    """Publish a Maven artifact using ``mvn`` if unclaimed."""

    scanner = Scanner()
    if not await scanner.is_unclaimed(group, artifact):
        log.info("Artifact %s:%s already exists", group, artifact)
        return

    infra = InfraManager()
    profile = await infra.generate_burner_identity()
    log.info("Using identity %s <%s>", profile.get("name"), profile.get("email"))
    log.debug("UA %s version %s", profile.get("user_agent"), profile.get("version"))
    await asyncio.sleep(profile.get("delay", 0))

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
