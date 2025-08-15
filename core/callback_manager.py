"""Manage callbacks received from deployed payloads."""
from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Optional

from .logger import get_logger
from .ml import classify_callback_severity

log = get_logger(__name__)


@dataclass
class CallbackEvent:
    target: str
    registry: str
    program: str
    severity: str
    data: dict


class CallbackManager:
    """Keep track of callback events and persist them."""

    def __init__(self, storage_dir: Path | str = Path("reports/json")) -> None:
        self.storage_dir = Path(storage_dir)
        self.events: List[CallbackEvent] = []
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def record(
        self,
        target: str,
        registry: str,
        program: str,
        severity: Optional[str] = None,
        data: Optional[dict] = None,
    ) -> None:
        data = data or {}
        if severity is None:
            severity = classify_callback_severity(data)
        event = CallbackEvent(target, registry, program, severity, data)
        self.events.append(event)
        log.info("callback from %s via %s", target, registry)
        self.save()

    def list(self, severity: Optional[str] = None) -> List[CallbackEvent]:
        if severity:
            return [e for e in self.events if e.severity == severity]
        return list(self.events)

    def save(self) -> Path:
        path = self.storage_dir / "callbacks.json"
        with path.open("w") as fh:
            json.dump([asdict(e) for e in self.events], fh, indent=2)
        return path


# default global instance used by interfaces
MANAGER = CallbackManager()
