"""Tests for XmlReporter."""

from __future__ import annotations

import unittest
import xml.etree.ElementTree as ET

from src.reporters.xml_reporter import XmlReporter
from src.detectors.base import DetectionResult, Dependency


def _make_result(
    ecosystem: str = "python",
    manifest: str = "requirements.txt",
    deps: list | None = None,
) -> DetectionResult:
    if deps is None:
        deps = [
            Dependency(name="requests", current_version="2.28.0", latest_version="2.31.0"),
            Dependency(name="flask", current_version="2.3.0", latest_version="2.3.0"),
        ]
    return DetectionResult(ecosystem=ecosystem, manifest_path=manifest, dependencies=deps)


class TestXmlReporter(unittest.TestCase):
    def setUp(self):
        self.reporter = XmlReporter()

    def _parse(self, results):
        xml_str = self.reporter.render(results)
        return ET.fromstring(xml_str.split("\n", 1)[1])  # strip XML declaration

    def test_render_returns_string(self):
        out = self.reporter.render([_make_result()])
        self.assertIsInstance(out, str)

    def test_render_contains_xml_declaration(self):
        out = self.reporter.render([_make_result()])
        self.assertIn("<?xml", out)

    def test_testsuites_root_element(self):
        root = self._parse([_make_result()])
        self.assertEqual(root.tag, "testsuites")

    def test_testsuite_per_ecosystem(self):
        results = [_make_result("python"), _make_result("node", "package.json")]
        root = self._parse(results)
        suites = root.findall("testsuite")
        self.assertEqual(len(suites), 2)

    def test_failure_for_outdated_dep(self):
        root = self._parse([_make_result()])
        failures = root.findall(".//failure")
        self.assertEqual(len(failures), 1)
        self.assertIn("requests", failures[0].text)

    def test_no_failure_for_up_to_date_dep(self):
        deps = [Dependency(name="flask", current_version="2.3.0", latest_version="2.3.0")]
        root = self._parse([_make_result(deps=deps)])
        failures = root.findall(".//failure")
        self.assertEqual(len(failures), 0)

    def test_total_tests_attribute(self):
        root = self._parse([_make_result()])
        self.assertEqual(root.get("tests"), "2")

    def test_total_failures_attribute(self):
        root = self._parse([_make_result()])
        self.assertEqual(root.get("failures"), "1")

    def test_testsuite_manifest_file_attribute(self):
        root = self._parse([_make_result(manifest="requirements.txt")])
        suite = root.find("testsuite")
        self.assertEqual(suite.get("file"), "requirements.txt")

    def test_empty_results(self):
        out = self.reporter.render([])
        root = ET.fromstring(out.split("\n", 1)[1])
        self.assertEqual(root.get("tests"), "0")
        self.assertEqual(root.get("failures"), "0")


if __name__ == "__main__":
    unittest.main()
