"""Operational security helpers."""

from __future__ import annotations

import asyncio
import random
from typing import Dict, List, Optional

from ..opsec import load_profiles, is_sandbox

from .logger import get_logger


async def jitter(min_delay: float = 0.1, max_delay: float = 1.0) -> None:
    """Sleep for a random amount of time between ``min_delay`` and ``max_delay``."""

    delay = random.uniform(min_delay, max_delay)
    get_logger(__name__).debug("Sleeping for %.2fs", delay)
    await asyncio.sleep(delay)


def random_identity(profiles: Optional[List[Dict[str, str]]] = None) -> Dict[str, str]:
    """Return a random fake identity profile."""
    profiles = profiles or load_profiles()
    return random.choice(profiles) if profiles else {}


def is_in_sandbox() -> bool:
    """Expose sandbox detection to the core."""
    return is_sandbox()


def apply_identity(headers: Dict[str, str], profile: Dict[str, str]) -> Dict[str, str]:
    """Merge identity profile information into request headers."""

    result = dict(headers)
    for key, value in profile.items():
        low = key.lower()
        if low == "user-agent":
            result["User-Agent"] = value
        elif low in {"name", "email"}:
            result[f"X-{key.title()}"] = value
        elif low.startswith("x-"):
            result[key] = value
    return result

