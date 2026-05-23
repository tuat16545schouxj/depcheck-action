"""InfluxDB line-protocol reporter for depcheck-action."""
from __future__ import annotations

import time
from typing import List, Optional

try:
    import urllib.request as _urllib
except ImportError:  # pragma: no cover
    _urllib = None  # type: ignore

from src.detectors.base import DetectionResult


class InfluxDBReporter:
    """Renders dependency audit results as InfluxDB line-protocol metrics.

    When *url* and *token* are supplied the reporter POSTs the payload to
    the InfluxDB v2 write endpoint; otherwise it simply returns the
    line-protocol string so callers can handle transport themselves.
    """

    MEASUREMENT = "depcheck"

    def __init__(
        self,
        url: Optional[str] = None,
        token: Optional[str] = None,
        org: str = "default",
        bucket: str = "depcheck",
        timestamp: Optional[int] = None,
    ) -> None:
        self._url = url
        self._token = token
        self._org = org
        self._bucket = bucket
        # nanosecond precision timestamp; fixed value useful in tests
        self._ts = timestamp if timestamp is not None else time.time_ns()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def render(self, results: List[DetectionResult]) -> str:
        lines = [self._render_result(r) for r in results]
        payload = "\n".join(lines)
        if self._url and self._token:
            self._send(payload)
        return payload

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _render_result(self, result: DetectionResult) -> str:
        ecosystem = self._escape_tag(result.ecosystem)
        total = len(result.dependencies)
        outdated = sum(1 for d in result.dependencies if d.outdated)
        up_to_date = total - outdated
        return (
            f"{self.MEASUREMENT},ecosystem={ecosystem} "
            f"total={total}i,outdated={outdated}i,up_to_date={up_to_date}i "
            f"{self._ts}"
        )

    @staticmethod
    def _escape_tag(value: str) -> str:
        """Escape special characters in InfluxDB tag values."""
        return value.replace(" ", "\\ ").replace(",", "\\,").replace("=", "\\=")

    def _send(self, payload: str) -> None:
        write_url = (
            f"{self._url.rstrip('/')}/api/v2/write"
            f"?org={self._org}&bucket={self._bucket}&precision=ns"
        )
        data = payload.encode("utf-8")
        req = _urllib.Request(
            write_url,
            data=data,
            headers={
                "Authorization": f"Token {self._token}",
                "Content-Type": "text/plain; charset=utf-8",
            },
            method="POST",
        )
        with _urllib.urlopen(req, timeout=10) as resp:  # noqa: S310
            if resp.status not in (200, 204):
                raise RuntimeError(
                    f"InfluxDB write failed with status {resp.status}"
                )
