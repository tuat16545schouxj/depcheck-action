"""Tests for TomlReporter."""
from __future__ import annotations

import unittest
from unittest.mock import patch

from src.detectors.base import Dependency, DetectionResult
from src.reporters.toml_reporter import TomlReporter

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore


def _dep(name, current, latest, outdated=True):
    d = Dependency(name=name, current_version=current, latest_version=latest)
    d.__dict__["outdated"] = outdated
    return d


def _make_result(ecosystem="python", manifest="requirements.txt", deps=None):
    if deps is None:
        deps = [_dep("requests", "2.28.0", "2.31.0")]
    r = DetectionResult(ecosystem=ecosystem, manifest=manifest, dependencies=deps)
    return r


class TestTomlReporter(unittest.TestCase):
    def setUp(self):
        self.reporter = TomlReporter()
        self.result = _make_result()

    def _parse(self, results=None):
        if results is None:
            results = [self.result]
        raw = self.reporter.render(results)
        return tomllib.loads(raw), raw

    def test_render_returns_string(self):
        out = self.reporter.render([self.result])
        self.assertIsInstance(out, str)
        self.assertTrue(len(out) > 0)

    def test_output_is_valid_toml(self):
        doc, _ = self._parse()
        self.assertIn("meta", doc)
        self.assertIn("ecosystems", doc)

    def test_meta_total_dependencies(self):
        doc, _ = self._parse()
        self.assertEqual(doc["meta"]["total_dependencies"], 1)

    def test_meta_total_outdated(self):
        deps = [
            _dep("requests", "2.28.0", "2.31.0", outdated=True),
            _dep("flask", "2.0.0", "2.0.0", outdated=False),
        ]
        result = _make_result(deps=deps)
        doc, _ = self._parse([result])
        self.assertEqual(doc["meta"]["total_outdated"], result.outdated_count)

    def test_meta_has_generated_at(self):
        doc, _ = self._parse()
        self.assertIn("generated_at", doc["meta"])
        self.assertTrue(doc["meta"]["generated_at"].endswith("Z"))

    def test_ecosystem_name_present(self):
        doc, _ = self._parse()
        self.assertEqual(doc["ecosystems"][0]["ecosystem"], "python")

    def test_manifest_present(self):
        doc, _ = self._parse()
        self.assertEqual(doc["ecosystems"][0]["manifest"], "requirements.txt")

    def test_dependency_name_present(self):
        doc, _ = self._parse()
        dep = doc["ecosystems"][0]["dependencies"][0]
        self.assertEqual(dep["name"], "requests")

    def test_dependency_versions(self):
        doc, _ = self._parse()
        dep = doc["ecosystems"][0]["dependencies"][0]
        self.assertEqual(dep["current"], "2.28.0")
        self.assertEqual(dep["latest"], "2.31.0")

    def test_multiple_ecosystems(self):
        r2 = _make_result(ecosystem="node", manifest="package.json",
                          deps=[_dep("lodash", "4.17.20", "4.17.21")])
        doc, _ = self._parse([self.result, r2])
        self.assertEqual(len(doc["ecosystems"]), 2)
        names = {e["ecosystem"] for e in doc["ecosystems"]}
        self.assertIn("node", names)

    def test_reporter_name(self):
        self.assertEqual(TomlReporter.name, "toml")
