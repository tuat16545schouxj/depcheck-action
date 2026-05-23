"""CSV reporter: renders detection results as comma-separated values."""
from __future__ import annotations

import csv
import io
from typing import List

from src.detectors.base import DetectionResult


class CsvReporter:
    """Renders a list of DetectionResult objects as CSV text.

    Columns: ecosystem, manifest_path, name, current_version, latest_version, outdated
    """

    COLUMNS = [
        "ecosystem",
        "manifest_path",
        "name",
        "current_version",
        "latest_version",
        "outdated",
    ]

    def __init__(self, include_header: bool = True) -> None:
        self.include_header = include_header

    def render(self, results: List[DetectionResult]) -> str:
        buf = io.StringIO()
        writer = csv.writer(buf, lineterminator="\n")
        if self.include_header:
            writer.writerow(self.COLUMNS)
        for result in results:
            for dep in result.dependencies:
                writer.writerow([
                    result.ecosystem,
                    result.manifest_path,
                    dep.name,
                    dep.current_version,
                    dep.latest_version or "",
                    str(dep.outdated).lower(),
                ])
        return buf.getvalue()

    def _render_result(self, result: DetectionResult) -> List[List[str]]:
        """Return rows for a single DetectionResult (useful for testing)."""
        return [
            [
                result.ecosystem,
                result.manifest_path,
                dep.name,
                dep.current_version,
                dep.latest_version or "",
                str(dep.outdated).lower(),
            ]
            for dep in result.dependencies
        ]
