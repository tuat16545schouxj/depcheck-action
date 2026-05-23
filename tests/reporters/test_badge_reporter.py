"""Tests for BadgeReporter."""
from __future__ import annotations

import json
import unittest
from dataclasses import dataclass, field
from typing import List

from src.reporters.badge_reporter import BadgeReporter


@dataclass
class _Dep:
    name: str
    current_version: str
    latest_version: str
    outdated: bool = False


@dataclass
class _Result:
    ecosystem: str
    manifest: str
    dependencies: List[_Dep] = field(default_factory=list)


def _make_result(eco="npm", total=4, outdated=1):
    deps = [_Dep(f"pkg{i}", "1.0.0", "2.0.0", outdated=(i < outdated)) for i in range(total)]
    return _Result(ecosystem=eco, manifest="package.json", dependencies=deps)


class TestBadgeReporter(unittest.TestCase):
    def setUp(self):
        self.reporter = BadgeReporter()

    def _parse(self, results):
        return json.loads(self.reporter.render(results))

    def test_render_returns_valid_json(self):
        payload = self._parse([_make_result()])
        self.assertIsInstance(payload, dict)

    def test_schema_version_is_one(self):
        payload = self._parse([_make_result()])
        self.assertEqual(payload["schemaVersion"], 1)

    def test_label_default(self):
        payload = self._parse([_make_result()])
        self.assertEqual(payload["label"], "dependencies")

    def test_custom_label(self):
        reporter = BadgeReporter(label="deps")
        payload = json.loads(reporter.render([_make_result()]))
        self.assertEqual(payload["label"], "deps")

    def test_all_up_to_date(self):
        result = _make_result(total=4, outdated=0)
        payload = self._parse([result])
        self.assertEqual(payload["message"], "up to date")
        self.assertEqual(payload["color"], "brightgreen")

    def test_some_outdated_message(self):
        result = _make_result(total=4, outdated=2)
        payload = self._parse([result])
        self.assertIn("outdated", payload["message"])
        self.assertIn("2", payload["message"])

    def test_high_ratio_is_red(self):
        result = _make_result(total=4, outdated=4)
        payload = self._parse([result])
        self.assertEqual(payload["color"], "red")

    def test_empty_results_unknown(self):
        payload = self._parse([])
        self.assertEqual(payload["message"], "unknown")
        self.assertEqual(payload["color"], "lightgrey")

    def test_color_field_present(self):
        payload = self._parse([_make_result()])
        self.assertIn("color", payload)

    def test_multiple_results_aggregated(self):
        r1 = _make_result(total=10, outdated=0)
        r2 = _make_result(total=10, outdated=0)
        payload = self._parse([r1, r2])
        self.assertEqual(payload["message"], "up to date")


if __name__ == "__main__":
    unittest.main()
