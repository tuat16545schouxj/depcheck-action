"""OpsGenie alert reporter — posts an alert per outdated dependency group."""
from __future__ import annotations

import json
import urllib.request
import urllib.error
from typing import List, Optional

from src.detectors.base import DetectionResult


class OpsGenieReporter:
    """Send dependency-audit results to OpsGenie as alerts."""

    _API_URL = "https://api.opsgenie.com/v2/alerts"

    def __init__(
        self,
        api_key: str,
        team: Optional[str] = None,
        priority: str = "P3",
        dry_run: bool = False,
    ) -> None:
        self._api_key = api_key
        self._team = team
        self._priority = priority
        self._dry_run = dry_run

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def render(self, results: List[DetectionResult]) -> str:
        """Build alert payloads and (unless dry_run) post them; return JSON summary."""
        outdated = [r for r in results if r.outdated]
        alerts: list = []
        for result in outdated:
            payload = self._build_payload(result)
            alerts.append(payload)
            if not self._dry_run:
                self._post(payload)
        return json.dumps({"alerts_sent": len(alerts), "dry_run": self._dry_run}, indent=2)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _build_payload(self, result: DetectionResult) -> dict:
        outdated_names = ", ".join(d.name for d in result.outdated)
        payload: dict = {
            "message": f"[depcheck] {len(result.outdated)} outdated dep(s) in {result.ecosystem}",
            "alias": f"depcheck-{result.ecosystem}",
            "description": (
                f"Outdated packages detected in **{result.ecosystem}** "
                f"({result.manifest}):\n{outdated_names}"
            ),
            "priority": self._priority,
            "tags": ["depcheck", result.ecosystem],
        }
        if self._team:
            payload["responders"] = [{"name": self._team, "type": "team"}]
        return payload

    def _post(self, payload: dict) -> None:
        data = json.dumps(payload).encode()
        req = urllib.request.Request(
            self._API_URL,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"GenieKey {self._api_key}",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:  # noqa: S310
            resp.read()
