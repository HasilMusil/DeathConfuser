"""Local listener for simulation mode."""
from __future__ import annotations

from aiohttp import web

async def run_listener(port: int = 0) -> str:
    async def handle(request: web.Request) -> web.Response:
        return web.Response(text="ok")
    app = web.Application()
    app.router.add_post("/cb", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", port)
    await site.start()
    port = site._server.sockets[0].getsockname()[1]
    return f"http://127.0.0.1:{port}/cb"
