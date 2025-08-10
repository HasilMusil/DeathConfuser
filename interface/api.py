"""REST API mode for DeathConfuser."""

from __future__ import annotations

from fastapi import FastAPI, Request
import asyncio
import sys
from pathlib import Path
from typing import List, Dict

if __package__ is None or __package__ == "":  # pragma: no cover - script run
    sys.path.append(str(Path(__file__).resolve().parents[2]))
    from DeathConfuser.core.config import Config
    from DeathConfuser.core.logger import get_logger
    from DeathConfuser.interface.cli import run_scan
else:  # pragma: no cover - imported as package
    from DeathConfuser.core.config import Config
    from DeathConfuser.core.logger import get_logger
    from .cli import run_scan

api = FastAPI(title="DeathConfuser API")

CONFIG: Config | None = None
SCAN_TASK: asyncio.Task | None = None
RESULTS: List[Dict[str, object]] = []


def _collect_results(task: asyncio.Task) -> None:
    """Safely gather results from a completed scan task."""
    try:
        RESULTS.extend(task.result())
    except Exception as exc:  # pragma: no cover - task errors
        get_logger(__name__).error("scan task failed: %s", exc)


@api.post("/start")
async def start(request: Request) -> Dict[str, str]:
    """Begin a scan based on posted targets and optional preset."""
    global SCAN_TASK, CONFIG, RESULTS
    if SCAN_TASK:
        return {"status": "running"}
    data = await request.json()
    targets = data.get("targets")
    preset = data.get("preset")
    if preset and CONFIG:
        CONFIG = Config.load(CONFIG.data.get("config_path"), preset)
    if not targets:
        targets = CONFIG.data.get("targets") if CONFIG else None
    if not CONFIG or not targets:
        return {"status": "error", "detail": "no targets"}
    SCAN_TASK = asyncio.create_task(run_scan(CONFIG, targets))
    SCAN_TASK.add_done_callback(_collect_results)
    return {"status": "started"}


@api.post("/stop")
async def stop() -> Dict[str, str]:
    """Stop the running scan if any."""
    global SCAN_TASK
    if SCAN_TASK and not SCAN_TASK.done():
        SCAN_TASK.cancel()
        SCAN_TASK = None
        return {"status": "stopped"}
    return {"status": "idle"}


@api.get("/status")
async def status() -> Dict[str, str]:
    running = SCAN_TASK is not None and not SCAN_TASK.done()
    return {"running": running, "results": len(RESULTS)}


@api.get("/results")
async def results() -> Dict[str, List[Dict[str, object]]]:
    return {"results": RESULTS}


def run_api(config: Config) -> None:
    """Launch the API server."""
    global CONFIG
    CONFIG = config
    logger = get_logger("api", config.log_file, config.log_level)
    logger.info("Starting API server")
    import uvicorn

    uvicorn.run(api, host="0.0.0.0", port=8081)
