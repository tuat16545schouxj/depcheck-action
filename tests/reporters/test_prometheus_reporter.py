"""Tests for PrometheusReporter."""
from __future__ import annotations

import re
import unittest

from src.detectors.base import Dependency, DetectionResult
from src.reporters.prometheus_reporter import PrometheusReporter


def _dep(name: str, current: str, latest: str) -> Dependency:
    return Dependency(name=name, current_version=current, latest_version=latest, ecosystem="test")


def _make_result(
    ecosystem: str = "python",
    manifest: str = "requirements.txt",
    deps=None,
) -> DetectionResult:
    if deps is None:
        deps = [_dep("requests", "2.28.0", "2.31.0"), _dep("flask", "2.3.0", "2.3.0")]
    return DetectionResult(ecosystem=ecosystem, manifest_path=manifest, dependencies=deps)


class TestPrometheusReporter(unittest.TestCase):
    def setUp(self):
        self.reporter = PrometheusReporter(timestamp=False)
        self.result = _make_result()
        self.output = self.reporter.render([self.result])

    # --- format checks ---

    def test_render_returns_string(self):
        self.assertIsInstance(self.output, str)

    def test_output_ends_with_newline(self):
        self.assertTrue(self.output.endswith("\n"))

    def test_help_lines_present(self):
        self.assertIn("# HELP depcheck_dependencies_total", self.output)
        self.assertIn("# HELP depcheck_outdated_total", self.output)

    def test_type_lines_are_gauge(self):
        for line in self.output.splitlines():
            if line.startswith("# TYPE"):
                self.assertIn("gauge", line)

    # --- value checks ---

    def test_total_dependencies_value(self):
        match = re.search(r"depcheck_dependencies_total (\d+)", self.output)
        self.assertIsNotNone(match)
        self.assertEqual(int(match.group(1)), 2)

    def test_total_outdated_value(self):
        match = re.search(r"depcheck_outdated_total (\d+)", self.output)
        self.assertIsNotNone(match)
        # only requests is outdated
        self.assertEqual(int(match.group(1)), 1)

    def test_ecosystem_label_present(self):
        self.assertIn('ecosystem="python"', self.output)

    def test_manifest_label_present(self):
        self.assertIn('manifest="requirements.txt"', self.output)

    # --- timestamp behaviour ---

    def test_no_timestamp_when_disabled(self):
        for line in self.output.splitlines():
            if line.startswith("#") or not line.strip():
                continue
            # metric lines should end with the numeric value, no trailing int
            parts = line.rsplit(" ", 1)
            # last token must be the float/int value only (no second space-sep number)
            self.assertEqual(len(parts), 2, msg=f"Unexpected extra token in: {line}")

    def test_timestamp_appended_when_enabled(self):
        reporter_ts = PrometheusReporter(timestamp=True)
        output = reporter_ts.render([self.result])
        metric_lines = [
            l for l in output.splitlines()
            if l and not l.startswith("#")
        ]
        for line in metric_lines:
            parts = line.split(" ")
            self.assertEqual(len(parts), 3, msg=f"Expected 3 tokens in: {line}")
            self.assertTrue(parts[2].isdigit(), msg=f"Timestamp not numeric: {line}")

    # --- multiple results ---

    def test_multiple_results_sum(self):
        r2 = _make_result(ecosystem="node", manifest="package.json",
                          deps=[_dep("lodash", "4.17.20", "4.17.21")])
        out = self.reporter.render([self.result, r2])
        match = re.search(r"depcheck_dependencies_total (\d+)", out)
        self.assertEqual(int(match.group(1)), 3)


if __name__ == "__main__":
    unittest.main()
