"""Manage artifacts like HTTP dumps or screenshots."""
from __future__ import annotations

from pathlib import Path


class ArtifactManager:
    def __init__(self, base: Path | str = Path("artifacts")) -> None:
        self.base = Path(base)
        self.base.mkdir(parents=True, exist_ok=True)

    def save_text(self, name: str, content: str) -> Path:
        path = self.base / f"{name}.txt"
        path.write_text(content)
        return path

    def save_binary(self, name: str, data: bytes) -> Path:
        path = self.base / name
        path.write_bytes(data)
        return path
