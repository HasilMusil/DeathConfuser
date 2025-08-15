"""Lightweight ML helpers for DeathConfuser.

These helpers load tiny JSON based models from the :mod:`ml_models`
package.  Real deployments can replace the model files with trained
artifacts.  The functions provided here offer a consistent interface for
other modules while keeping the implementation extremely small so unit

```python
from DeathConfuser.core import ml
ml.predict_package_variants("pkg_name")
```
"""
from __future__ import annotations

from pathlib import Path
import json
import random
from typing import Any, Dict, List

MODELS_DIR = Path(__file__).resolve().parent.parent / "ml_models"


def _load(name: str) -> Dict[str, Any]:
    """Return the JSON model named ``name`` if present."""

    path = MODELS_DIR / f"{name}.json"
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception:  # pragma: no cover - corrupt model
            return {}
    return {}


def predict_package_variants(name: str) -> List[str]:
    """Predict common variants of a package ``name``.

    The default implementation uses a tiny heuristics model shipped with
the repository and applies a couple of simple transformations.  The goal
is to provide deterministic behaviour for the test-suite while exposing
an interface that can later be swapped for a real ML model.
    """

    model = _load("name_variants")
    variants = {name}
    variants.update(model.get(name, []))
    variants.add(name.replace("_", "-"))
    variants.add(name.replace("-", "_"))
    return sorted(variants)


def classify_callback_severity(data: Dict[str, Any]) -> str:
    """Classify callback ``data`` into a severity level.

    A naive keyword lookup is used; production deployments may replace
    this with a proper classifier.
    """

    model = _load("severity")
    text = json.dumps(data).lower()
    for keyword, sev in model.items():
        if keyword.lower() in text:
            return sev
    return "info"


def select_payload_for_stack(stack: str) -> str:
    """Select a payload template for a given technology stack."""

    model = _load("payloads")
    return model.get(stack, "default")


def adjust_opsec_behavior(context: Dict[str, Any]) -> Dict[str, Any]:
    """Adjust OPSEC profile fields based on a tiny model.

    Currently only tweaks delay values but can easily be extended.
    """

    model = _load("opsec")
    delay = context.get("delay", 0) + model.get("delay_adjust", 0)
    return {**context, "delay": delay}


def score_target_priority(target: str) -> float:
    """Return a numeric priority score for ``target``.

    The bundled model contains optional overrides; otherwise a simple
    length based score is returned.
    """

    model = _load("priority")
    return float(model.get(target, len(target)))


__all__ = [
    "predict_package_variants",
    "classify_callback_severity",
    "select_payload_for_stack",
    "adjust_opsec_behavior",
    "score_target_priority",
]
