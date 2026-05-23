"""Central registry mapping reporter names to reporter classes."""
from __future__ import annotations

from typing import Dict, List, Optional, Type


def _build_registry() -> Dict[str, str]:
    """Return {name: dotted_class_path} for every available reporter."""
    return {
        "badge": "src.reporters.badge_reporter.BadgeReporter",
        "console": "src.reporters.console_reporter.ConsoleReporter",
        "csv": "src.reporters.csv_reporter.CsvReporter",
        "cyclonedx": "src.reporters.cyclonedx_reporter.CycloneDXReporter",
        "dashboard": "src.reporters.dashboard_reporter.DashboardReporter",
        "datadog": "src.reporters.datadog_reporter.DatadogReporter",
        "email": "src.reporters.email_reporter.EmailReporter",
        "github_pr": "src.reporters.github_pr_reporter.GitHubPRReporter",
        "graphite": "src.reporters.graphite_reporter.GraphiteReporter",
        "html": "src.reporters.html_reporter.HtmlReporter",
        "influxdb": "src.reporters.influxdb_reporter.InfluxDBReporter",
        "json": "src.reporters.json_reporter.JsonReporter",
        "junit": "src.reporters.junit_reporter.JUnitReporter",
        "markdown": "src.reporters.markdown_reporter.MarkdownReporter",
        "opsgenie": "src.reporters.opsgenie_reporter.OpsGenieReporter",
        "pdf": "src.reporters.pdf_reporter.PdfReporter",
        "prometheus": "src.reporters.prometheus_reporter.PrometheusReporter",
        "sarif": "src.reporters.sarif_reporter.SarifReporter",
        "slack": "src.reporters.slack_reporter.SlackReporter",
        "sonarqube": "src.reporters.sonarqube_reporter.SonarQubeReporter",
        "teamcity": "src.reporters.teamcity_reporter.TeamCityReporter",
        "toml": "src.reporters.toml_reporter.TomlReporter",
        "xml": "src.reporters.xml_reporter.XmlReporter",
    }


_REGISTRY: Dict[str, str] = _build_registry()


def available_reporters() -> List[str]:
    """Return a sorted list of all registered reporter names."""
    return sorted(_REGISTRY.keys())


def get_reporter_class(name: str) -> Type:
    """Import and return the class for *name*; raise ValueError if unknown."""
    import importlib

    if name not in _REGISTRY:
        raise ValueError(
            f"Unknown reporter '{name}'. Available: {', '.join(available_reporters())}"
        )
    module_path, class_name = _REGISTRY[name].rsplit(".", 1)
    module = importlib.import_module(module_path)
    return getattr(module, class_name)


def get_reporter(name: str, **kwargs) -> object:
    """Instantiate and return the reporter for *name*, forwarding **kwargs."""
    cls = get_reporter_class(name)
    try:
        return cls(**kwargs)
    except TypeError:
        return cls()
