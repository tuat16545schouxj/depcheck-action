"""Reporter registry: discover and instantiate reporters by name."""
from __future__ import annotations

from typing import Dict, List, Optional, Type

from src.reporters.console_reporter import ConsoleReporter
from src.reporters.csv_reporter import CsvReporter
from src.reporters.github_pr_reporter import GitHubPRReporter
from src.reporters.html_reporter import HtmlReporter
from src.reporters.json_reporter import JsonReporter
from src.reporters.markdown_reporter import MarkdownReporter
from src.reporters.sarif_reporter import SarifReporter
from src.reporters.slack_reporter import SlackReporter

# Maps lowercase alias -> reporter class
_REGISTRY: Dict[str, Type] = {
    "console": ConsoleReporter,
    "csv": CsvReporter,
    "github_pr": GitHubPRReporter,
    "html": HtmlReporter,
    "json": JsonReporter,
    "markdown": MarkdownReporter,
    "sarif": SarifReporter,
    "slack": SlackReporter,
}


def available_reporters() -> List[str]:
    """Return sorted list of registered reporter names."""
    return sorted(_REGISTRY.keys())


def get_reporter_class(name: str) -> Optional[Type]:
    """Return the reporter class for *name*, or None if not found."""
    return _REGISTRY.get(name.lower())


def get_reporter(name: str, **kwargs):
    """Instantiate and return a reporter by name.

    Extra *kwargs* are forwarded to the reporter constructor.
    Raises ValueError for unknown names.
    """
    cls = get_reporter_class(name)
    if cls is None:
        raise ValueError(
            f"Unknown reporter '{name}'. "
            f"Available: {', '.join(available_reporters())}"
        )
    try:
        return cls(**kwargs)
    except TypeError:
        # Reporter doesn't accept kwargs — instantiate without them
        return cls()
