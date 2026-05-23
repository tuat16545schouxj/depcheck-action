"""Tests for DatadogReporter."""
from __future__ import annotations

import json
import unittest
from unittest.mock import MagicMock, patch

from src.detectors.base import Dependency, DetectionResult
from src.reporters.datadog_reporter import DatadogReporter, _sanitize


def _dep(name: str, current: str, latest: str) -> Dependency:
    return Dependency(name=name, current_version=current, latest_version=latest)


def _make_result(eco: str = "python") -> DetectionResult:
    return DetectionResult(
        ecosystem=eco,
        manifest="requirements.txt",
        dependencies=[
            _dep("requests", "2.28.0", "2.31.0"),
            _dep("flask", "2.3.0", "2.3.0"),
        ],
    )


class TestDatadogReporter(unittest.TestCase):
    def setUp(self) -> None:
        self.reporter = DatadogReporter(post=False)
        self.result = _make_result()

    def _parse(self) -> dict:
        return json.loads(self.reporter.render([self.result]))

    def test_render_returns_string(self) -> None:
        self.assertIsInstance(self.reporter.render([self.result]), str)

    def test_output_is_valid_json(self) -> None:
        data = self._parse()
        self.assertIn("series", data)

    def test_series_contains_total_metric(self) -> None:
        series = self._parse()["series"]
        names = [s["metric"] for s in series]
        self.assertIn("depcheck.total", names)

    def test_series_contains_outdated_metric(self) -> None:
        series = self._parse()["series"]
        names = [s["metric"] for s in series]
        self.assertIn("depcheck.outdated", names)

    def test_series_contains_outdated_pct_metric(self) -> None:
        series = self._parse()["series"]
        names = [s["metric"] for s in series]
        self.assertIn("depcheck.outdated_pct", names)

    def test_total_value_is_correct(self) -> None:
        series = {s["metric"]: s for s in self._parse()["series"]}
        self.assertEqual(series["depcheck.total"]["points"][0][1], 2)

    def test_outdated_value_is_correct(self) -> None:
        series = {s["metric"]: s for s in self._parse()["series"]}
        self.assertEqual(series["depcheck.outdated"]["points"][0][1], 1)

    def test_outdated_pct_value(self) -> None:
        series = {s["metric"]: s for s in self._parse()["series"]}
        self.assertAlmostEqual(series["depcheck.outdated_pct"]["points"][0][1], 50.0)

    def test_tag_contains_ecosystem(self) -> None:
        series = self._parse()["series"]
        for s in series:
            self.assertIn("ecosystem:python", s["tags"])

    def test_no_pct_metric_when_no_dependencies(self) -> None:
        empty = DetectionResult(ecosystem="go", manifest="go.mod", dependencies=[])
        reporter = DatadogReporter(post=False)
        data = json.loads(reporter.render([empty]))
        names = [s["metric"] for s in data["series"]]
        self.assertNotIn("depcheck.outdated_pct", names)

    def test_post_called_when_api_key_set(self) -> None:
        reporter = DatadogReporter(api_key="test-key", post=True)
        with patch.object(reporter, "_send") as mock_send:
            reporter.render([self.result])
            mock_send.assert_called_once()

    def test_post_not_called_without_api_key(self) -> None:
        reporter = DatadogReporter(api_key=None, post=True)
        with patch.object(reporter, "_send") as mock_send:
            reporter.render([self.result])
            mock_send.assert_not_called()

    def test_sanitize_replaces_spaces(self) -> None:
        self.assertEqual(_sanitize("My Eco"), "my_eco")

    def test_sanitize_replaces_hyphens(self) -> None:
        self.assertEqual(_sanitize("node-js"), "node_js")
