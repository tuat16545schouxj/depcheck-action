"""Tests for EmailReporter."""
from __future__ import annotations

import smtplib
import unittest
from unittest.mock import MagicMock, patch

from src.detectors.base import Dependency, DetectionResult
from src.reporters.email_reporter import EmailReporter


def _make_result(
    ecosystem: str = "python",
    manifest: str = "requirements.txt",
    deps: list | None = None,
    outdated: list | None = None,
) -> DetectionResult:
    deps = deps or [
        Dependency("requests", "2.28.0", "2.31.0"),
        Dependency("flask", "2.0.0", "2.0.0"),
    ]
    outdated = outdated or [deps[0]]
    return DetectionResult(
        ecosystem=ecosystem,
        manifest_path=manifest,
        dependencies=deps,
        outdated=outdated,
    )


class TestEmailReporter(unittest.TestCase):
    def setUp(self) -> None:
        self.reporter = EmailReporter()
        self.result = _make_result()

    def _render(self, results=None) -> str:
        return self.reporter.render(results or [self.result])

    # ------------------------------------------------------------------
    # Body content
    # ------------------------------------------------------------------

    def test_render_returns_string(self):
        self.assertIsInstance(self._render(), str)

    def test_render_contains_title(self):
        self.assertIn("Dependency Audit Report", self._render())

    def test_render_shows_total_count(self):
        body = self._render()
        self.assertIn("Total dependencies checked", body)
        self.assertIn("2", body)

    def test_render_shows_outdated_count(self):
        body = self._render()
        self.assertIn("Outdated", body)
        self.assertIn("1", body)

    def test_render_shows_outdated_dep_name(self):
        self.assertIn("requests", self._render())

    def test_render_shows_version_transition(self):
        body = self._render()
        self.assertIn("2.28.0", body)
        self.assertIn("2.31.0", body)

    def test_render_shows_ecosystem(self):
        self.assertIn("python", self._render())

    def test_all_up_to_date_message(self):
        dep = Dependency("flask", "2.0.0", "2.0.0")
        result = DetectionResult(
            ecosystem="python",
            manifest_path="requirements.txt",
            dependencies=[dep],
            outdated=[],
        )
        self.assertIn("up to date", self.reporter.render([result]))

    def test_multiple_ecosystems(self):
        r2 = _make_result(ecosystem="node", manifest="package.json")
        body = self.reporter.render([self.result, r2])
        self.assertIn("python", body)
        self.assertIn("node", body)

    # ------------------------------------------------------------------
    # SMTP dispatch
    # ------------------------------------------------------------------

    def test_send_raises_without_host(self):
        reporter = EmailReporter(smtp_host="", recipients=["a@b.com"])
        with self.assertRaises(ValueError):
            reporter.render([self.result], send=True)

    def test_send_raises_without_recipients(self):
        reporter = EmailReporter(smtp_host="smtp.example.com", recipients=[])
        with self.assertRaises(ValueError):
            reporter.render([self.result], send=True)

    def test_send_calls_smtp(self):
        reporter = EmailReporter(
            smtp_host="smtp.example.com",
            smtp_port=587,
            smtp_user="user",
            smtp_password="pass",
            sender="ci@example.com",
            recipients=["dev@example.com"],
        )
        mock_server = MagicMock()
        mock_server.__enter__ = lambda s: mock_server
        mock_server.__exit__ = MagicMock(return_value=False)
        with patch("smtplib.SMTP", return_value=mock_server) as mock_smtp:
            reporter.render([self.result], send=True)
            mock_smtp.assert_called_once_with("smtp.example.com", 587)
            mock_server.starttls.assert_called_once()
            mock_server.login.assert_called_once_with("user", "pass")
            mock_server.sendmail.assert_called_once()
