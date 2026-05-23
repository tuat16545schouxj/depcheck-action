"""Registry of all available reporters.

Usage::

    from src.reporters.reporter_registry import get_reporter
    reporter = get_reporter("markdown")
    output = reporter.render(results)
"""
from __future__ import annotations

from typing import Dict, Type

from src.reporters.console_reporter import ConsoleReporter
from src.reporters.csv_reporter import CsvReporter
from src.reporters.email_reporter import EmailReporter
from src.reporters.html_reporter import HtmlReporter
from src.reporters.json_reporter import JsonReporter
from src.reporters.markdown_reporter import MarkdownReporter
from src.reporters.sarif_reporter import SarifReporter
from src.reporters.slack_reporter import SlackReporter
from src.reporters.xml_reporter import XmlReporter

# Map of lowercase format name -> reporter class
_REGISTRY: Dict[str, Type] = {
    "console": ConsoleReporter,
    "csv": CsvReporter,
    "email": EmailReporter,
    "html": HtmlReporter,
    "json": JsonReporter,
    "markdown": MarkdownReporter,
    "sarif": SarifReporter,
    "slack": SlackReporter,
    "xml": XmlReporter,
}


def available_reporters() -> list[str]:
    """Return sorted list of registered reporter format names."""
    return sorted(_REGISTRY.keys())


def get_reporter_class(fmt: str) -> Type:
    """Return the reporter *class* for *fmt*.

    Raises
    ------
    KeyError
        If *fmt* is not a known reporter format.
    """
    fmt = fmt.lower().strip()
    if fmt not in _REGISTRY:
        raise KeyError(
            f"Unknown reporter '{fmt}'. Available: {', '.join(available_reporters())}"
        )
    return _REGISTRY[fmt]


def get_reporter(fmt: str, **kwargs):
    """Instantiate and return a reporter for *fmt*.

    Extra *kwargs* are forwarded to the reporter constructor.
    """
    cls = get_reporter_class(fmt)
    return cls(**kwargs)
