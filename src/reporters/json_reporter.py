"""JSON reporter for depcheck-action audit results."""

import json
from datetime import datetime, timezone
from typing import List

from src.detectors.base import DetectionResult


class JsonReporter:
    """Renders detection results as a structured JSON report."""

    def __init__(self, indent: int = 2):
        self.indent = indent

    def render(self, results: List[DetectionResult]) -> str:
        """Serialize all detection results to a JSON string."""
        total_deps = sum(r.total for r in results)
        total_outdated = sum(r.outdated_count for r in results)

        payload = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "summary": {
                "total_dependencies": total_deps,
                "total_outdated": total_outdated,
                "files_scanned": len(results),
            },
            "results": [self._render_result(r) for r in results],
        }
        return json.dumps(payload, indent=self.indent)

    def _render_result(self, result: DetectionResult) -> dict:
        """Convert a single DetectionResult to a serialisable dict."""
        return {
            "file": result.manifest_path,
            "ecosystem": result.ecosystem,
            "total": result.total,
            "outdated": result.outdated_count,
            "dependencies": [
                {
                    "name": dep.name,
                    "current_version": dep.current_version,
                    "latest_version": dep.latest_version,
                    "outdated": dep.outdated,
                }
                for dep in result.dependencies
            ],
        }
