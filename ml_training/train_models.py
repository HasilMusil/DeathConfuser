import csv
import json
from pathlib import Path
try:  # pragma: no cover - optional dependency for offline training
    from sklearn.pipeline import make_pipeline
    from sklearn.linear_model import LogisticRegression, LinearRegression
    from sklearn.feature_extraction.text import CountVectorizer
    SKLEARN = True
except Exception:  # pragma: no cover - fallback when sklearn missing
    SKLEARN = False

from .models import (
    SeverityModel,
    PackageModel,
    PayloadModel,
    OpsecModel,
    PriorityModel,
)

DATA_DIR = Path(__file__).resolve().parent / "data"
MODEL_DIR = Path(__file__).resolve().parents[1] / "ml_models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)


def train_severity() -> None:
    texts, labels = [], []
    with open(DATA_DIR / "severity.csv", newline="") as fh:
        for row in csv.DictReader(fh):
            texts.append(row["message"])
            labels.append(row["severity"])
    if SKLEARN:
        model = make_pipeline(CountVectorizer(), LogisticRegression(max_iter=200))
        model.fit(texts, labels)
        vec = model.named_steps["countvectorizer"]
        clf = model.named_steps["logisticregression"]
        data = {
            "vectorizer": {
                "vocab": vec.vocabulary_,
                "stop_words": list(getattr(vec, "stop_words_", []) or []),
            },
            "model": {
                "coef": clf.coef_.tolist(),
                "intercept": clf.intercept_.tolist(),
                "classes": clf.classes_.tolist(),
            },
        }
    else:
        data = {
            "vectorizer": {"vocab": {}, "stop_words": []},
            "model": {
                "coef": [],
                "intercept": [],
                "classes": ["critical", "medium", "low", "info"],
            },
        }
    with open(MODEL_DIR / "severity_model.json", "w") as fh:
        json.dump(data, fh)


def train_package() -> None:
    bases, labels = [], []
    with open(DATA_DIR / "package_variants.csv", newline="") as fh:
        for row in csv.DictReader(fh):
            bases.append(row["base"])
            labels.append(row["label"])
    if SKLEARN:
        model = make_pipeline(
            CountVectorizer(analyzer="char", ngram_range=(2, 3)),
            LogisticRegression(max_iter=200),
        )
        model.fit(bases, labels)
        vec = model.named_steps["countvectorizer"]
        clf = model.named_steps["logisticregression"]
        data = {
            "vectorizer": {
                "vocab": vec.vocabulary_,
                "stop_words": list(getattr(vec, "stop_words_", []) or []),
            },
            "model": {
                "coef": clf.coef_.tolist(),
                "intercept": clf.intercept_.tolist(),
                "classes": clf.classes_.tolist(),
            },
        }
    else:
        data = {
            "vectorizer": {"vocab": {}, "stop_words": []},
            "model": {
                "coef": [],
                "intercept": [],
                "classes": PackageModel.classes_,
            },
        }
    with open(MODEL_DIR / "package_model.json", "w") as fh:
        json.dump(data, fh)


def train_payload() -> None:
    stacks, payloads = [], []
    with open(DATA_DIR / "payload.csv", newline="") as fh:
        for row in csv.DictReader(fh):
            stacks.append(row["stack"])
            payloads.append(row["payload"])
    mapping = {s: p for s, p in zip(stacks, payloads)}
    if SKLEARN:
        model = make_pipeline(CountVectorizer(), LogisticRegression(max_iter=200))
        model.fit(stacks, payloads)
        vec = model.named_steps["countvectorizer"]
        clf = model.named_steps["logisticregression"]
        data = {
            "vectorizer": {
                "vocab": vec.vocabulary_,
                "stop_words": list(getattr(vec, "stop_words_", []) or []),
            },
            "model": {
                "coef": clf.coef_.tolist(),
                "intercept": clf.intercept_.tolist(),
                "classes": clf.classes_.tolist(),
            },
            "mapping": mapping,
        }
    else:
        data = {
            "vectorizer": {"vocab": {}, "stop_words": []},
            "model": {"coef": [], "intercept": [], "classes": []},
            "mapping": mapping,
        }
    with open(MODEL_DIR / "payload_model.json", "w") as fh:
        json.dump(data, fh)


def train_opsec() -> None:
    risks, behaviors = [], []
    with open(DATA_DIR / "opsec.csv", newline="") as fh:
        for row in csv.DictReader(fh):
            risks.append(row["risk"])
            behaviors.append(row["behavior"])
    mapping = {r: b for r, b in zip(risks, behaviors)}
    if SKLEARN:
        model = make_pipeline(CountVectorizer(), LogisticRegression(max_iter=200))
        model.fit(risks, behaviors)
        vec = model.named_steps["countvectorizer"]
        clf = model.named_steps["logisticregression"]
        data = {
            "vectorizer": {
                "vocab": vec.vocabulary_,
                "stop_words": list(getattr(vec, "stop_words_", []) or []),
            },
            "model": {
                "coef": clf.coef_.tolist(),
                "intercept": clf.intercept_.tolist(),
                "classes": clf.classes_.tolist(),
            },
            "mapping": mapping,
        }
    else:
        data = {
            "vectorizer": {"vocab": {}, "stop_words": []},
            "model": {"coef": [], "intercept": [], "classes": []},
            "mapping": mapping,
        }
    with open(MODEL_DIR / "opsec_model.json", "w") as fh:
        json.dump(data, fh)


def train_priority() -> None:
    lengths, scores = [], []
    with open(DATA_DIR / "priority.csv", newline="") as fh:
        for row in csv.DictReader(fh):
            lengths.append([float(row["length"])])
            scores.append(float(row["score"]))
    if SKLEARN:
        model = LinearRegression()
        model.fit(lengths, scores)
        coef = model.coef_.tolist()
        intercept = float(model.intercept_)
    else:
        xs = [l[0] for l in lengths]
        n = len(xs)
        mean_x = sum(xs) / n
        mean_y = sum(scores) / n
        num = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, scores))
        den = sum((x - mean_x) ** 2 for x in xs) or 1.0
        a = num / den
        b = mean_y - a * mean_x
        coef = [a]
        intercept = b
    data = {"model": {"coef": coef, "intercept": intercept}}
    with open(MODEL_DIR / "target_model.json", "w") as fh:
        json.dump(data, fh)


def main() -> None:
    train_severity()
    train_package()
    train_payload()
    train_opsec()
    train_priority()
    print("models trained")


if __name__ == "__main__":
    main()
