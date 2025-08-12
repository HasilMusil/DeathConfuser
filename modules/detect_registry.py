from __future__ import annotations

"""Registry detection utilities for DeathConfuser.

This module provides a lightweight :func:`detect_registry` helper which attempts
to infer the most likely package registry for a given file path or piece of
source code.  The detection is heuristic-based and avoids any network calls so
it can run prior to probing remote registries.
"""

from pathlib import Path
from typing import List, Tuple, Union

# Known manifest files that strongly indicate an ecosystem
MANIFEST_FILES = {
    "npm": {"package.json"},
    "pypi": {"requirements.txt", "setup.py", "Pipfile"},
    "rubygems": {"Gemfile"},
    "composer": {"composer.json"},
    "maven": {"pom.xml", "build.gradle"},
    "nuget": {"packages.config", "*.csproj"},
    "rust": {"Cargo.toml"},
    "golang": {"go.mod"},
    "cpan": {"Makefile.PL", "Build.PL"},
    "hackage": {"stack.yaml", "*.cabal"},
    "hexpm": {"mix.exs"},
    "swiftpm": {"Package.swift"},
    "cocoapods": {"Podfile"},
    "conda": {"environment.yml"},
    "meteor": {".meteor/packages"},
}

# File extensions which hint at a language / ecosystem
EXTENSIONS = {
    ".js": {"npm"},
    ".ts": {"npm"},
    ".py": {"pypi"},
    ".rb": {"rubygems"},
    ".php": {"composer"},
    ".java": {"maven"},
    ".gradle": {"maven"},
    ".cs": {"nuget"},
    ".rs": {"rust"},
    ".go": {"golang"},
    ".pl": {"cpan"},
    ".pm": {"cpan"},
    ".hs": {"hackage"},
    ".ex": {"hexpm"},
    ".exs": {"hexpm"},
    ".erl": {"hexpm"},
    ".swift": {"swiftpm", "cocoapods"},
    ".m": {"cocoapods"},
}

# Common keywords which may appear in READMEs or metadata
KEYWORDS = {
    "npm": {"npm install", "yarn add"},
    "pypi": {"pip install", "python package"},
    "rubygems": {"gem install", "bundle install"},
    "composer": {"composer require", "packagist"},
    "maven": {"mvn install", "maven"},
    "nuget": {"install-package", "nuget install"},
    "rust": {"cargo install", "crates.io"},
    "golang": {"go get", "go install"},
    "cpan": {"cpan install", "perl module"},
    "hackage": {"cabal install", "stack build"},
    "hexpm": {"mix deps.get", "hex.pm"},
    "swiftpm": {"swift build", "swift package"},
    "cocoapods": {"pod install", "cocoapods"},
    "conda": {"conda install", "anaconda.org"},
    "meteor": {"meteor add", "meteor remove"},
}

# Weights assigned to different evidence types.  The values are chosen so that
# a single strong indicator (manifest or extension) yields a confidence above
# the 0.7 threshold used by the scan logic.
MANIFEST_WEIGHT = 0.8
EXTENSION_WEIGHT = 0.7
KEYWORD_WEIGHT = 0.3

RegistryResult = Tuple[str, float]


def _check_keywords(text: str, scores: dict[str, float]) -> None:
    text = text.lower()
    for reg, words in KEYWORDS.items():
        if any(word in text for word in words):
            scores[reg] += KEYWORD_WEIGHT


def detect_registry(package_path_or_code: Union[str, Path]) -> List[RegistryResult]:
    """Return probable registries for the supplied path or code snippet.

    The result is a list of ``(registry, confidence)`` tuples ordered by
    confidence in descending order.  Confidence values range from ``0`` to ``1``.
    """

    scores: dict[str, float] = {name: 0.0 for name in MANIFEST_FILES}
    try:
        path = Path(package_path_or_code)  # type: ignore[arg-type]
    except TypeError:
        path = Path(str(package_path_or_code))

    if path.exists():
        try:
            if path.is_dir():
                for reg, patterns in MANIFEST_FILES.items():
                    if any(path.glob(pattern) for pattern in patterns):
                        scores[reg] += MANIFEST_WEIGHT
                # inspect README-like files for keywords
                for readme in path.glob("README*"):
                    try:
                        _check_keywords(readme.read_text(errors="ignore"), scores)
                    except OSError:
                        continue
            else:
                ext = path.suffix.lower()
                regs = EXTENSIONS.get(ext, set())
                for reg in regs:
                    scores[reg] += EXTENSION_WEIGHT
                parent = path.parent
                for reg_name, patterns in MANIFEST_FILES.items():
                    if any(parent.glob(pattern) for pattern in patterns):
                        scores[reg_name] += MANIFEST_WEIGHT
                try:
                    _check_keywords(path.read_text(errors="ignore"), scores)
                except OSError:
                    pass
        except OSError:
            pass
    else:
        # treat input as code or a path string which does not exist locally
        text = str(package_path_or_code)
        ext = Path(text).suffix.lower()
        regs = EXTENSIONS.get(ext, set())
        for reg in regs:
            scores[reg] += EXTENSION_WEIGHT
        _check_keywords(text, scores)

    results: List[RegistryResult] = [
        (reg, min(score, 1.0)) for reg, score in scores.items() if score > 0
    ]
    results.sort(key=lambda x: x[1], reverse=True)
    return results
