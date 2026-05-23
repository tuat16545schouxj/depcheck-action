"""Tests for CycloneDXReporter."""
from __future__ import annotations

import json
import unittest

from src.detectors.base import Dependency, DetectionResult
from src.reporters.cyclonedx_reporter import CycloneDXReporter


def _dep(name: str, current: str, latest: str | None = None, outdated: bool = False) -> Dependency:
    return Dependency(name=name, current_version=current, latest_version=latest, outdated=outdated)


def _make_result(ecosystem: str = "python") -> DetectionResult:
    return DetectionResult(
        ecosystem=ecosystem,
        manifest="requirements.txt",
        dependencies=[
            _dep("requests", "2.28.0", "2.31.0", outdated=True),
            _dep("flask", "2.3.0"),
        ],
    )


class TestCycloneDXReporter(unittest.TestCase):
    SERIAL = "urn:uuid:00000000-0000-0000-0000-000000000001"

    def setUp(self) -> None:
        self.reporter = CycloneDXReporter(serial_number=self.SERIAL)
        self.result = _make_result()

    def _parse(self) -> dict:
        return json.loads(self.reporter.render([self.result]))

    def test_render_returns_string(self) -> None:
        self.assertIsInstance(self.reporter.render([self.result]), str)

    def test_output_is_valid_json(self) -> None:
        bom = self._parse()
        self.assertIsInstance(bom, dict)

    def test_bom_format_field(self) -> None:
        self.assertEqual(self._parse()["bomFormat"], "CycloneDX")

    def test_spec_version_field(self) -> None:
        self.assertEqual(self._parse()["specVersion"], "1.4")

    def test_serial_number_injected(self) -> None:
        self.assertEqual(self._parse()["serialNumber"], self.SERIAL)

    def test_component_count(self) -> None:
        self.assertEqual(len(self._parse()["components"]), 2)

    def test_component_name(self) -> None:
        names = [c["name"] for c in self._parse()["components"]]
        self.assertIn("requests", names)

    def test_component_version(self) -> None:
        comp = next(c for c in self._parse()["components"] if c["name"] == "requests")
        self.assertEqual(comp["version"], "2.28.0")

    def test_purl_pypi(self) -> None:
        comp = next(c for c in self._parse()["components"] if c["name"] == "requests")
        self.assertTrue(comp["purl"].startswith("pkg:pypi/requests@"))

    def test_purl_npm_ecosystem(self) -> None:
        result = _make_result(ecosystem="node")
        bom = json.loads(self.reporter.render([result]))
        comp = bom["components"][0]
        self.assertIn("pkg:npm/", comp["purl"])

    def test_outdated_property_true(self) -> None:
        comp = next(c for c in self._parse()["components"] if c["name"] == "requests")
        props = {p["name"]: p["value"] for p in comp["properties"]}
        self.assertEqual(props["depcheck:outdated"], "true")

    def test_outdated_property_false(self) -> None:
        comp = next(c for c in self._parse()["components"] if c["name"] == "flask")
        props = {p["name"]: p["value"] for p in comp["properties"]}
        self.assertEqual(props["depcheck:outdated"], "false")

    def test_latest_version_property_present_when_outdated(self) -> None:
        comp = next(c for c in self._parse()["components"] if c["name"] == "requests")
        props = {p["name"]: p["value"] for p in comp["properties"]}
        self.assertEqual(props["depcheck:latest_version"], "2.31.0")

    def test_metadata_tool_name(self) -> None:
        tools = self._parse()["metadata"]["tools"]
        self.assertEqual(tools[0]["name"], "depcheck-action")

    def test_empty_results(self) -> None:
        bom = json.loads(self.reporter.render([]))
        self.assertEqual(bom["components"], [])


if __name__ == "__main__":
    unittest.main()
