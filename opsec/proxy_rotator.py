"""Proxy rotation utilities for OPSEC simulations.

This component supports HTTP/SOCKS proxies, Tor integration via the
``stem`` library, and optional chaining of proxies. Rotation strategies
can be interval based or on every request/target. All operations are
non-blocking and errors are logged rather than raised.
"""
from __future__ import annotations

import asyncio
import random
from pathlib import Path
from typing import Dict, Iterable, List, Optional

try:
    from stem import Signal
    from stem.control import Controller
except Exception:  # pragma: no cover - optional dependency may be missing
    Controller = None
    Signal = None

from core.logger import get_logger


class ProxyRotator:
    """Rotate through a list of proxies with optional Tor support."""

    def __init__(
        self,
        proxies: Iterable[str] | None = None,
        interval: int = 60,
        per_request: bool = False,
        per_target: bool = False,
        use_tor: bool = False,
    ) -> None:
        self.proxies: List[str] = list(proxies or [])
        self.interval = interval
        self.per_request = per_request
        self.per_target = per_target
        self.use_tor = use_tor

        self.current: Optional[str] = None
        self.target_map: Dict[str, str] = {}
        self.chain: List[str] = []

        self.log = get_logger(__name__)
        self._task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        """Begin rotating proxies asynchronously."""
        if self._task:
            return
        self._task = asyncio.create_task(self._rotate_loop())

    async def stop(self) -> None:
        """Stop rotation tasks."""
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:  # pragma: no cover - expected
                pass
            self._task = None

    async def _rotate_loop(self) -> None:
        """Background loop to rotate proxies."""
        while True:
            await self.rotate()
            await asyncio.sleep(self.interval)

    async def rotate(self) -> None:
        """Select a new proxy at random and optionally renew Tor."""
        if self.proxies:
            self.current = random.choice(self.proxies)
            self.log.debug("Rotated proxy to %s", self.current)
        else:
            self.current = None

        if self.use_tor and Controller is not None:
            try:
                with Controller.from_port(port=9051) as c:
                    c.authenticate()
                    c.signal(Signal.NEWNYM)
                    self.log.debug("Requested new Tor circuit")
                if "socks5://127.0.0.1:9050" not in self.chain:
                    self.chain.insert(0, "socks5://127.0.0.1:9050")
            except Exception as exc:  # pragma: no cover - optional
                self.log.warning("Tor rotation failed: %s", exc)

    def get(self, target: str | None = None) -> Optional[str]:
        """Return a proxy for the given target, rotating if necessary."""
        if self.per_request:
            asyncio.create_task(self.rotate())
        elif self.per_target and target:
            if target not in self.target_map:
                self.target_map[target] = random.choice(self.proxies) if self.proxies else None
            return self.target_map[target]
        return self.current

    def add(self, proxy: str) -> None:
        """Add a proxy to the rotation list."""
        self.proxies.append(proxy)
        self.log.debug("Added proxy %s", proxy)

    def chain_proxy(self, proxy: str) -> None:
        """Add a proxy to the chaining list."""
        self.chain.append(proxy)
        self.log.debug("Chained proxy %s", proxy)

    def all_proxies(self) -> List[str]:
        """Return the current proxy chain."""
        chain = list(self.chain)
        if self.current:
            chain.append(self.current)
        return chain

    @classmethod
    def from_file(cls, path: str, **kwargs) -> "ProxyRotator":
        """Create a rotator from a file containing proxy URLs."""
        proxies: List[str] = []
        try:
            for line in Path(path).read_text().splitlines():
                line = line.strip()
                if line:
                    proxies.append(line)
        except Exception as exc:  # pragma: no cover - file errors
            get_logger(__name__).error("Failed to load proxies: %s", exc)
        return cls(proxies, **kwargs)

    def mark_bad(self, proxy: str) -> None:
        """Remove a proxy temporarily when a timeout occurs."""
        if proxy in self.proxies:
            self.proxies.remove(proxy)
            self.log.debug("Removed failing proxy %s", proxy)
