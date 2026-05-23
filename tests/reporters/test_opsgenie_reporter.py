"""Tests for OpsGenieReporter."""
from __future__ import annotations

import json
import unittest
from unittest.mock import MagicMock, patch

from src.detectors.base import Dependency, DetectionResult
from src.reporters.opsgenie_reporter import OpsGenieReporter


def _dep(name: str, current: str, latest: str) -> Dependency:
    return Dependency(name=name, current_version=current, latest_version=latest)


def _make_result(ecosystem: str, deps) -> DetectionResult:
    return DetectionResult(ecosystem=ecosystem, manifest="manifest.txt", dependencies=deps)


class TestOpsGenieReporter(unittest.TestCase):
    def setUp(self):
        self.reporter = OpsGenieReporter(api_key="test-key", team="platform", dry_run=True)
        self.outdated_result = _make_result(
            "python", [_dep("requests", "2.28.0", "2.31.0"), _dep("flask", "2.0.0", "3.0.0")]
        )
        self.uptodate_result = _make_result(
            "node", [_dep("lodash", "4.17.21", "4.17.21")]
        )

    def _parse(self, result):
        return json.loads(self.reporter.render(result))

    def test_render_returns_valid_json(self):
        out = self.reporter.render([self.outdated_result])
        data = json.loads(out)
        self.assertIn("alerts_sent", data)

    def test_dry_run_flag_in_output(self):
        data = self._parse([self.outdated_result])
        self.assertTrue(data["dry_run"])

    def test_alerts_sent_count_matches_outdated_results(self):
        data = self._parse([self.outdated_result, self.outdated_result])
        self.assertEqual(data["alerts_sent"], 2)

    def test_uptodate_result_produces_no_alert(self):
        data = self._parse([self.uptodate_result])
        self.assertEqual(data["alerts_sent"], 0)

    def test_build_payload_message_contains_ecosystem(self):
        payload = self.reporter._build_payload(self.outdated_result)
        self.assertIn("python", payload["message"])

    def test_build_payload_includes_outdated_count(self):
        payload = self.reporter._build_payload(self.outdated_result)
        self.assertIn("2", payload["message"])

    def test_build_payload_alias_is_stable(self):
        p1 = self.reporter._build_payload(self.outdated_result)
        p2 = self.reporter._build_payload(self.outdated_result)
        self.assertEqual(p1["alias"], p2["alias"])

    def test_build_payload_responders_when_team_set(self):
        payload = self.reporter._build_payload(self.outdated_result)
        self.assertEqual(payload["responders"][0]["name"], "platform")

    def test_build_payload_no_responders_when_team_none(self):
        r = OpsGenieReporter(api_key="k", dry_run=True)
        payload = r._build_payload(self.outdated_result)
        self.assertNotIn("responders", payload)

    def test_build_payload_priority_respected(self):
        r = OpsGenieReporter(api_key="k", priority="P1", dry_run=True)
        payload = r._build_payload(self.outdated_result)
        self.assertEqual(payload["priority"], "P1")

    def test_post_called_when_not_dry_run(self):
        r = OpsGenieReporter(api_key="k", dry_run=False)
        with patch.object(r, "_post") as mock_post:
            r.render([self.outdated_result])
            mock_post.assert_called_once()

    def test_post_not_called_in_dry_run(self):
        with patch.object(self.reporter, "_post") as mock_post:
            self.reporter.render([self.outdated_result])
            mock_post.assert_not_called()
