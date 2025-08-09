"""Target parsing utilities."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Set

import ipaddress
import socket
from urllib.parse import urlparse


def load_targets(file_path: str | Path) -> List[str]:
    """Load newline-separated targets from a file."""

    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(file_path)

    targets: Set[str] = set()
    with path.open("r") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            targets.update(normalize_target(line))

    return sorted(targets)


def normalize_target(target: str) -> List[str]:
    """Normalize a target string into one or more URLs."""

    if target.startswith("http"):
        parsed = urlparse(target)
        host = parsed.hostname or target
    else:
        host = target
        parsed = None

    # wildcard handling
    if host.startswith("*."):
        host = host[2:]

    urls: List[str] = []

    # attempt to expand CIDR ranges
    try:
        net = ipaddress.ip_network(host, strict=False)
        for ip in net.hosts():
            urls.append(f"http://{ip}")
        return urls
    except ValueError:
        pass

    # resolve hostname
    try:
        ip = socket.gethostbyname(host)
        urls.append(f"http://{ip}")
    except socket.gaierror:
        pass

    if parsed:
        urls.append(target)
    else:
        urls.append(f"http://{host}")

    return urls

