"""Simple sandbox detection helpers.

These heuristics attempt to detect whether the code is running inside a
virtual machine, debugger or known sandbox environment. The goal is to
allow payloads or high risk operations to abort when indicators are
present, reducing unintentional exposure during research.
"""
from __future__ import annotations

import os
import subprocess
from typing import List

from ..core.logger import get_logger


def check_indicators() -> List[str]:
    """Return a list of detected sandbox indicators."""
    indicators: List[str] = []
    # environment variables commonly set in CI or containers
    for var in ("CI", "BUILD_ID", "CONTAINER", "DOTCI"):
        if os.getenv(var):
            indicators.append(var)

    # docker
    if os.path.exists("/.dockerenv") or os.path.exists("/run/.containerenv"):
        indicators.append("docker")

    # virtualization strings
    product_name = ""
    try:
        with open("/sys/class/dmi/id/product_name") as fh:
            product_name = fh.read().strip().lower()
    except FileNotFoundError:
        pass
    if any(x in product_name for x in ("virtualbox", "vmware", "kvm")):
        indicators.append(product_name)

    # common sandbox processes
    try:
        output = subprocess.check_output(["ps", "aux"], text=True)
        if any(p in output.lower() for p in ("vboxservice", "xenstore", "vmsrvr")):
            indicators.append("vm-process")
    except Exception:
        pass

    # debugger presence
    if os.getenv("PYTHONINSPECT"):
        indicators.append("debugger")

    # unusual user agent environment
    if os.getenv("HTTP_USER_AGENT") == "curl/7.64.1":
        indicators.append("curl-agent")

    return indicators


def is_sandbox() -> bool:
    """Heuristically determine if running in a sandbox or VM."""
    detected = check_indicators()
    log = get_logger(__name__)
    if detected:
        log.debug("Sandbox indicators detected: %s", detected)
    return bool(detected)


def is_sandboxed() -> bool:
    """Alias for :func:`is_sandbox` for older code."""
    return is_sandbox()
