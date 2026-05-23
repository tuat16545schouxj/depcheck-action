"""Registry of all available reporters."""

from __future__ import annotations

from typing import Dict, Type

from src.reporters.markdown_reporter import MarkdownReporter
from src.reporters.json_reporter import JsonReporter
from src.reporters.console_reporter import ConsoleReporter
from src.reporters.sarif_reporter import SarifReporter
from src.reporters.slack_reporter import SlackReporter
from src.reporters.html_reporter import HtmlReporter
from src.reporters.csv_reporter import CsvReporter
from src.reporters.xml_reporter import XmlReporter

_REPORTERS: Dict[str, Type] = {
    "markdown": MarkdownReporter,
    "json": JsonReporter,
    "console": ConsoleReporter,
    "sarif": SarifReporter,
    "slack": SlackReporter,
    "html": HtmlReporter,
    "csv": CsvReporter,
    "xml": XmlReporter,
}


def available_reporters() -> list[str]:
    """Return the names of all registered reporters."""
    return list(_REPORTERS.keys())


def get_reporter_class(name: str) -> Type:
    """Return the reporter class for *name*.

    Raises
    ------
    ValueError
        If *name* is not a registered reporter.
    """
    try:
        return _REPORTERS[name.lower()]
    except KeyError:
        raise ValueError(
            f"Unknown reporter '{name}'. "
            f"Available: {', '.join(available_reporters())}"
        )


def get_reporter(name: str, **kwargs):
    """Instantiate and return the reporter identified by *name*.

    Extra keyword arguments are forwarded to the reporter constructor.
    """
    cls = get_reporter_class(name)
    return cls(**kwargs)
