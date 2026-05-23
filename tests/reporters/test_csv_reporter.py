"""Tests for CsvReporter."""
import csv
import io
import unittest

from src.reporters.csv_reporter import CsvReporter
from src.detectors.base import Dependency, DetectionResult


def _make_result(
    ecosystem: str = "python",
    manifest: str = "requirements.txt",
    deps=None,
) -> DetectionResult:
    if deps is None:
        deps = [
            Dependency("requests", "2.28.0", "2.31.0"),
            Dependency("flask", "2.0.0", "2.0.0"),
        ]
    return DetectionResult(ecosystem=ecosystem, manifest_path=manifest, dependencies=deps)


def _parse(csv_text: str):
    return list(csv.reader(io.StringIO(csv_text)))


class TestCsvReporter(unittest.TestCase):
    def setUp(self):
        self.reporter = CsvReporter()

    def test_render_returns_string(self):
        out = self.reporter.render([_make_result()])
        self.assertIsInstance(out, str)

    def test_render_includes_header(self):
        rows = _parse(self.reporter.render([_make_result()]))
        self.assertEqual(rows[0], CsvReporter.COLUMNS)

    def test_render_no_header_option(self):
        reporter = CsvReporter(include_header=False)
        rows = _parse(reporter.render([_make_result()]))
        self.assertNotEqual(rows[0], CsvReporter.COLUMNS)

    def test_render_row_count(self):
        rows = _parse(self.reporter.render([_make_result()]))
        # 1 header + 2 deps
        self.assertEqual(len(rows), 3)

    def test_render_ecosystem_column(self):
        rows = _parse(self.reporter.render([_make_result(ecosystem="node")]))
        self.assertEqual(rows[1][0], "node")

    def test_render_manifest_path_column(self):
        rows = _parse(self.reporter.render([_make_result(manifest="pkg/requirements.txt")]))
        self.assertEqual(rows[1][1], "pkg/requirements.txt")

    def test_render_outdated_flag_true(self):
        rows = _parse(self.reporter.render([_make_result()]))
        # requests is outdated
        self.assertEqual(rows[1][5], "true")

    def test_render_outdated_flag_false(self):
        rows = _parse(self.reporter.render([_make_result()]))
        # flask is up-to-date
        self.assertEqual(rows[2][5], "false")

    def test_render_empty_latest_version(self):
        deps = [Dependency("unknown", "1.0.0", None)]
        rows = _parse(self.reporter.render([_make_result(deps=deps)]))
        self.assertEqual(rows[1][4], "")

    def test_render_multiple_results(self):
        results = [
            _make_result(ecosystem="python"),
            _make_result(ecosystem="node", manifest="package.json"),
        ]
        rows = _parse(self.reporter.render(results))
        # 1 header + 2 + 2
        self.assertEqual(len(rows), 5)

    def test_render_result_helper(self):
        result = _make_result()
        rows = self.reporter._render_result(result)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0][2], "requests")


if __name__ == "__main__":
    unittest.main()
