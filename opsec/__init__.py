"""OPSEC utilities for DeathConfuser."""
from __future__ import annotations

from pathlib import Path
from typing import List, Dict

import yaml

from .dns_over_https import resolve
from .proxy_rotator import ProxyRotator
from .infra_manager import InfraManager
from .sandbox_detector import is_sandbox, is_sandboxed

__all__ = [
    "load_profiles",
    "ProxyRotator",
    "InfraManager",
    "resolve",
    "is_sandbox",
    "is_sandboxed",
]

PROFILE_FILE = Path(__file__).with_name("burner_profiles.yaml")


def load_profiles(path: Path = PROFILE_FILE) -> List[Dict[str, str]]:
    """Load burner identity profiles from the bundled YAML file."""
    if not path.exists():
        return []
    with path.open("r") as f:
        data = yaml.safe_load(f) or {}
    return data.get("profiles", [])
