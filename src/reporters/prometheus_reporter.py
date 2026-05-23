"""Prometheus / OpenMetrics text-format reporter.

Outputs dependency metrics in the Prometheus exposition format so that
a Prometheus scrape endpoint or push-gateway can ingest them.
"""
from __future__ import annotations

import time
from typing import List

from src.detectors.base import DetectionResult


class PrometheusReporter:
    """Render detection results as Prometheus text-format metrics."""

    METRIC_PREFIX = "depcheck"

    def __init__(self, timestamp: bool = True) -> None:
        """Args:
            timestamp: When True, append the current Unix ms timestamp to
                       every sample (makes metrics valid for push-gateway).
        """
        self._timestamp = timestamp

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def render(self, results: List[DetectionResult]) -> str:
        lines: List[str] = []
        ts = f" {int(time.time() * 1000)}" if self._timestamp else ""

        lines += self._gauge(
            "dependencies_total",
            "Total number of dependencies detected across all ecosystems.",
            [(sum(len(r.dependencies) for r in results), {}, ts)],
        )

        lines += self._gauge(
            "outdated_total",
            "Total number of outdated dependencies detected across all ecosystems.",
            [(sum(len(r.outdated) for r in results), {}, ts)],
        )

        per_eco: List[tuple] = []
        per_eco_outdated: List[tuple] = []
        for result in results:
            labels = {"ecosystem": result.ecosystem, "manifest": result.manifest_path}
            per_eco.append((len(result.dependencies), labels, ts))
            per_eco_outdated.append((len(result.outdated), labels, ts))

        lines += self._gauge(
            "dependencies_by_ecosystem",
            "Number of dependencies per ecosystem manifest.",
            per_eco,
        )
        lines += self._gauge(
            "outdated_by_ecosystem",
            "Number of outdated dependencies per ecosystem manifest.",
            per_eco_outdated,
        )

        return "\n".join(lines) + "\n"

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _gauge(self, name: str, help_text: str, samples: list) -> List[str]:
        full_name = f"{self.METRIC_PREFIX}_{name}"
        out = [
            f"# HELP {full_name} {help_text}",
            f"# TYPE {full_name} gauge",
        ]
        for value, labels, ts in samples:
            label_str = self._label_str(labels)
            out.append(f"{full_name}{label_str} {value}{ts}")
        return out

    @staticmethod
    def _label_str(labels: dict) -> str:
        if not labels:
            return ""
        parts = [f'{k}="{v}"' for k, v in labels.items()]
        return "{" + ",".join(parts) + "}"
