"""Tests for JUnitReporter."""
from __future__ import annotations

import unittest
import xml.etree.ElementTree as ET

from src.reporters.junit_reporter import JUnitReporter
from src.detectors.base import DetectionResult, Dependency


def _dep(name: str, current: str, latest: str) -> Dependency:
    return Dependency(name=name, current_version=current, latest_version=latest)


def _make_result(
    ecosystem: str = "python",
    manifest: str = "requirements.txt",
    deps=None,
) -> DetectionResult:
    if deps is None:
        deps = [
            _dep("requests", "2.28.0", "2.31.0"),
            _dep("flask", "2.3.0", "2.3.0"),
        ]
    return DetectionResult(ecosystem=ecosystem, manifest_path=manifest, dependencies=deps)


class TestJUnitReporter(unittest.TestCase):

    def setUp(self):
        self.reporter = JUnitReporter()
        self.result = _make_result()
        self.output = self.reporter.render([self.result])

    def _root(self):
        return ET.fromstring(self.output)

    # --- basic structure ---

    def test_render_returns_string(self):
        self.assertIsInstance(self.output, str)

    def test_root_element_is_testsuites(self):
        self.assertEqual(self._root().tag, "testsuites")

    def test_root_has_name_attribute(self):
        self.assertEqual(self._root().get("name"), "depcheck")

    def test_root_tests_count(self):
        self.assertEqual(self._root().get("tests"), "2")

    def test_root_failures_count(self):
        # only 'requests' is outdated
        self.assertEqual(self._root().get("failures"), "1")

    # --- testsuite element ---

    def test_one_suite_per_result(self):
        suites = self._root().findall("testsuite")
        self.assertEqual(len(suites), 1)

    def test_suite_name_is_ecosystem(self):
        suite = self._root().find("testsuite")
        self.assertEqual(suite.get("name"), "python")

    def test_suite_tests_count(self):
        suite = self._root().find("testsuite")
        self.assertEqual(suite.get("tests"), "2")

    def test_suite_failures_count(self):
        suite = self._root().find("testsuite")
        self.assertEqual(suite.get("failures"), "1")

    # --- testcase elements ---

    def test_two_testcases(self):
        cases = self._root().findall(".//testcase")
        self.assertEqual(len(cases), 2)

    def test_outdated_dep_has_failure_child(self):
        cases = self._root().findall(".//testcase")
        outdated = [c for c in cases if c.get("name") == "requests"]
        self.assertEqual(len(outdated), 1)
        self.assertIsNotNone(outdated[0].find("failure"))

    def test_up_to_date_dep_has_no_failure_child(self):
        cases = self._root().findall(".//testcase")
        ok = [c for c in cases if c.get("name") == "flask"]
        self.assertEqual(len(ok), 1)
        self.assertIsNone(ok[0].find("failure"))

    def test_failure_message_mentions_package(self):
        failure = self._root().find(".//failure")
        self.assertIn("requests", failure.get("message", ""))

    def test_failure_text_contains_versions(self):
        failure = self._root().find(".//failure")
        self.assertIn("2.28.0", failure.text)
        self.assertIn("2.31.0", failure.text)

    # --- multiple results ---

    def test_multiple_results_produce_multiple_suites(self):
        r2 = _make_result(ecosystem="node", manifest="package.json", deps=[
            _dep("lodash", "4.17.20", "4.17.21")
        ])
        output = self.reporter.render([self.result, r2])
        root = ET.fromstring(output)
        self.assertEqual(len(root.findall("testsuite")), 2)


if __name__ == "__main__":
    unittest.main()
