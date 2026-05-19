"""Slack webhook reporter — posts a dependency audit summary to a Slack channel."""

from __future__ import annotations

import json
import urllib.request
from typing import List

from src.detectors.registry import DetectionResult


class SlackReporter:
    """Posts an audit summary as a Slack Block Kit message via an incoming webhook."""

    def __init__(self, webhook_url: str, channel: str | None = None) -> None:
        self.webhook_url = webhook_url
        self.channel = channel

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def render(self, results: List[DetectionResult]) -> str:
        """Build the payload, POST it, and return the JSON payload string."""
        payload = self._build_payload(results)
        serialized = json.dumps(payload)
        self._post(serialized)
        return serialized

    # ------------------------------------------------------------------
    # Payload helpers
    # ------------------------------------------------------------------

    def _build_payload(self, results: List[DetectionResult]) -> dict:
        total = sum(len(r.dependencies) for r in results)
        outdated = sum(
            sum(1 for d in r.dependencies if d.outdated) for r in results
        )

        header_text = (
            f":mag: *depcheck* found *{outdated}* outdated "
            f"out of *{total}* dependencies"
        )

        blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "depcheck Dependency Audit"},
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": header_text},
            },
            {"type": "divider"},
        ]

        for result in results:
            outdated_deps = [d for d in result.dependencies if d.outdated]
            if not outdated_deps:
                continue
            lines = [
                f"*{result.ecosystem}* — `{result.manifest_path}`",
            ]
            for dep in outdated_deps:
                lines.append(
                    f"  • `{dep.name}` {dep.current_version} → {dep.latest_version}"
                )
            blocks.append(
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": "\n".join(lines)},
                }
            )

        payload: dict = {"blocks": blocks}
        if self.channel:
            payload["channel"] = self.channel
        return payload

    # ------------------------------------------------------------------
    # HTTP helper
    # ------------------------------------------------------------------

    def _post(self, payload: str) -> None:
        data = payload.encode("utf-8")
        req = urllib.request.Request(
            self.webhook_url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req) as resp:  # noqa: S310
            if resp.status not in (200, 204):
                raise RuntimeError(
                    f"Slack webhook returned HTTP {resp.status}"
                )
