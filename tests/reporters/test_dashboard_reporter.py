"""Tests for DashboardReporter."""
import unittest
from unittest.mock import MagicMock

from src.reporters.dashboard_reporter import DashboardReporter
from src.detectors.base import Dependency, DetectionResult


def _dep(name: str, current: str, latest: str) -> Dependency:
    d = Dependency(name=name, current_version=current, latest_version=latest, ecosystem="test")
    return d


def _make_result(ecosystem: str, deps) -> DetectionResult:
    r = MagicMock(spec=DetectionResult)
    r.ecosystem = ecosystem
    r.dependencies = deps
    return r


class TestDashboardReporter(unittest.TestCase):
    def setUp(self):
        self.reporter = DashboardReporter()
        self.results = [
            _make_result("python", [_dep("requests", "2.28.0", "2.31.0"), _dep("flask", "2.3.0", "2.3.0")]),
            _make_result("node", [_dep("lodash", "4.17.20", "4.17.21")]),
        ]

    def _render(self):
        return self.reporter.render(self.results)

    def test_render_returns_string(self):
        self.assertIsInstance(self._render(), str)

    def test_render_contains_doctype(self):
        self.assertIn("<!DOCTYPE html>", self._render())

    def test_render_contains_title(self):
        self.assertIn("Dependency Health Dashboard", self._render())

    def test_render_shows_ecosystems(self):
        html = self._render()
        self.assertIn("python", html)
        self.assertIn("node", html)

    def test_render_shows_total_count(self):
        html = self._render()
        self.assertIn("3", html)  # total deps across both ecosystems

    def test_render_shows_outdated_count(self):
        html = self._render()
        # requests and lodash are outdated
        self.assertIn("2", html)

    def test_render_empty_results(self):
        html = self.reporter.render([])
        self.assertIn("100.0% up-to-date", html)

    def test_render_all_outdated_score_color(self):
        results = [_make_result("go", [_dep("gin", "1.0", "2.0"), _dep("cobra", "1.0", "2.0")])]
        html = self.reporter.render(results)
        self.assertIn("#e74c3c", html)

    def test_render_all_current_score_color(self):
        results = [_make_result("rust", [_dep("serde", "1.0.0", "1.0.0")])]
        html = self.reporter.render(results)
        self.assertIn("#2ecc71", html)

    def test_render_contains_chart_data_json(self):
        html = self._render()
        self.assertIn("const data =", html)
        self.assertIn('"python"', html)

    def test_score_color_boundaries(self):
        self.assertEqual(DashboardReporter._score_color(100), "#2ecc71")
        self.assertEqual(DashboardReporter._score_color(80), "#f39c12")
        self.assertEqual(DashboardReporter._score_color(50), "#e74c3c")


if __name__ == "__main__":
    unittest.main()
