"""Graphite/StatsD plaintext metrics reporter.

Emits one metric line per dependency in the Graphite plaintext protocol::

    depcheck.<ecosystem>.<name>.outdated 1 <timestamp>
    depcheck.<ecosystem>.<name>.current_version 0 <timestamp>

When *host* and *port* are supplied the reporter also pushes the metrics
over a TCP socket; otherwise it just returns the plaintext payload so it
can be piped to another tool.
"""

from __future__ import annotations

import socket
import time
from typing import List, Optional

from src.detectors.base import DetectionResult


class GraphiteReporter:
    """Render detection results as Graphite plaintext metrics."""

    def __init__(
        self,
        host: Optional[str] = None,
        port: int = 2003,
        prefix: str = "depcheck",
        timestamp: Optional[int] = None,
    ) -> None:
        self.host = host
        self.port = port
        self.prefix = prefix.rstrip(".")
        self._timestamp = timestamp  # allow injection for tests

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def render(self, results: List[DetectionResult]) -> str:
        """Return Graphite plaintext payload and optionally push it."""
        ts = self._timestamp if self._timestamp is not None else int(time.time())
        lines: List[str] = []
        for result in results:
            lines.extend(self._render_result(result, ts))
        payload = "\n".join(lines) + ("\n" if lines else "")
        if self.host:
            self._push(payload)
        return payload

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _render_result(self, result: DetectionResult, ts: int) -> List[str]:
        eco = self._sanitize(result.ecosystem)
        lines: List[str] = []
        for dep in result.dependencies:
            name = self._sanitize(dep.name)
            outdated_val = 1 if dep.outdated else 0
            lines.append(f"{self.prefix}.{eco}.{name}.outdated {outdated_val} {ts}")
        # summary gauge per ecosystem
        total = len(result.dependencies)
        outdated = sum(1 for d in result.dependencies if d.outdated)
        lines.append(f"{self.prefix}.{eco}.summary.total {total} {ts}")
        lines.append(f"{self.prefix}.{eco}.summary.outdated {outdated} {ts}")
        return lines

    @staticmethod
    def _sanitize(value: str) -> str:
        """Replace characters illegal in Graphite metric paths."""
        return value.replace(" ", "_").replace("/", ".").replace("-", "_").lower()

    def _push(self, payload: str) -> None:
        """Send *payload* to the Graphite TCP endpoint."""
        with socket.create_connection((self.host, self.port), timeout=5) as sock:
            sock.sendall(payload.encode("utf-8"))
