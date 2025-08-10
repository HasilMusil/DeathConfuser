"""Report generation utilities."""
from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List

from jinja2 import Environment, FileSystemLoader, select_autoescape

from ..core.logger import get_logger

TEMPLATE_DIR = Path(__file__).parent / "templates"

log = get_logger(__name__)


@dataclass
class PayloadInfo:
    """Information about a payload used during a scan."""

    name: str
    snippet: str
    ecosystem: str


@dataclass
class CallbackInfo:
    """Status of callbacks triggered by payload execution."""

    type: str
    status: str
    detail: str | None = None


@dataclass
class ReportData:
    """Normalized representation of scan results."""

    target: str
    timestamp: datetime
    profile: str
    tech_stack: Iterable[str]
    registries: Dict[str, Iterable[str]]
    payloads: List[PayloadInfo]
    callbacks: List[CallbackInfo]

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data


class ReportExporter:
    """Export findings to various formats."""

    def __init__(self, template_dir: Path = TEMPLATE_DIR) -> None:
        self.template_dir = template_dir
        self.env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape()
        )

    def _render(self, template: str, context: Dict[str, Any]) -> str:
        tmpl = self.env.get_template(template)
        return tmpl.render(**context)

    def _normalize(self, data: Dict[str, Any] | ReportData) -> Dict[str, Any]:
        if isinstance(data, ReportData):
            return data.to_dict()
        return data

    def export_json(self, data: Dict[str, Any] | ReportData, path: Path) -> Path:
        """Write findings to a JSON file."""
        payload = self._normalize(data)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2))
        log.debug("Wrote JSON report to %s", path)
        return path

    def export_html(self, data: Dict[str, Any] | ReportData, path: Path) -> Path:
        """Write findings to an HTML file using template."""
        context = self._normalize(data)
        html = self._render("html_template.j2", context)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html)
        log.debug("Wrote HTML report to %s", path)
        return path

    def export_markdown(self, data: Dict[str, Any] | ReportData, path: Path) -> Path:
        """Write findings to a Markdown file using template."""
        context = self._normalize(data)
        md = self._render("markdown_template.j2", context)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(md)
        log.debug("Wrote Markdown report to %s", path)
        return path

    def export_all(
        self, data: Dict[str, Any] | ReportData, output_dir: Path, base_name: str
    ) -> Dict[str, Path]:
        """Export all report formats and return created file paths."""
        reports = {
            "json": self.export_json(data, output_dir / "json" / f"{base_name}.json"),
            "html": self.export_html(data, output_dir / "html" / f"{base_name}.html"),
            "markdown": self.export_markdown(data, output_dir / "markdown" / f"{base_name}.md"),
        }
        return reports
