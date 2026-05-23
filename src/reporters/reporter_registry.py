"""Registry of all available reporters.

Import this module to discover or instantiate reporters by name.
"""
from __future__ import annotations

from typing import Dict, List, Type

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
    "pdf": PdfReporter,
    "sarif": SarifReporter,
    "slack": SlackReporter,
    "xml": XmlReporter,
}


def available_reporters() -> List[str]:
    """Return a sorted list of reporter names."""
    return sorted(_REGISTRY.keys())


def get_reporter_class(name: str) -> Type:
    """Return the reporter class for *name*.

    Raises
    ------
    KeyError
        If *name* is not a registered reporter.
    """
    try:
        return _REGISTRY[name]
    except KeyError:
        available = ", ".join(available_reporters())
        raise KeyError(
            f"Unknown reporter {name!r}. Available reporters: {available}"
        ) from None


def get_reporter(name: str, **kwargs):
    """Instantiate and return the reporter for *name*, passing **kwargs**."""
    cls = get_reporter_class(name)
    return cls(**kwargs)
