"""Tests for TeamCityReporter."""

from __future__ import annotations

import unittest

from src.detectors.base import Dependency, DetectionResult
from src.reporters.teamcity_reporter import TeamCityReporter


def _dep(name: str, current: str, latest: str) -> Dependency:
    d = Dependency(name=name, current_version=current, latest_version=latest)
    return d


def _make_result(ecosystem: str = "python") -> DetectionResult:
    return DetectionResult(
        ecosystem=ecosystem,
        manifest="requirements.txt",
        dependencies=[
            _dep("requests", "2.28.0", "2.31.0"),
            _dep("flask", "2.3.0", "2.3.0"),
        ],
    )


class TestTeamCityReporter(unittest.TestCase):
    def setUp(self) -> None:
        self.reporter = TeamCityReporter()
        self.result = _make_result()

    def _lines(self, results=None) -> list[str]:
        if results is None:
            results = [self.result]
        return self.reporter.render(results).splitlines()

    def test_render_returns_string(self) -> None:
        out = self.reporter.render([self.result])
        self.assertIsInstance(out, str)

    def test_outer_suite_opened_and_closed(self) -> None:
        lines = self._lines()
        self.assertTrue(any("testSuiteStarted" in l and "depcheck" in l for l in lines))
        self.assertTrue(any("testSuiteFinished" in l and "depcheck" in l for l in lines))

    def test_ecosystem_suite_opened_and_closed(self) -> None:
        lines = self._lines()
        self.assertTrue(any("testSuiteStarted" in l and "python" in l for l in lines))
        self.assertTrue(any("testSuiteFinished" in l and "python" in l for l in lines))

    def test_outdated_dep_emits_test_failed(self) -> None:
        lines = self._lines()
        failed = [l for l in lines if "testFailed" in l]
        self.assertEqual(len(failed), 1)
        self.assertIn("requests", failed[0])

    def test_up_to_date_dep_does_not_emit_test_failed(self) -> None:
        lines = self._lines()
        failed = [l for l in lines if "testFailed" in l]
        self.assertFalse(any("flask" in l for l in failed))

    def test_build_statistic_total(self) -> None:
        lines = self._lines()
        stat = [l for l in lines if "depcheck.total" in l]
        self.assertEqual(len(stat), 1)
        self.assertIn("value='2'", stat[0])

    def test_build_statistic_outdated(self) -> None:
        lines = self._lines()
        stat = [l for l in lines if "depcheck.outdated" in l]
        self.assertEqual(len(stat), 1)
        self.assertIn("value='1'", stat[0])

    def test_escape_pipe_character(self) -> None:
        escaped = self.reporter._escape("a|b")
        self.assertEqual(escaped, "a||b")

    def test_escape_newline(self) -> None:
        escaped = self.reporter._escape("a\nb")
        self.assertEqual(escaped, "a|nb")

    def test_empty_results(self) -> None:
        out = self.reporter.render([])
        self.assertIn("testSuiteStarted", out)
        self.assertIn("depcheck.total", out)
        self.assertIn("value='0'", out)

    def test_multiple_ecosystems(self) -> None:
        r1 = _make_result("python")
        r2 = _make_result("node")
        lines = self._lines([r1, r2])
        self.assertTrue(any("python" in l and "testSuiteStarted" in l for l in lines))
        self.assertTrue(any("node" in l and "testSuiteStarted" in l for l in lines))


if __name__ == "__main__":
    unittest.main()
