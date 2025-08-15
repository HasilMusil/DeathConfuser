"""Manage artifacts like HTTP dumps or screenshots."""
from __future__ import annotations

from pathlib import Path
from typing import Union


class ArtifactManager:
    def __init__(self, base_dir: Union[str, Path] = "artifacts") -> None:
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save_text(self, name: str, content: str) -> Path:
        path = self.base_dir / f"{name}.txt"
        path.write_text(content)
        return path

    def save_binary(self, name: str, data: bytes) -> Path:
        path = self.base_dir / name
        path.write_bytes(data)
        return path


__all__ = ["ArtifactManager"]
