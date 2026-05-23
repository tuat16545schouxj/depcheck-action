"""DataDog reporter – emits dependency metrics as DogStatsD / Datadog API series."""
from __future__ import annotations

import json
import time
import urllib.request
from typing import List, Optional

from src.detectors.base import DetectionResult


class DatadogReporter:
    """Render detection results as Datadog metric series (JSON) and optionally POST them."""

    METRIC_PREFIX = "depcheck"

    def __init__(
        self,
        api_key: Optional[str] = None,
        app_key: Optional[str] = None,
        host: str = "depcheck-action",
        post: bool = True,
    ) -> None:
        self._api_key = api_key
        self._app_key = app_key
        self._host = host
        self._post = post

    def render(self, results: List[DetectionResult]) -> str:
        """Return a JSON string of Datadog metric series; POST if credentials are set."""
        now = int(time.time())
        series: list = []
        for result in results:
            eco = _sanitize(result.ecosystem)
            total = len(result.dependencies)
            outdated = sum(1 for d in result.dependencies if d.outdated)
            series.append(self._gauge(f"{self.METRIC_PREFIX}.total", total, now, eco))
            series.append(self._gauge(f"{self.METRIC_PREFIX}.outdated", outdated, now, eco))
            if total:
                pct = round(outdated / total * 100, 2)
                series.append(self._gauge(f"{self.METRIC_PREFIX}.outdated_pct", pct, now, eco))

        payload = json.dumps({"series": series}, indent=2)
        if self._post and self._api_key:
            self._send(payload)
        return payload

    def _gauge(
        self, metric: str, value: float, ts: int, ecosystem: str
    ) -> dict:
        return {
            "metric": metric,
            "type": "gauge",
            "points": [[ts, value]],
            "host": self._host,
            "tags": [f"ecosystem:{ecosystem}"],
        }

    def _send(self, payload: str) -> None:
        url = "https://api.datadoghq.com/api/v1/series"
        headers = {
            "Content-Type": "application/json",
            "DD-API-KEY": self._api_key or "",
        }
        if self._app_key:
            headers["DD-APPLICATION-KEY"] = self._app_key
        req = urllib.request.Request(
            url, data=payload.encode(), headers=headers, method="POST"
        )
        with urllib.request.urlopen(req, timeout=10) as resp:  # noqa: S310
            resp.read()


def _sanitize(value: str) -> str:
    return value.lower().replace(" ", "_").replace("-", "_")
