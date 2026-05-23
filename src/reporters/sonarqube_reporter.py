"""SonarQube Generic Issue Format reporter.

Outputs JSON conforming to SonarQube's generic external issues format so
results can be imported via ``sonar.externalIssuesReportPaths``.

Reference:
  https://docs.sonarqube.org/latest/analyzing-source-code/importing-external-issues/generic-issue-import-format/
"""

from __future__ import annotations

import json
from typing import Any

from src.detectors.base import DetectionResult


class SonarQubeReporter:
    """Render detection results as a SonarQube Generic Issue report."""

    # SonarQube severity levels (mapped from outdated-ness heuristic)
    _SEVERITY_OUTDATED = "MAJOR"
    _SEVERITY_UNKNOWN = "INFO"
    _RULE_ID = "depcheck:outdated-dependency"
    _TYPE = "CODE_SMELL"

    def __init__(self, *, engine_id: str = "depcheck") -> None:
        self.engine_id = engine_id

    def render(self, results: list[DetectionResult]) -> str:
        """Return a JSON string in SonarQube generic issue format."""
        issues: list[dict[str, Any]] = []
        for result in results:
            for dep in result.dependencies:
                if not dep.outdated:
                    continue
                issues.append(self._build_issue(result, dep))

        payload: dict[str, Any] = {
            "engineId": self.engine_id,
            "rules": [self._build_rule()],
            "issues": issues,
        }
        return json.dumps(payload, indent=2)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_rule(self) -> dict[str, Any]:
        return {
            "id": self._RULE_ID,
            "name": "Outdated Dependency",
            "description": "A direct dependency has a newer version available.",
            "engineId": self.engine_id,
            "cleanCodeAttribute": "CONVENTIONAL",
            "impacts": [
                {"softwareQuality": "MAINTAINABILITY", "severity": "MEDIUM"}
            ],
        }

    def _build_issue(
        self, result: DetectionResult, dep: Any
    ) -> dict[str, Any]:
        current = dep.current_version or "unknown"
        latest = dep.latest_version or "unknown"
        message = (
            f"{dep.name} is outdated: {current} → {latest} "
            f"(ecosystem: {result.ecosystem})"
        )
        issue: dict[str, Any] = {
            "ruleId": self._RULE_ID,
            "engineId": self.engine_id,
            "severity": self._SEVERITY_OUTDATED,
            "type": self._TYPE,
            "primaryLocation": {
                "message": message,
                "filePath": result.manifest_path,
            },
        }
        return issue
