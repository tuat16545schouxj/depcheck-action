"""Tests for JsonReporter."""

import json
import unittest

from src.detectors.base import Dependency, DetectionResult
from src.reporters.json_reporter import JsonReporter


class TestJsonReporter(unittest.TestCase):
    def setUp(self):
        self.reporter = JsonReporter()
        dep_outdated = Dependency(name="requests", current_version="2.26.0", latest_version="2.31.0")
        dep_current = Dependency(name="flask", current_version="3.0.0", latest_version="3.0.0")
        self.result = DetectionResult(
            manifest_path="requirements.txt",
            ecosystem="python",
            dependencies=[dep_outdated, dep_current],
        )

    def _parse(self, results=None) -> dict:
        if results is None:
            results = [self.result]
        return json.loads(self.reporter.render(results))

    def test_output_is_valid_json(self):
        raw = self.reporter.render([self.result])
        parsed = json.loads(raw)
        self.assertIsInstance(parsed, dict)

    def test_summary_total_dependencies(self):
        data = self._parse()
        self.assertEqual(data["summary"]["total_dependencies"], 2)

    def test_summary_total_outdated(self):
        data = self._parse()
        self.assertEqual(data["summary"]["total_outdated"], 1)

    def test_summary_files_scanned(self):
        data = self._parse()
        self.assertEqual(data["summary"]["files_scanned"], 1)

    def test_result_ecosystem(self):
        data = self._parse()
        self.assertEqual(data["results"][0]["ecosystem"], "python")

    def test_result_file_path(self):
        data = self._parse()
        self.assertEqual(data["results"][0]["file"], "requirements.txt")

    def test_dependency_outdated_flag(self):
        data = self._parse()
        deps = {d["name"]: d for d in data["results"][0]["dependencies"]}
        self.assertTrue(deps["requests"]["outdated"])
        self.assertFalse(deps["flask"]["outdated"])

    def test_generated_at_present(self):
        data = self._parse()
        self.assertIn("generated_at", data)
        self.assertTrue(data["generated_at"].endswith("+00:00"))

    def test_multiple_results_aggregated(self):
        dep2 = Dependency(name="lodash", current_version="4.17.20", latest_version="4.17.21")
        result2 = DetectionResult(
            manifest_path="package.json",
            ecosystem="node",
            dependencies=[dep2],
        )
        data = self._parse(results=[self.result, result2])
        self.assertEqual(data["summary"]["files_scanned"], 2)
        self.assertEqual(data["summary"]["total_outdated"], 2)

    def test_indent_respected(self):
        reporter_compact = JsonReporter(indent=None)
        raw = reporter_compact.render([self.result])
        self.assertNotIn("\n", raw)


if __name__ == "__main__":
    unittest.main()
