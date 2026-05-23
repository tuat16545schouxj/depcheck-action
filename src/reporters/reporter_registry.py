"""Registry of all available reporters."""
from __future__ import annotations

from typing import Dict, List, Optional, Type

from src.reporters.badge_reporter import BadgeReporter
from src.reporters.console_reporter import ConsoleReporter
from src.reporters.csv_reporter import CsvReporter
from src.reporters.dashboard_reporter import DashboardReporter
from src.reporters.email_reporter import EmailReporter
from src.reporters.github_pr_reporter import GitHubPRReporter
from src.reporters.html_reporter import HtmlReporter
from src.reporters.json_reporter import JsonReporter
from src.reporters.junit_reporter import JUnitReporter
from src.reporters.markdown_reporter import MarkdownReporter
from src.reporters.pdf_reporter import PdfReporter
from src.reporters.sarif_reporter import SarifReporter
from src.reporters.slack_reporter import SlackReporter
from src.reporters.toml_reporter import TomlReporter
from src.reporters.xml_reporter import XmlReporter

_REGISTRY: Dict[str, Type] = {
    BadgeReporter.name: BadgeReporter,
    "console": ConsoleReporter,
    CsvReporter.name: CsvReporter,
    "dashboard": DashboardReporter,
    "email": EmailReporter,
    "github_pr": GitHubPRReporter,
    "html": HtmlReporter,
    "json": JsonReporter,
    "junit": JUnitReporter,
    "markdown": MarkdownReporter,
    "pdf": PdfReporter,
    "sarif": SarifReporter,
    "slack": SlackReporter,
    TomlReporter.name: TomlReporter,
    "xml": XmlReporter,
}


def available_reporters() -> List[str]:
    """Return a sorted list of reporter names."""
    return sorted(_REGISTRY.keys())


def get_reporter_class(name: str) -> Optional[Type]:
    """Return the reporter class for *name*, or None if unknown."""
    return _REGISTRY.get(name)


def get_reporter(name: str, **kwargs):
    """Instantiate and return the reporter identified by *name*.

    Extra keyword arguments are forwarded to the reporter constructor.
    Raises ValueError for unknown reporter names.
    """
    cls = get_reporter_class(name)
    if cls is None:
        known = ", ".join(available_reporters())
        raise ValueError(f"Unknown reporter '{name}'. Available: {known}")
    try:
        return cls(**kwargs)
    except TypeError:
        return cls()
