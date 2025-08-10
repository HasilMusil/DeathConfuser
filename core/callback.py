"""Callback server and client handlers."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import aiohttp

from ..opsec.dns_over_https import resolve

from aiohttp import web

from .logger import get_logger


@dataclass
class CallbackServer:
    """Minimal HTTP callback server to collect events."""

    host: str = "0.0.0.0"
    port: int = 8000
    _app: web.Application = field(init=False)
    _runner: web.AppRunner = field(init=False)
    events: List[Dict] = field(default_factory=list)

    def __post_init__(self) -> None:
        self._app = web.Application()
        self._app.add_routes([web.post("/", self._handle)])
        self._runner = web.AppRunner(self._app)

    async def _handle(self, request: web.Request) -> web.Response:
        data = await request.json()
        get_logger(__name__).debug("callback received: %s", data)
        self.events.append(data)
        return web.Response(text="ok")

    async def start(self) -> None:
        await self._runner.setup()
        site = web.TCPSite(self._runner, self.host, self.port)
        await site.start()

    async def stop(self) -> None:
        await self._runner.cleanup()


@dataclass
class CallbackClient:
    """Helper to send callbacks via HTTP, DNS or collaborator."""

    http_url: Optional[str] = None
    dns_domain: Optional[str] = None
    interact_url: Optional[str] = None
    burp_collaborator: Optional[str] = None

    async def http(self, data: Dict[str, str]) -> None:
        if not self.http_url:
            return
        async with aiohttp.ClientSession() as session:
            try:
                await session.post(self.http_url, json=data, timeout=10)
            except Exception as exc:  # pragma: no cover - network
                get_logger(__name__).debug("HTTP callback failed: %s", exc)

            if self.interact_url:
                try:
                    await session.post(self.interact_url, json=data, timeout=10)
                except Exception as exc:  # pragma: no cover - network
                    get_logger(__name__).debug("Interactsh callback failed: %s", exc)

            if self.burp_collaborator:
                try:
                    await session.post(self.burp_collaborator, json=data, timeout=10)
                except Exception as exc:  # pragma: no cover - network
                    get_logger(__name__).debug("Burp callback failed: %s", exc)

    async def dns(self, token: str) -> None:
        if not self.dns_domain:
            return
        domain = f"{token}.{self.dns_domain}"
        _ = resolve(domain)

    async def trigger(self, data: Dict[str, str]) -> None:
        await asyncio.gather(
            self.http(data),
            self.dns(data.get("id", "")),
        )

