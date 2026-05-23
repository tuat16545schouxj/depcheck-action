"""Badge reporter: emits a Shields.io-compatible JSON endpoint for dependency health."""
from __future__ import annotations

import json
from typing import List

from src.detectors.registry import DetectionResult


class BadgeReporter:
    """Produces a Shields.io endpoint JSON payload summarising dependency health."""

    # Colour thresholds (outdated / total ratio)
    _THRESHOLDS = [
        (0.0, "brightgreen"),
        (0.1, "green"),
        (0.25, "yellow"),
        (0.5, "orange"),
        (1.01, "red"),
    ]

    def __init__(self, *, label: str = "dependencies") -> None:
        self.label = label

    # ------------------------------------------------------------------
    def render(self, results: List[DetectionResult]) -> str:
        total = sum(len(r.dependencies) for r in results)
        outdated = sum(
            sum(1 for d in r.dependencies if d.outdated) for r in results
        )

        ratio = outdated / total if total else 0.0
        color = self._color(ratio)

        if total == 0:
            message = "unknown"
            color = "lightgrey"
        elif outdated == 0:
            message = "up to date"
        else:
            message = f"{outdated} outdated"

        payload = {
            "schemaVersion": 1,
            "label": self.label,
            "message": message,
            "color": color,
            "namedLogo": "dependabot",
        }
        return json.dumps(payload, indent=2)

    # ------------------------------------------------------------------
    def _color(self, ratio: float) -> str:
        for threshold, color in self._THRESHOLDS:
            if ratio <= threshold:
                return color
        return "red"
