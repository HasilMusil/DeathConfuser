"""REST API mode for DeathConfuser."""

from __future__ import annotations

from fastapi import FastAPI, Request
import asyncio
from typing import List, Dict

from core.config import Config
from core.logger import get_logger
from .cli import run_scan

api = FastAPI(title="DeathConfuser API")

CONFIG: Config | None = None
SCAN_TASK: asyncio.Task | None = None
RESULTS: List[Dict[str, object]] = []


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
    SCAN_TASK.add_done_callback(lambda t: RESULTS.extend(t.result()))
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
    return {"running": str(running), "results": str(len(RESULTS))}


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
