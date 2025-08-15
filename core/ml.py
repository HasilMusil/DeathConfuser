"""ML utilities for DeathConfuser — supports both trained sklearn models and lightweight JSON fallbacks."""
from __future__ import annotations

import json
import random
from pathlib import Path
from functools import lru_cache
from typing import Any, Dict, List

MODEL_DIR = Path(__file__).resolve().parent.parent / "ml_models"

# Optional sklearn support.  The JSON models in this repository are
# deliberately minimal; they generally do not ship with full vectorizer or
# coefficient data.  Attempting to bootstrap real sklearn models from these
# files would result in runtime errors (e.g. empty vocabularies).  To keep the
# code lightweight and robust we therefore only enable sklearn integration if
# the library is available *and* the model files contain the necessary fields.
try:  # pragma: no cover - optional dependency
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.linear_model import LogisticRegression, LinearRegression
    from sklearn.pipeline import Pipeline
    import numpy as np
    SKLEARN_AVAILABLE = True
except Exception:  # pragma: no cover
    SKLEARN_AVAILABLE = False

# Optional fallback custom classes if available.  These provide trivial
# ``predict`` implementations used in tests when sklearn is absent.
try:  # pragma: no cover - best effort imports
    from ml_training.models import (
        SeverityModel,
        PackageModel,
        PayloadModel,
        OpsecModel,
        PriorityModel,
    )
except Exception:  # pragma: no cover - models are optional
    SeverityModel = PackageModel = PayloadModel = OpsecModel = PriorityModel = None


@lru_cache()
def _load_model(name: str) -> Any:
    """Load model from JSON, supporting sklearn or simple JSON lookup."""
    json_path = MODEL_DIR / f"{name}.json"
    if not json_path.exists():
        json_path = MODEL_DIR / f"{name}_model.json"
    if not json_path.exists():
        return {}

    with open(json_path) as fh:
        data = json.load(fh)

    # Many of the JSON files simply contain mapping dictionaries.  If we detect
    # that the data lacks a proper model or vocabulary we return the raw data so
    # that helper functions can operate on it directly.
    if (
        not SKLEARN_AVAILABLE
        or "model" not in data
        or not data.get("vectorizer", {}).get("vocab")
    ):
        # Use lightweight fallback models when available
        if name == "package" and PackageModel:
            return PackageModel()
        if name == "payload" and PayloadModel:
            return PayloadModel(data.get("mapping", {}))
        if name.startswith("opsec") and OpsecModel:
            return OpsecModel(data.get("mapping", {}))
        if name == "target" and PriorityModel:
            coef = data.get("model", {}).get("coef", [0])
            intercept = data.get("model", {}).get("intercept", 0)
            return PriorityModel(coef[0], intercept)
        # Extract nested mapping dictionaries for convenience
        if "mapping" in data:
            return data["mapping"]
        return data

    # At this point we have sklearn available and the JSON file contains the
    # required fields to reconstruct a simple model.
    if name == "target":
        model = LinearRegression()
        model.coef_ = np.array(data["model"]["coef"])  # type: ignore
        model.intercept_ = np.array(data["model"]["intercept"])  # type: ignore
        model.n_features_in_ = len(model.coef_)  # type: ignore
        return model

    vec_data = data.get("vectorizer", {})
    vocab = {k: int(v) for k, v in vec_data.get("vocab", {}).items()}
    stop_words = vec_data.get("stop_words") or []
    vectorizer = CountVectorizer()
    vectorizer.vocabulary_ = vocab
    vectorizer.fixed_vocabulary_ = True
    vectorizer.stop_words_ = set(stop_words)
    clf = LogisticRegression()
    clf.coef_ = np.array(data["model"]["coef"])  # type: ignore
    clf.intercept_ = np.array(data["model"]["intercept"])  # type: ignore
    clf.classes_ = np.array(data["model"].get("classes", []))  # type: ignore
    clf.n_features_in_ = len(vocab)  # type: ignore
    clf.n_iter_ = np.array([1])  # type: ignore
    return Pipeline([("vectorizer", vectorizer), ("model", clf)])


VARIANT_MAP = {
    "suffix_dev": lambda b: f"{b}-dev",
    "suffix_utils": lambda b: f"{b}-utils",
    "prefix_lib": lambda b: f"lib-{b}",
    "numeric_1": lambda b: f"{b}1",
}


def predict_package_variants(name: str, top_n: int = 3) -> List[str]:
    model = _load_model("package")
    if hasattr(model, "predict_proba"):
        probs = model.predict_proba([name])[0]
        labels = getattr(model, "classes_", [])
        pairs = sorted(zip(probs, labels), reverse=True)[:top_n]
        variants = [VARIANT_MAP.get(lbl, lambda b: b)(name) for _, lbl in pairs]
        variants.extend([name, name.replace("_", "-"), name.replace("-", "_")])
        return sorted(set(variants))
    # JSON fallback
    variants = {name}
    if isinstance(model, dict):
        variants.update(model.get(name, []))
    else:
        extra = _load_model("name_variants")
        if isinstance(extra, dict):
            variants.update(extra.get(name, []))
    variants.add(name.replace("_", "-"))
    variants.add(name.replace("-", "_"))
    return sorted(variants)


def classify_callback_severity(event: Dict[str, Any]) -> str:
    mapping = _load_model("severity")
    if SeverityModel:
        text = str(event.get("message", ""))
        sev = SeverityModel().predict([text])[0]
        if sev != "info":
            return sev
    if isinstance(mapping, dict):
        text = json.dumps(event).lower()
        for keyword, sev in mapping.items():
            if keyword.lower() in text:
                return sev
    return "info"


def select_payload_for_stack(stack: str) -> str:
    model = _load_model("payload")
    if hasattr(model, "predict"):
        return model.predict([stack])[0]
    if isinstance(model, dict):
        return model.get(stack, "default")
    return "default"


def adjust_opsec_behavior(context: Dict[str, Any]) -> Dict[str, Any]:
    """Adjust behaviour based on OPSEC risk profile."""

    model = _load_model("opsec_model") or _load_model("opsec")
    delay_conf = _load_model("opsec")

    if hasattr(model, "predict"):
        behavior = model.predict([context.get("risk", "low")])[0]
        profile = dict(context)
        if behavior == "stealth":
            profile["delay"] = max(profile.get("delay", 1), 5)
            profile["user_agent"] = "Mozilla/5.0 (Stealth)"
        elif behavior == "balanced":
            profile["delay"] = max(profile.get("delay", 1), 2)
            profile["user_agent"] = "Balanced/1.0"
        else:
            profile["delay"] = min(profile.get("delay", 1), 0.1)
            profile["user_agent"] = "Aggressive/1.0"
        profile["behavior"] = behavior
    elif isinstance(model, dict):
        behavior = model.get(context.get("risk", "low"), "balanced")
        profile = {**context, "behavior": behavior}
    else:
        profile = dict(context)

    if isinstance(delay_conf, dict):
        profile["delay"] = profile.get("delay", 0) + delay_conf.get("delay_adjust", 0)
    return profile


def score_target_priority(target: str) -> float:
    model = _load_model("target")
    if hasattr(model, "predict"):
        return float(model.predict([[len(target)]])[0])
    if isinstance(model, dict):
        if "coef" in model.get("model", {}):
            coef = model["model"].get("coef", [0])[0]
            intercept = model["model"].get("intercept", 0)
            return float(coef * len(target) + intercept)
        return float(model.get(target, len(target)))
    return float(len(target))


__all__ = [
    "predict_package_variants",
    "classify_callback_severity",
    "select_payload_for_stack",
    "adjust_opsec_behavior",
    "score_target_priority",
]
