"""Tests for GraphiteReporter."""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from src.detectors.base import Dependency, DetectionResult
from src.reporters.graphite_reporter import GraphiteReporter

FIXED_TS = 1_700_000_000


def _dep(name: str, current: str, latest: str) -> Dependency:
    return Dependency(name=name, current_version=current, latest_version=latest)


def _make_result(ecosystem: str, deps) -> DetectionResult:
    return DetectionResult(ecosystem=ecosystem, dependencies=deps, manifest="fake")


class TestGraphiteReporter(unittest.TestCase):
    def setUp(self):
        self.reporter = GraphiteReporter(prefix="depcheck", timestamp=FIXED_TS)
        self.result = _make_result(
            "python",
            [
                _dep("requests", "2.28.0", "2.31.0"),
                _dep("flask", "3.0.0", "3.0.0"),
            ],
        )

    def _lines(self, results=None):
        if results is None:
            results = [self.result]
        return self.reporter.render(results).strip().splitlines()

    def test_render_returns_string(self):
        self.assertIsInstance(self.reporter.render([self.result]), str)

    def test_outdated_dep_emits_1(self):
        lines = self._lines()
        matching = [l for l in lines if "requests.outdated" in l]
        self.assertEqual(len(matching), 1)
        self.assertIn(" 1 ", matching[0])

    def test_current_dep_emits_0(self):
        lines = self._lines()
        matching = [l for l in lines if "flask.outdated" in l]
        self.assertEqual(len(matching), 1)
        self.assertIn(" 0 ", matching[0])

    def test_timestamp_appended(self):
        lines = self._lines()
        for line in lines:
            self.assertTrue(line.endswith(str(FIXED_TS)), line)

    def test_summary_total_line(self):
        lines = self._lines()
        total_lines = [l for l in lines if "summary.total" in l]
        self.assertEqual(len(total_lines), 1)
        self.assertIn(" 2 ", total_lines[0])

    def test_summary_outdated_line(self):
        lines = self._lines()
        out_lines = [l for l in lines if "summary.outdated" in l]
        self.assertEqual(len(out_lines), 1)
        self.assertIn(" 1 ", out_lines[0])

    def test_prefix_applied(self):
        reporter = GraphiteReporter(prefix="myapp", timestamp=FIXED_TS)
        payload = reporter.render([self.result])
        self.assertTrue(all(l.startswith("myapp.") for l in payload.strip().splitlines()))

    def test_sanitize_hyphen_and_slash(self):
        result = _make_result("my-eco/test", [_dep("my-pkg", "1.0", "2.0")])
        lines = GraphiteReporter(timestamp=FIXED_TS).render([result]).strip().splitlines()
        for line in lines:
            self.assertNotIn("-", line.split(" ")[0])
            self.assertNotIn(" ", line.split(" ")[0])

    def test_empty_results_returns_empty_string(self):
        payload = self.reporter.render([])
        self.assertEqual(payload, "")

    def test_push_called_when_host_set(self):
        reporter = GraphiteReporter(host="localhost", port=2003, timestamp=FIXED_TS)
        with patch("src.reporters.graphite_reporter.socket.create_connection") as mock_conn:
            mock_sock = MagicMock()
            mock_conn.return_value.__enter__ = lambda s: mock_sock
            mock_conn.return_value.__exit__ = MagicMock(return_value=False)
            reporter.render([self.result])
            mock_conn.assert_called_once_with(("localhost", 2003), timeout=5)

    def test_no_push_without_host(self):
        with patch("src.reporters.graphite_reporter.socket.create_connection") as mock_conn:
            self.reporter.render([self.result])
            mock_conn.assert_not_called()
