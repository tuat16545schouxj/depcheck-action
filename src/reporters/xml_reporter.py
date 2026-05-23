"""XML reporter — emits a JUnit-style XML report of outdated dependencies."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from xml.dom import minidom
from typing import List

from src.detectors.base import DetectionResult


class XmlReporter:
    """Renders detection results as a JUnit-compatible XML document.

    Each ecosystem becomes a <testsuite> and each outdated dependency
    becomes a <testcase> with a <failure> element.  Up-to-date
    dependencies are represented as passing test cases.
    """

    def render(self, results: List[DetectionResult]) -> str:
        root = ET.Element("testsuites")
        total_deps = sum(len(r.dependencies) for r in results)
        total_outdated = sum(
            sum(1 for d in r.dependencies if d.outdated) for r in results
        )
        root.set("name", "depcheck")
        root.set("tests", str(total_deps))
        root.set("failures", str(total_outdated))

        for result in results:
            root.append(self._render_result(result))

        raw = ET.tostring(root, encoding="unicode")
        return minidom.parseString(raw).toprettyxml(indent="  ")

    def _render_result(self, result: DetectionResult) -> ET.Element:
        outdated_count = sum(1 for d in result.dependencies if d.outdated)
        suite = ET.Element("testsuite")
        suite.set("name", result.ecosystem)
        suite.set("tests", str(len(result.dependencies)))
        suite.set("failures", str(outdated_count))
        suite.set("file", result.manifest_path)

        for dep in result.dependencies:
            case = ET.SubElement(suite, "testcase")
            case.set("classname", result.ecosystem)
            case.set("name", dep.name)
            if dep.outdated:
                failure = ET.SubElement(case, "failure")
                failure.set("type", "OutdatedDependency")
                failure.text = (
                    f"{dep.name} is outdated: "
                    f"current={dep.current_version}, "
                    f"latest={dep.latest_version}"
                )
        return suite
