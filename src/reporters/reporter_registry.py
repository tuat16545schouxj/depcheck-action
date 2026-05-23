"""Registry of all available reporters."""
from __future__ import annotations

from typing import Dict, List, Type

from src.reporters.markdown_reporter import MarkdownReporter
from src.reporters.json_reporter import JsonReporter
from src.reporters.console_reporter import ConsoleReporter
from src.reporters.sarif_reporter import SarifReporter
from src.reporters.slack_reporter import SlackReporter
from src.reporters.html_reporter import HtmlReporter
from src.reporters.csv_reporter import CsvReporter
from src.reporters.xml_reporter import XmlReporter
from src.reporters.email_reporter import EmailReporter
from src.reporters.badge_reporter import BadgeReporter

_REGISTRY: Dict[str, Type] = {
    "markdown": MarkdownReporter,
    "json": JsonReporter,
    "console": ConsoleReporter,
    "sarif": SarifReporter,
    "slack": SlackReporter,
    "html": HtmlReporter,
    "csv": CsvReporter,
    "xml": XmlReporter,
    "email": EmailReporter,
    "badge": BadgeReporter,
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
        return _REGISTRY[name.lower()]
    except KeyError:
        known = ", ".join(available_reporters())
        raise KeyError(f"Unknown reporter {name!r}. Known reporters: {known}") from None


def get_reporter(name: str, **kwargs):
    """Instantiate and return the reporter identified by *name*.

    Extra keyword arguments are forwarded to the reporter constructor.
    """
    cls = get_reporter_class(name)
    try:
        return cls(**kwargs)
    except TypeError:
        # Reporter may not accept kwargs — fall back to no-arg construction.
        return cls()
