"""Simple FastAPI-based web dashboard."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import asyncio
from typing import List, Dict

from ..core.config import Config
from ..core.logger import get_logger
from ..core.callback_manager import MANAGER as CALLBACKS
from .cli import run_scan


app = FastAPI(title="DeathConfuser WebUI")

CONFIG: Config | None = None
SCAN_TASK: asyncio.Task | None = None
RESULTS: List[Dict[str, object]] = []


def _collect_results(task: asyncio.Task) -> None:
    """Safely append scan results when the task completes."""
    try:
        RESULTS.extend(task.result())
    except Exception as exc:  # pragma: no cover - task errors
        get_logger(__name__).error("scan task failed: %s", exc)


@app.get("/")
async def dashboard(request: Request) -> HTMLResponse:
    """Simple dashboard with current status and log tail."""
    if CONFIG and CONFIG.log_file:
        try:
            with open(CONFIG.log_file, "r") as fh:
                lines = fh.readlines()[-20:]
            log_html = "<br>".join(l.strip() for l in lines)
        except FileNotFoundError:
            log_html = ""
    else:
        log_html = ""
    running = SCAN_TASK is not None and not SCAN_TASK.done()
    severity = request.query_params.get("severity")
    callbacks = CALLBACKS.list(severity)
    cb_html = "<br>".join(
        f"<span class='sev-{c.severity}'>{c.severity}: {c.target} ({c.registry})</span>" for c in callbacks
    )
    html = f"""<html><body>
    <h1>DeathConfuser WebUI</h1>
    <p>Running: {running}</p>
    <form method='post' action='/start'>
      <input type='text' name='targets' placeholder='targets file'/>
      <input type='text' name='preset' placeholder='preset'/>
      <input type='text' name='builder' placeholder='builder'/>
      <button type='submit'>Start Scan</button>
    </form>
    <form method='post' action='/stop'>
      <button type='submit'>Stop Scan</button>
    </form>
    <h2>Callbacks</h2>
    <div>{cb_html}</div>
    <pre>{log_html}</pre>
    </body></html>"""
    return HTMLResponse(html)


def run_webui(config: Config) -> None:
    """Run the web interface with Uvicorn."""
    global CONFIG
    CONFIG = config
    logger = get_logger("webui", config.log_file, config.log_level)
    logger.info("Starting WebUI server")
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)


@app.post("/start")
async def start(request: Request) -> RedirectResponse:
    """Start a scan via the dashboard."""
    global SCAN_TASK, RESULTS
    if SCAN_TASK:
        return RedirectResponse("/", status_code=303)
    form = await request.form()
    targets = form.get("targets") or (CONFIG.data.get("targets") if CONFIG else None)
    preset = form.get("preset")
    builder = form.get("builder")
    if preset and CONFIG:
        CONFIG = Config.load(CONFIG.data.get("config_path"), preset)
    if builder and CONFIG:
        CONFIG.data["payload_builder"] = builder
    if not CONFIG or not targets:
        return RedirectResponse("/", status_code=303)
    SCAN_TASK = asyncio.create_task(run_scan(CONFIG, targets))
    SCAN_TASK.add_done_callback(_collect_results)
    return RedirectResponse("/", status_code=303)


@app.post("/stop")
async def stop() -> RedirectResponse:
    global SCAN_TASK
    if SCAN_TASK and not SCAN_TASK.done():
        SCAN_TASK.cancel()
        SCAN_TASK = None
    return RedirectResponse("/", status_code=303)
