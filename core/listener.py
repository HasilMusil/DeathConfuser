"""Async callback listener with Interactsh integration."""
from __future__ import annotations

import uuid
from typing import List

from aiohttp import web

from .logger import get_logger


class Listener:
    def __init__(self) -> None:
        self.log = get_logger(__name__)
        self.app = web.Application()
        self.callbacks: List[dict] = []
        self._endpoint: str | None = None

    async def _handle(self, request: web.Request) -> web.Response:
        data = await request.json(content_type=None)
        self.callbacks.append(data)
        self.log.info("callback received: %s", data)
        return web.Response(text="ok")

    async def start(self) -> str:
        token = uuid.uuid4().hex
        self._endpoint = f"/cb/{token}"
        self.app.router.add_post(self._endpoint, self._handle)
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, "127.0.0.1", 0)
        await site.start()
        port = site._server.sockets[0].getsockname()[1]
        url = f"http://127.0.0.1:{port}{self._endpoint}"
        self.log.debug("listener started at %s", url)
        return url
