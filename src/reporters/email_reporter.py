"""Email reporter: renders a plain-text e-mail body and optionally sends it
via SMTP using environment variables for configuration."""
from __future__ import annotations

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List

from src.detectors.registry import DetectionResult


class EmailReporter:
    """Render detection results as an e-mail and (optionally) send it."""

    SUBJECT = "[depcheck] Outdated dependency report"

    def __init__(
        self,
        smtp_host: str = "",
        smtp_port: int = 587,
        smtp_user: str = "",
        smtp_password: str = "",
        sender: str = "",
        recipients: List[str] | None = None,
        use_tls: bool = True,
    ) -> None:
        self.smtp_host = smtp_host or os.getenv("SMTP_HOST", "")
        self.smtp_port = smtp_port or int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = smtp_user or os.getenv("SMTP_USER", "")
        self.smtp_password = smtp_password or os.getenv("SMTP_PASSWORD", "")
        self.sender = sender or os.getenv("SMTP_SENDER", self.smtp_user)
        self.recipients: List[str] = recipients or [
            r.strip() for r in os.getenv("SMTP_RECIPIENTS", "").split(",") if r.strip()
        ]
        self.use_tls = use_tls

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def render(self, results: List[DetectionResult], send: bool = False) -> str:
        """Return the plain-text body.  If *send* is True, also dispatch it."""
        body = self._build_body(results)
        if send:
            self._send(body)
        return body

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _build_body(self, results: List[DetectionResult]) -> str:
        lines: List[str] = ["Dependency Audit Report", "=" * 40, ""]
        total_outdated = sum(len(r.outdated) for r in results)
        total_deps = sum(len(r.dependencies) for r in results)
        lines.append(f"Total dependencies checked : {total_deps}")
        lines.append(f"Outdated                   : {total_outdated}")
        lines.append("")
        for result in results:
            if not result.outdated:
                continue
            lines.append(f"[{result.ecosystem}] {result.manifest_path}")
            lines.append("-" * 36)
            for dep in result.outdated:
                lines.append(
                    f"  {dep.name:<30} {dep.current_version!s:<15} -> {dep.latest_version}"
                )
            lines.append("")
        if total_outdated == 0:
            lines.append("All dependencies are up to date.")
        return "\n".join(lines)

    def _send(self, body: str) -> None:
        if not self.smtp_host or not self.recipients:
            raise ValueError("SMTP host and at least one recipient are required to send e-mail.")
        msg = MIMEMultipart("alternative")
        msg["Subject"] = self.SUBJECT
        msg["From"] = self.sender
        msg["To"] = ", ".join(self.recipients)
        msg.attach(MIMEText(body, "plain"))
        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            if self.use_tls:
                server.starttls()
            if self.smtp_user and self.smtp_password:
                server.login(self.smtp_user, self.smtp_password)
            server.sendmail(self.sender, self.recipients, msg.as_string())
