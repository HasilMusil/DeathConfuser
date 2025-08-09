"""Proxy management utilities."""

from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from typing import Iterable, Iterator, List, Optional

import aiohttp
from aiohttp_socks import ProxyConnector


@dataclass
class ProxyManager:
    """Rotate through HTTP proxies for outgoing requests."""

    proxies: Iterable[str] = field(default_factory=list)
    use_tor: bool = False
    socks_port: int = 9050
    _iterator: Optional[Iterator[str]] = field(init=False, default=None)

    def __post_init__(self) -> None:
        self._iterator = itertools.cycle(self.proxies)

    def get(self) -> Optional[str]:
        """Return the next proxy in the list or ``None`` if none configured."""

        try:
            return next(self._iterator) if self.proxies else None
        except StopIteration:  # pragma: no cover - cycle should not stop
            return None

    def get_chain(self, count: int = 1) -> List[str]:
        """Return a list of proxies to chain."""
        chain = []
        for _ in range(count):
            proxy = self.get()
            if proxy:
                chain.append(proxy)
        return chain

    def add(self, proxy: str) -> None:
        self.proxies = list(self.proxies) + [proxy]
        self._iterator = itertools.cycle(self.proxies)

    def rotate_pool(self, proxies: Iterable[str]) -> None:
        self.proxies = list(proxies)
        self._iterator = itertools.cycle(self.proxies)

    def aiohttp_session(self) -> aiohttp.ClientSession:
        """Return an aiohttp session with the current proxy (and Tor if enabled)."""
        proxy = self.get()
        if self.use_tor:
            connector = ProxyConnector.from_url(f"socks5://127.0.0.1:{self.socks_port}")
        elif proxy and proxy.startswith("socks"):
            connector = ProxyConnector.from_url(proxy)
        else:
            connector = aiohttp.TCPConnector()
        return aiohttp.ClientSession(connector=connector)

