"""Asynchronous callback listener with Interactsh-like integration."""
from __future__ import annotations

from aiohttp import web
from uuid import uuid4
from typing import List, Dict, Any, Tuple

from .logger import get_logger

log = get_logger(__name__)


class Listener:
    """aiohttp-based listener that also simulates an Interactsh-like service.

    - Generates a unique endpoint token per start.
    - Stores received callbacks in memory.
    - Can generate callback URLs and stop gracefully.
    """

    def __init__(self) -> None:
        self._app = web.Application()
        self._runner: web.AppRunner | None = None
        self._site: web.TCPSite | None = None
        self.callbacks: List[Dict[str, Any]] = []
        self._endpoint: str | None = None
        self.domain = f"{uuid4().hex}.interactsh.test"

    async def _handle(self, request: web.Request) -> web.Response:
        """Handle incoming POST callback requests."""
        data = await request.json(content_type=None)
        self.callbacks.append(data)
        log.info("callback received: %s", data)
        return web.Response(text="ok")

    async def start(self) -> str:
        """Start listener on an ephemeral port and return full callback URL."""
        token = uuid4().hex
        self._endpoint = f"/cb/{token}"
        self._app.router.add_post(self._endpoint, self._handle)
        self._runner = web.AppRunner(self._app)
        await self._runner.setup()
        self._site = web.TCPSite(self._runner, "127.0.0.1", 0)
        await self._site.start()
        port = self._site._server.sockets[0].getsockname()[1]  # type: ignore
        url = f"http://127.0.0.1:{port}{self._endpoint}"
        log.debug("listener started at %s", url)
        return url

    def generate_callback_url(self, base: str) -> Tuple[str, str]:
        """Generate a new callback URL and token."""
        token = uuid4().hex
        return f"{base}/{token}", token

    async def stop(self) -> None:
        """Stop the listener and clean up resources."""
        if self._runner:
            await self._runner.cleanup()
            self._runner = None
            self._site = None


__all__ = ["Listener"]
