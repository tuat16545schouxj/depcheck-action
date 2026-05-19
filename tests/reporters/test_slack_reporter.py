"""Tests for SlackReporter."""

from __future__ import annotations

import json
import unittest
from unittest.mock import MagicMock, patch

from src.reporters.slack_reporter import SlackReporter
from src.detectors.base import Dependency, DetectionResult


def _make_result(
    ecosystem: str,
    manifest: str,
    deps: list[tuple[str, str, str]],
) -> DetectionResult:
    """Helper: build a DetectionResult from (name, current, latest) tuples."""
    dependencies = [
        Dependency(name=n, current_version=c, latest_version=l)
        for n, c, l in deps
    ]
    return DetectionResult(
        ecosystem=ecosystem,
        manifest_path=manifest,
        dependencies=dependencies,
    )


class TestSlackReporter(unittest.TestCase):

    def setUp(self) -> None:
        self.webhook = "https://hooks.slack.com/services/TEST/WEBHOOK"
        self.reporter = SlackReporter(webhook_url=self.webhook)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _render_no_post(self, results):
        """Call render() with _post stubbed out; return parsed payload."""
        with patch.object(self.reporter, "_post"):
            raw = self.reporter.render(results)
        return json.loads(raw)

    # ------------------------------------------------------------------
    # Tests
    # ------------------------------------------------------------------

    def test_render_returns_valid_json(self):
        payload = self._render_no_post([])
        self.assertIsInstance(payload, dict)

    def test_payload_contains_blocks(self):
        payload = self._render_no_post([])
        self.assertIn("blocks", payload)
        self.assertIsInstance(payload["blocks"], list)

    def test_header_block_present(self):
        payload = self._render_no_post([])
        types = [b["type"] for b in payload["blocks"]]
        self.assertIn("header", types)

    def test_summary_counts_outdated(self):
        result = _make_result(
            "python", "requirements.txt",
            [("requests", "2.28.0", "2.31.0"), ("flask", "2.0.0", "2.0.0")],
        )
        payload = self._render_no_post([result])
        summary_block = payload["blocks"][1]["text"]["text"]
        self.assertIn("1", summary_block)   # 1 outdated
        self.assertIn("2", summary_block)   # 2 total

    def test_outdated_dep_appears_in_blocks(self):
        result = _make_result(
            "node", "package.json",
            [("lodash", "4.17.19", "4.17.21")],
        )
        payload = self._render_no_post([result])
        all_text = json.dumps(payload)
        self.assertIn("lodash", all_text)
        self.assertIn("4.17.19", all_text)
        self.assertIn("4.17.21", all_text)

    def test_up_to_date_dep_omitted_from_ecosystem_block(self):
        result = _make_result(
            "python", "requirements.txt",
            [("boto3", "1.26.0", "1.26.0")],
        )
        payload = self._render_no_post([result])
        # Only header + summary + divider — no ecosystem section block
        self.assertEqual(len(payload["blocks"]), 3)

    def test_channel_included_when_set(self):
        reporter = SlackReporter(webhook_url=self.webhook, channel="#deps")
        with patch.object(reporter, "_post"):
            raw = reporter.render([])
        payload = json.loads(raw)
        self.assertEqual(payload["channel"], "#deps")

    def test_channel_absent_when_not_set(self):
        payload = self._render_no_post([])
        self.assertNotIn("channel", payload)

    def test_post_called_once(self):
        with patch.object(self.reporter, "_post") as mock_post:
            self.reporter.render([])
        mock_post.assert_called_once()

    def test_post_raises_on_bad_status(self):
        mock_resp = MagicMock()
        mock_resp.status = 500
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        with patch("urllib.request.urlopen", return_value=mock_resp):
            with self.assertRaises(RuntimeError):
                self.reporter._post('{"blocks":[]}')


if __name__ == "__main__":
    unittest.main()
