"""CI/CD pipeline injection helpers."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Optional

from core.logger import get_logger


class CIInjector:
    """Simulate injection of CI configuration files for auditing."""

    def __init__(self) -> None:
        self.log = get_logger(__name__)

    def _is_hardened(self, text: str) -> bool:
        markers = ("gpg", "signed", "checksum")
        return any(m in text.lower() for m in markers)

    def inject_github_actions(self, repo_dir: Path, workflow: str) -> Path:
        dest = repo_dir / ".github" / "workflows" / "deathconfuser.yml"
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists() and self._is_hardened(dest.read_text()):
            self.log.warning("Refusing to inject hardened GitHub workflow %s", dest)
            return dest
        dest.write_text(workflow)
        self.log.info("Injected GitHub Actions workflow at %s", dest)
        return dest

    def inject_gitlab_ci(self, repo_dir: Path, job: str) -> Path:
        dest = repo_dir / ".gitlab-ci.yml"
        if dest.exists() and self._is_hardened(dest.read_text()):
            self.log.warning("Refusing to inject hardened GitLab CI file %s", dest)
            return dest
        dest.write_text(job)
        self.log.info("Injected GitLab CI config at %s", dest)
        return dest

    def inject_jenkinsfile(self, repo_dir: Path, step: str) -> Path:
        dest = repo_dir / "Jenkinsfile"
        if dest.exists() and self._is_hardened(dest.read_text()):
            self.log.warning("Refusing to inject hardened Jenkinsfile %s", dest)
            return dest
        content = dest.read_text() if dest.exists() else "pipeline {\n    agent any\n}"
        if "steps" in content:
            injected = content.replace("steps {", f"steps {{\n    {step}\n")
        else:
            injected = content + f"\n    stages {{ stage('dc') {{ steps {{ {step} }} }} }}"
        dest.write_text(injected)
        self.log.info("Injected Jenkinsfile step at %s", dest)
        return dest

    def cleanup(self, file: Optional[Path]) -> None:
        if file and file.exists():
            try:
                shutil.move(str(file), str(file) + ".bak")
                self.log.debug("Archived injected file %s.bak", file)
            except Exception:
                self.log.error("Failed to archive %s", file)
