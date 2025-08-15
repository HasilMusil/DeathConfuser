"""Asynchronous callback listener utilities."""
from __future__ import annotations

import asyncio
from aiohttp import web
from uuid import uuid4
from typing import List, Dict, Any, Tuple

from .logger import get_logger

log = get_logger(__name__)


class Listener:
    """Simple aiohttp based listener.

    It also simulates an Interactsh like service by generating unique
    domains for each run.  The implementation focuses on offering a tiny
    yet fully asynchronous listener suitable for unit tests.
    """

    def __init__(self) -> None:
        self._app = web.Application()
        self._app.router.add_post("/{token}", self._handle)
        self._runner: web.AppRunner | None = None
        self._site: web.TCPSite | None = None
        self.callbacks: List[Dict[str, Any]] = []
        self.domain = f"{uuid4().hex}.interactsh.test"

    async def _handle(self, request: web.Request) -> web.Response:
        data = await request.json()
        self.callbacks.append(data)
        return web.Response(text="ok")

    async def start(self) -> str:
        """Start the listener on an ephemeral port and return base URL."""

        self._runner = web.AppRunner(self._app)
        await self._runner.setup()
        self._site = web.TCPSite(self._runner, "127.0.0.1", 0)
        await self._site.start()
        port = self._site._server.sockets[0].getsockname()[1]  # type: ignore
        url = f"http://127.0.0.1:{port}"
        log.debug("listener started at %s", url)
        return url

    def generate_callback_url(self, base: str) -> Tuple[str, str]:
        token = uuid4().hex
        return f"{base}/{token}", token

    async def stop(self) -> None:
        if self._runner:
            await self._runner.cleanup()
            self._runner = None
            self._site = None


__all__ = ["Listener"]
