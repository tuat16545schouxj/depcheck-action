"""Registry of all available reporters."""
from __future__ import annotations

from typing import Dict, List, Optional, Type


def available_reporters() -> List[str]:
    """Return a sorted list of reporter names."""
    return sorted(_REGISTRY.keys())


def get_reporter_class(name: str) -> Type:
    """Return the reporter class for *name* (case-insensitive)."""
    key = name.lower()
    if key not in _REGISTRY:
        raise KeyError(f"Unknown reporter: {name!r}. Available: {available_reporters()}")
    return _REGISTRY[key]


def get_reporter(name: str, **kwargs):
    """Instantiate and return a reporter by name, forwarding *kwargs*."""
    cls = get_reporter_class(name)
    return cls(**kwargs)


def _build_registry() -> Dict[str, Type]:
    # Import lazily to avoid circular imports and optional heavy dependencies.
    from src.reporters.badge_reporter import BadgeReporter
    from src.reporters.console_reporter import ConsoleReporter
    from src.reporters.csv_reporter import CsvReporter
    from src.reporters.dashboard_reporter import DashboardReporter
    from src.reporters.datadog_reporter import DatadogReporter
    from src.reporters.email_reporter import EmailReporter
    from src.reporters.github_pr_reporter import GitHubPRReporter
    from src.reporters.graphite_reporter import GraphiteReporter
    from src.reporters.html_reporter import HtmlReporter
    from src.reporters.json_reporter import JsonReporter
    from src.reporters.junit_reporter import JUnitReporter
    from src.reporters.markdown_reporter import MarkdownReporter
    from src.reporters.pdf_reporter import PdfReporter
    from src.reporters.prometheus_reporter import PrometheusReporter
    from src.reporters.sarif_reporter import SarifReporter
    from src.reporters.slack_reporter import SlackReporter
    from src.reporters.toml_reporter import TomlReporter
    from src.reporters.xml_reporter import XmlReporter

    return {
        "badge": BadgeReporter,
        "console": ConsoleReporter,
        "csv": CsvReporter,
        "dashboard": DashboardReporter,
        "datadog": DatadogReporter,
        "email": EmailReporter,
        "github_pr": GitHubPRReporter,
        "graphite": GraphiteReporter,
        "html": HtmlReporter,
        "json": JsonReporter,
        "junit": JUnitReporter,
        "markdown": MarkdownReporter,
        "pdf": PdfReporter,
        "prometheus": PrometheusReporter,
        "sarif": SarifReporter,
        "slack": SlackReporter,
        "toml": TomlReporter,
        "xml": XmlReporter,
    }


_REGISTRY: Dict[str, Type] = _build_registry()
