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
from DeathConfuser.core.target_feed import update_target_file
from DeathConfuser.core.recon import Recon
from DeathConfuser.core.recon_v2 import ReconEngineV2
from DeathConfuser.core.concurrency import run_tasks
from DeathConfuser.modules import MODULES
from DeathConfuser.modules.detect_registry import detect_registry, get_top_registry

__all__ = ["main", "run_scan"]


async def run_scan(config: Config, target_file: str) -> List[Dict[str, object]]:
    """Perform a scan of the supplied targets with the given configuration."""

    if config.recon.v2_engine:
        recon = ReconEngineV2(config.recon.mode)
    else:
        recon = Recon()
    await update_target_file(target_file)
    targets = load_targets(target_file)

    modules = config.get("modules", list(MODULES.keys()))
    searchers = {name: MODULES[name] for name in modules if name in MODULES}

    logger = get_logger("scan")

    async def scan(url: str):
        pkgs = await recon.scrape_js(url)
        findings = []
        for pkg, context in pkgs:
            # run detection for logging and targeting
            results = detect_registry(context, extension=".js")
            if results:
                detected_name, detected_conf = results[0]
                logger.info(
                    "Detected Registry: %s (confidence: %.2f)",
                    detected_name,
                    detected_conf,
                )
                logger.debug(
                    "[DETECTED] %s → %s (confidence: %.2f)",
                    pkg,
                    detected_name,
                    detected_conf,
                )
            else:
                detected_name, detected_conf = None, 0.0
                logger.info("Detected Registry: unknown (confidence: 0.00)")
                logger.debug(
                    "[DETECTED] %s → unknown (confidence: 0.00)", pkg
                )

            top = get_top_registry(context, extension=".js")
            if top and top[0] in searchers:
                top_reg, confidence = top
                logger.debug("[SCAN] Using targeted registry: %s", top_reg)
                try:
                    res = await searchers[top_reg].search_package(pkg)
                except Exception as exc:  # pragma: no cover - network errors
                    logger.debug("%s search error: %s", top_reg, exc)
                    res = {"exists": True}
                if res.get("exists"):
                    continue
                findings.append({"ecosystem": top_reg, "package": pkg})

                others = {
                    mod_name: mod
                    for mod_name, mod in searchers.items()
                    if mod_name != top_reg
                }
                if others:
                    logger.debug(
                        "[SCAN] %s → fallback scanning: %s",
                        pkg,
                        ", ".join(others.keys()),
                    )
                    results = await asyncio.gather(
                        *[m.search_package(pkg) for m in others.values()],
                        return_exceptions=True,
                    )
                    for (mod_name, res) in zip(others.keys(), results):
                        if isinstance(res, Exception):  # pragma: no cover - network
                            logger.debug("%s search error: %s", mod_name, res)
                        elif not res.get("exists"):
                            findings.append({"ecosystem": mod_name, "package": pkg})
                continue

            # no confident registry or not supported -> scan all registries
            tasks = {
                mod_name: mod.search_package(pkg) for mod_name, mod in searchers.items()
            }
            logger.debug(
                "[SCAN] %s → scanning all registries: %s",
                pkg,
                ", ".join(tasks.keys()),
            )
            results = await asyncio.gather(
                *tasks.values(), return_exceptions=True
            )
            for (mod_name, res) in zip(tasks.keys(), results):
                if isinstance(res, Exception):  # pragma: no cover - network
                    logger.debug("%s search error: %s", mod_name, res)
                elif not res.get("exists"):
                    findings.append({"ecosystem": mod_name, "package": pkg})

        return {"target": url, "findings": findings}

    tasks = [lambda url=t: scan(url) for t in targets]
    limit = config.concurrency.limit
    retries = config.concurrency.retries
    timeout = config.concurrency.timeout
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
    parser.add_argument(
        "--builder",
        choices=["template", "dynamic"],
        default="template",
        help="Payload builder to use",
    )
    parser.add_argument("-c", "--config", help="Path to config file")
    parser.add_argument(
        "--set",
        action="append",
        metavar="KEY=VAL",
        help="Override arbitrary config values",
    )
    args = parser.parse_args(argv)

    overrides = {}
    if args.set:
        for item in args.set:
            if "=" not in item:
                parser.error("--set expects KEY=VAL")
            key, val = item.split("=", 1)
            overrides[key.strip()] = val.strip()

    config = Config.load(args.config, args.preset, overrides)
    core_init(args.config, args.preset)
    logger = get_logger("deathconfuser", config.log_file, config.log_level)
    logger.info("DeathConfuser initialized")
    config["payloads"]["builder"] = args.builder

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
