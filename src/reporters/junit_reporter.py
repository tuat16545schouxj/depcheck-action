"""JUnit XML reporter — emits results as a JUnit-compatible test-suite XML.

Each ecosystem becomes a <testsuite>; each outdated dependency becomes a
<testcase> with a <failure> element.  Up-to-date dependencies are emitted
as passing <testcase> elements so that CI tooling can display full counts.
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from xml.dom import minidom
from typing import List

from src.detectors.base import DetectionResult


class JUnitReporter:
    """Render detection results as JUnit XML."""

    # ------------------------------------------------------------------
    # public API
    # ------------------------------------------------------------------

    def render(self, results: List[DetectionResult]) -> str:
        """Return a pretty-printed JUnit XML string."""
        root = ET.Element("testsuites")
        root.set("name", "depcheck")

        total_tests = 0
        total_failures = 0

        for result in results:
            suite, tests, failures = self._build_suite(result)
            root.append(suite)
            total_tests += tests
            total_failures += failures

        root.set("tests", str(total_tests))
        root.set("failures", str(total_failures))

        return self._pretty(root)

    # ------------------------------------------------------------------
    # private helpers
    # ------------------------------------------------------------------

    def _build_suite(self, result: DetectionResult):
        suite = ET.Element("testsuite")
        suite.set("name", result.ecosystem)
        suite.set("tests", str(len(result.dependencies)))

        failures = 0
        for dep in result.dependencies:
            tc = ET.SubElement(suite, "testcase")
            tc.set("classname", result.ecosystem)
            tc.set("name", dep.name)

            if dep.outdated:
                failures += 1
                failure = ET.SubElement(tc, "failure")
                failure.set("message", f"{dep.name} is outdated")
                failure.text = (
                    f"Package : {dep.name}\n"
                    f"Current : {dep.current_version}\n"
                    f"Latest  : {dep.latest_version}\n"
                    f"File    : {result.manifest_path}"
                )

        suite.set("failures", str(failures))
        return suite, len(result.dependencies), failures

    @staticmethod
    def _pretty(element: ET.Element) -> str:
        raw = ET.tostring(element, encoding="unicode")
        return minidom.parseString(raw).toprettyxml(indent="  ")
