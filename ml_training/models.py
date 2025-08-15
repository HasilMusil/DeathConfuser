"""Fallback model classes used when scikit-learn is unavailable."""
from __future__ import annotations

class SeverityModel:
    def predict(self, X):
        out = []
        for text in X:
            t = text.lower()
            if any(k in t for k in ["critical", "leak", "privilege"]):
                out.append("critical")
            elif "medium" in t or "warning" in t:
                out.append("medium")
            elif "bug" in t or "issue" in t:
                out.append("low")
            else:
                out.append("info")
        return out

class PackageModel:
    classes_ = ["suffix_dev", "suffix_utils", "prefix_lib", "numeric_1"]

    def predict_proba(self, X):
        return [[0.25, 0.25, 0.25, 0.25] for _ in X]

class PayloadModel:
    def __init__(self, mapping: dict):
        self.mapping = mapping

    def predict(self, X):
        return [self.mapping.get(x, "default.j2") for x in X]

class OpsecModel:
    def __init__(self, mapping: dict):
        self.mapping = mapping

    def predict(self, X):
        return [self.mapping.get(x, "balanced") for x in X]

class PriorityModel:
    def __init__(self, a: float, b: float):
        self.a = a
        self.b = b

    def predict(self, X):
        return [self.a * x[0] + self.b for x in X]
