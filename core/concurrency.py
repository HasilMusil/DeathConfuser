"""Asynchronous concurrency helpers."""

from __future__ import annotations

import asyncio
import random
from typing import Awaitable, Callable, Iterable, List, Tuple

from .logger import get_logger


async def run_tasks(
    coros: Iterable[Callable[[], Awaitable]],
    limit: int = 10,
    retries: int = 2,
    timeout: int = 30,
    jitter: Tuple[float, float] = (0.0, 0.0),
) -> List:
    """Run coroutines with concurrency limits, retry and jitter."""

    semaphore = asyncio.Semaphore(limit)
    results: List = []
    log = get_logger(__name__)

    async def worker(coro_func: Callable[[], Awaitable]) -> None:
        attempt = 0
        while attempt <= retries:
            try:
                async with semaphore:
                    result = await asyncio.wait_for(coro_func(), timeout=timeout)
                results.append(result)
                return
            except Exception as exc:  # pragma: no cover - network/backoff errors
                attempt += 1
                log.debug("Task failed (attempt %s/%s): %s", attempt, retries, exc)
                delay = attempt + random.uniform(*jitter)
                await asyncio.sleep(delay)

    await asyncio.gather(*(worker(c) for c in coros))
    return results

