"""Central registry of all available reporters.

Usage::

    from src.reporters.reporter_registry import get_reporter, available_reporters

    reporter = get_reporter("markdown")
    print(reporter.render(results))
"""

from __future__ import annotations

from typing import Dict, List, Type

from src.reporters.badge_reporter import BadgeReporter
from src.reporters.console_reporter import ConsoleReporter
from src.reporters.csv_reporter import CsvReporter
from src.reporters.dashboard_reporter import DashboardReporter
from src.reporters.email_reporter import EmailReporter
from src.reporters.graphite_reporter import GraphiteReporter
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
    "badge": BadgeReporter,
    "console": ConsoleReporter,
    "csv": CsvReporter,
    "dashboard": DashboardReporter,
    "email": EmailReporter,
    "graphite": GraphiteReporter,
    "html": HtmlReporter,
    "json": JsonReporter,
    "junit": JUnitReporter,
    "markdown": MarkdownReporter,
    "pdf": PdfReporter,
    "sarif": SarifReporter,
    "slack": SlackReporter,
    "toml": TomlReporter,
    "xml": XmlReporter,
}


def available_reporters() -> List[str]:
    """Return a sorted list of reporter names."""
    return sorted(_REGISTRY.keys())


def get_reporter_class(name: str) -> Type:
    """Return the reporter class for *name* or raise *KeyError*."""
    try:
        return _REGISTRY[name.lower()]
    except KeyError:
        raise KeyError(
            f"Unknown reporter '{name}'. Available: {', '.join(available_reporters())}"
        )


def get_reporter(name: str, **kwargs):
    """Instantiate and return the reporter identified by *name*.

    Extra *kwargs* are forwarded to the reporter constructor.
    """
    cls = get_reporter_class(name)
    return cls(**kwargs)
