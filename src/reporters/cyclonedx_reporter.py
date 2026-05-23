"""CycloneDX SBOM reporter – emits a CycloneDX 1.4 JSON Software Bill of Materials."""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import List

from src.detectors.base import DetectionResult


class CycloneDXReporter:
    """Render detection results as a CycloneDX 1.4 JSON SBOM."""

    SPEC_VERSION = "1.4"
    BOM_FORMAT = "CycloneDX"

    def __init__(self, serial_number: str | None = None) -> None:
        # Allow injection for deterministic tests
        self._serial = serial_number or f"urn:uuid:{uuid.uuid4()}"

    def render(self, results: List[DetectionResult]) -> str:
        components: list[dict] = []
        for result in results:
            for dep in result.dependencies:
                components.append(self._build_component(dep, result.ecosystem))

        bom = {
            "bomFormat": self.BOM_FORMAT,
            "specVersion": self.SPEC_VERSION,
            "serialNumber": self._serial,
            "version": 1,
            "metadata": {
                "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "tools": [{"name": "depcheck-action", "version": "1.0.0"}],
            },
            "components": components,
        }
        return json.dumps(bom, indent=2)

    # ------------------------------------------------------------------
    def _build_component(self, dep, ecosystem: str) -> dict:
        component: dict = {
            "type": "library",
            "name": dep.name,
            "version": dep.current_version,
            "purl": self._purl(dep.name, dep.current_version, ecosystem),
            "properties": [
                {"name": "depcheck:ecosystem", "value": ecosystem},
                {"name": "depcheck:outdated", "value": str(dep.outdated).lower()},
            ],
        }
        if dep.outdated and dep.latest_version:
            component["properties"].append(
                {"name": "depcheck:latest_version", "value": dep.latest_version}
            )
        return component

    @staticmethod
    def _purl(name: str, version: str, ecosystem: str) -> str:
        _type_map = {
            "python": "pypi",
            "node": "npm",
            "ruby": "gem",
            "go": "golang",
            "rust": "cargo",
            "java": "maven",
            "php": "composer",
            "dotnet": "nuget",
        }
        pkg_type = _type_map.get(ecosystem.lower(), ecosystem.lower())
        safe_name = name.replace("/", "%2F")
        return f"pkg:{pkg_type}/{safe_name}@{version}"
