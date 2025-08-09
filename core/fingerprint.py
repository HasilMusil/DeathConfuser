"""Technology fingerprinting helpers."""

from __future__ import annotations

import re
from typing import Dict, Set

from urllib.parse import urljoin

import requests

from .logger import get_logger

SERVER_RE = re.compile(r"server:(.*)", re.I)
POWERED_RE = re.compile(r"x-powered-by:(.*)", re.I)


def fingerprint_url(url: str) -> Set[str]:
    """Return a set of technology hints extracted from a URL."""

    log = get_logger(__name__)
    try:
        response = requests.get(url, timeout=10)
    except requests.RequestException as exc:  # pragma: no cover - network errors
        log.debug(f"fingerprint failed for %s: %s", url, exc)
        return set()

    hints: Set[str] = set()
    for header, value in response.headers.items():
        header_line = f"{header}:{value}".lower()
        m = SERVER_RE.match(header_line) or POWERED_RE.match(header_line)
        if m:
            hints.add(m.group(1).strip())
        if header.lower() == "set-cookie":
            if "wordpress" in value.lower():
                hints.add("wordpress")
            if "sessionid" in value.lower():
                hints.add("django")

    body = response.text.lower()
    if "wordpress" in body:
        hints.add("wordpress")
    if "django" in body:
        hints.add("django")
    if "react" in body:
        hints.add("react")

    # attempt to infer package manager registry
    try:
        pkg_resp = requests.get(urljoin(url, "package.json"), timeout=5)
        if pkg_resp.status_code < 300:
            hints.add("npm")
    except Exception:
        pass
    try:
        if requests.get(urljoin(url, "setup.py"), timeout=5).status_code < 300:
            hints.add("pypi")
    except Exception:
        pass

    return hints
