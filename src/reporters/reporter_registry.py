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
from src.reporters.sarif_reporter import SarifReporter
from src.reporters.slack_reporter import SlackReporter
from src.reporters.xml_reporter import XmlReporter

_REGISTRY: Dict[str, Type] = {
    "badge": BadgeReporter,
    "console": ConsoleReporter,
    "csv": CsvReporter,
    "dashboard": DashboardReporter,
    "email": EmailReporter,
    "github_pr": GitHubPRReporter,
    "html": HtmlReporter,
    "json": JsonReporter,
    "junit": JUnitReporter,
    "markdown": MarkdownReporter,
    "sarif": SarifReporter,
    "slack": SlackReporter,
    "xml": XmlReporter,
}


def available_reporters() -> List[str]:
    """Return a sorted list of reporter names."""
    return sorted(_REGISTRY.keys())


def get_reporter_class(name: str) -> Optional[Type]:
    """Return the reporter class for *name*, or None if unknown."""
    return _REGISTRY.get(name)


def get_reporter(name: str, **kwargs):
    """Instantiate and return a reporter by name.

    Extra keyword arguments are forwarded to the constructor.
    Raises ValueError for unknown reporter names.
    """
    cls = get_reporter_class(name)
    if cls is None:
        raise ValueError(f"Unknown reporter: {name!r}. Available: {available_reporters()}")
    try:
        return cls(**kwargs)
    except TypeError:
        return cls()
