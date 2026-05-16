"""SARIF (Static Analysis Results Interchange Format) reporter for depcheck-action."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import List

from src.detectors.registry import DetectionResult


SARIF_SCHEMA = "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json"
SARIF_VERSION = "2.1.0"
TOOL_NAME = "depcheck-action"
TOOL_URI = "https://github.com/your-org/depcheck-action"
RULE_ID = "DEPCHECK001"


class SarifReporter:
    """Renders detection results as a SARIF 2.1.0 document."""

    def __init__(self, tool_version: str = "1.0.0") -> None:
        self.tool_version = tool_version

    def render(self, results: List[DetectionResult]) -> str:
        """Return a SARIF JSON string for the given detection results."""
        sarif = {
            "$schema": SARIF_SCHEMA,
            "version": SARIF_VERSION,
            "runs": [self._build_run(results)],
        }
        return json.dumps(sarif, indent=2)

    def _build_run(self, results: List[DetectionResult]) -> dict:
        outdated_results = [
            dep
            for result in results
            for dep in result.dependencies
            if dep.outdated
        ]
        return {
            "tool": {
                "driver": {
                    "name": TOOL_NAME,
                    "version": self.tool_version,
                    "informationUri": TOOL_URI,
                    "rules": [self._build_rule()],
                }
            },
            "results": [self._build_result(dep, result) for result in results for dep in result.dependencies if dep.outdated],
            "invocations": [
                {
                    "executionSuccessful": True,
                    "endTimeUtc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                }
            ],
        }

    def _build_rule(self) -> dict:
        return {
            "id": RULE_ID,
            "name": "OutdatedDependency",
            "shortDescription": {"text": "Outdated dependency detected."},
            "fullDescription": {
                "text": "A dependency is not at its latest available version."
            },
            "helpUri": TOOL_URI,
            "defaultConfiguration": {"level": "warning"},
        }

    def _build_result(self, dep, detection_result: DetectionResult) -> dict:
        message = (
            f"{dep.name} {dep.current_version} is outdated"
            + (f"; latest is {dep.latest_version}" if dep.latest_version else "")
            + f" (ecosystem: {detection_result.ecosystem})"
        )
        return {
            "ruleId": RULE_ID,
            "level": "warning",
            "message": {"text": message},
            "locations": [
                {
                    "physicalLocation": {
                        "artifactLocation": {
                            "uri": detection_result.manifest_path,
                            "uriBaseId": "%SRCROOT%",
                        }
                    }
                }
            ],
            "fingerprints": {
                "depcheck/v1": f"{detection_result.ecosystem}:{dep.name}:{dep.current_version}"
            },
        }
