"""Utilities for loading and using lightweight ML models."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List

MODEL_DIR = Path(__file__).resolve().parent.parent / "ml_models"

try:  # pragma: no cover - optional runtime dependency
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.linear_model import LogisticRegression, LinearRegression
    from sklearn.pipeline import Pipeline
    import numpy as np
    SKLEARN = True
except Exception:  # pragma: no cover
    SKLEARN = False
    from ml_training.models import (
        SeverityModel,
        PackageModel,
        PayloadModel,
        OpsecModel,
        PriorityModel,
    )


@lru_cache()
def _load_model(name: str) -> Any:
    path = MODEL_DIR / f"{name}_model.json"
    with open(path) as fh:
        data = json.load(fh)
    if not SKLEARN:
        if name == "severity":
            return SeverityModel()
        if name == "package":
            return PackageModel()
        if name == "payload":
            return PayloadModel(data.get("mapping", {}))
        if name == "opsec":
            return OpsecModel(data.get("mapping", {}))
        if name == "target":
            coef = data["model"].get("coef", [0])
            intercept = data["model"].get("intercept", 0)
            return PriorityModel(coef[0], intercept)
        return data
    if name == "target":
        model = LinearRegression()
        model.coef_ = np.array(data["model"]["coef"])  # type: ignore[attr-defined]
        model.intercept_ = np.array(data["model"]["intercept"])  # type: ignore[attr-defined]
        model.n_features_in_ = len(model.coef_)  # type: ignore[attr-defined]
        return model
    vec_data = data.get("vectorizer", {})
    vocab = {k: int(v) for k, v in vec_data.get("vocab", {}).items()}
    stop_words = vec_data.get("stop_words") or []
    vectorizer = CountVectorizer()
    vectorizer.vocabulary_ = vocab
    vectorizer.fixed_vocabulary_ = True
    vectorizer.stop_words_ = set(stop_words)
    clf = LogisticRegression()
    clf.coef_ = np.array(data["model"]["coef"])  # type: ignore[attr-defined]
    clf.intercept_ = np.array(data["model"]["intercept"])  # type: ignore[attr-defined]
    clf.classes_ = np.array(data["model"].get("classes", []))  # type: ignore[attr-defined]
    clf.n_features_in_ = len(vocab)  # type: ignore[attr-defined]
    clf.n_iter_ = np.array([1])  # type: ignore[attr-defined]
    return Pipeline([("vectorizer", vectorizer), ("model", clf)])


VARIANT_MAP = {
    "suffix_dev": lambda b: f"{b}-dev",
    "suffix_utils": lambda b: f"{b}-utils",
    "prefix_lib": lambda b: f"lib-{b}",
    "numeric_1": lambda b: f"{b}1",
}


def predict_package_variants(name: str, top_n: int = 3) -> List[str]:
    model = _load_model("package")
    probs = model.predict_proba([name])[0]
    labels = getattr(model, "classes_", [])
    pairs = sorted(zip(probs, labels), reverse=True)[:top_n]
    return [VARIANT_MAP.get(lbl, lambda b: b)(name) for _, lbl in pairs]


def classify_callback_severity(event: Dict[str, Any]) -> str:
    model = _load_model("severity")
    text = str(event.get("message", ""))
    return model.predict([text])[0]


def select_payload_for_stack(stack: str) -> str:
    model = _load_model("payload")
    return model.predict([stack])[0]


def adjust_opsec_behavior(context: Dict[str, Any]) -> Dict[str, Any]:
    model = _load_model("opsec")
    risk = context.get("risk", "low")
    behavior = model.predict([risk])[0]
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
    return profile


def score_target_priority(target: str) -> float:
    model = _load_model("target")
    length = len(target)
    score = model.predict([[length]])[0]
    return float(score)
