"""Command-line interface for the DeathConfuser framework.

This module exposes a small helper :func:`run_scan` which is re-used by the
API and WebUI implementations.  The CLI supports three modes which may be
selected via ``--mode``:

``cli``  - run a scan directly from the command line and optionally write
           reports.
``api``  - expose a small REST API that can trigger scans.
``web``  - launch a minimal dashboard using FastAPI.
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path
from typing import Optional, List, Dict

if __package__ is None or __package__ == "":  # pragma: no cover - script run
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from DeathConfuser.core.config import Config
from DeathConfuser.core.logger import get_logger
from DeathConfuser.core import init as core_init
from DeathConfuser.core.targets import load_targets
from DeathConfuser.core.recon import Recon
from DeathConfuser.core.concurrency import run_tasks
from DeathConfuser.modules import MODULES, load_module

__all__ = ["main", "run_scan"]


async def run_scan(config: Config, target_file: str) -> List[Dict[str, object]]:
    """Perform a scan of the supplied targets with the given configuration."""

    recon = Recon()
    targets = load_targets(target_file)

    modules = config.data.get("modules", list(MODULES.keys()))
    scanners = {name: load_module(name).Scanner() for name in modules}

    logger = get_logger("scan")

    async def scan(url: str):
        pkgs = await recon.scrape_js(url)
        findings = []
        for pkg in pkgs:
            for mod_name, scanner in scanners.items():
                try:
                    if await scanner.is_unclaimed(pkg):
                        findings.append({"ecosystem": mod_name, "package": pkg})
                except Exception as exc:  # pragma: no cover - network errors
                    logger.debug("%s scanner error: %s", mod_name, exc)
        return {"target": url, "findings": findings}

    tasks = [lambda url=t: scan(url) for t in targets]
    limit = config.data.get("concurrency", {}).get("limit", 10)
    retries = config.data.get("concurrency", {}).get("retries", 1)
    timeout = config.data.get("concurrency", {}).get("timeout", 30)
    return await run_tasks(tasks, limit=limit, retries=retries, timeout=timeout)


def main(argv: Optional[list[str]] = None) -> None:
    """Entry point for the CLI."""
    parser = argparse.ArgumentParser(description="DeathConfuser CLI")
    parser.add_argument("--preset", help="Preset profile name")
    parser.add_argument("--targets", help="File with target URLs")
    parser.add_argument("--output", help="Directory to write reports")
    parser.add_argument(
        "--mode",
        choices=["cli", "api", "web"],
        default="cli",
        help="Run as CLI, API or Web dashboard",
    )
    parser.add_argument("-c", "--config", help="Path to config file")
    args = parser.parse_args(argv)

    config = Config.load(args.config, args.preset)
    core_init(args.config, args.preset)
    logger = get_logger("deathconfuser", config.log_file, config.log_level)
    logger.info("DeathConfuser initialized")


    mode = args.mode

    if mode == "web":
        from .webui import run_webui

        run_webui(config)
    elif mode == "api":
        from .api import run_api

        run_api(config)
    else:
        target_file = args.targets or config.data.get("targets")
        if not target_file:
            parser.error("--targets is required in CLI mode")
        results = asyncio.run(run_scan(config, target_file))
        for res in results:
            if res and res.get("findings"):
                logger.info("Unclaimed packages for %s:", res["target"])
                for f in res["findings"]:
                    logger.info("  [%s] %s", f["ecosystem"], f["package"])

        if args.output:
            from pathlib import Path
            from DeathConfuser.reports import ReportExporter

            exporter = ReportExporter()
            output = exporter.export_all(
                {"results": results, "title": "DeathConfuser Report"},
                Path(args.output),
                "scan",
            )
            for fmt, path in output.items():
                logger.info("Wrote %s report to %s", fmt, path)


if __name__ == "__main__":
    main()
