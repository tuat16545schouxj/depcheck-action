"""Tests for SonarQubeReporter."""

from __future__ import annotations

import json
import unittest
from dataclasses import dataclass, field
from typing import List

from src.reporters.sonarqube_reporter import SonarQubeReporter


# ---------------------------------------------------------------------------
# Minimal stubs
# ---------------------------------------------------------------------------

@dataclass
class _Dep:
    name: str
    current_version: str = "1.0.0"
    latest_version: str = "2.0.0"
    outdated: bool = True


@dataclass
class _Result:
    ecosystem: str
    manifest_path: str
    dependencies: List[_Dep] = field(default_factory=list)


def _make_result(
    ecosystem: str = "python",
    manifest: str = "requirements.txt",
    deps: list[_Dep] | None = None,
) -> _Result:
    return _Result(
        ecosystem=ecosystem,
        manifest_path=manifest,
        dependencies=deps or [
            _Dep("requests", "2.28.0", "2.31.0", True),
            _Dep("flask", "2.2.0", "3.0.0", True),
            _Dep("pytest", "7.4.0", "7.4.0", False),
        ],
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestSonarQubeReporter(unittest.TestCase):
    def setUp(self) -> None:
        self.reporter = SonarQubeReporter()
        self.result = _make_result()

    def _parse(self, result=None) -> dict:
        raw = self.reporter.render([result or self.result])
        return json.loads(raw)

    def test_render_returns_string(self) -> None:
        self.assertIsInstance(self.reporter.render([self.result]), str)

    def test_output_is_valid_json(self) -> None:
        payload = self._parse()
        self.assertIsInstance(payload, dict)

    def test_engine_id_present(self) -> None:
        payload = self._parse()
        self.assertEqual(payload["engineId"], "depcheck")

    def test_custom_engine_id(self) -> None:
        reporter = SonarQubeReporter(engine_id="my-engine")
        payload = json.loads(reporter.render([self.result]))
        self.assertEqual(payload["engineId"], "my-engine")

    def test_rules_list_present(self) -> None:
        payload = self._parse()
        self.assertIn("rules", payload)
        self.assertEqual(len(payload["rules"]), 1)

    def test_rule_has_required_fields(self) -> None:
        rule = self._parse()["rules"][0]
        for key in ("id", "name", "description", "engineId"):
            self.assertIn(key, rule)

    def test_only_outdated_deps_become_issues(self) -> None:
        payload = self._parse()
        # pytest is NOT outdated — should not appear
        self.assertEqual(len(payload["issues"]), 2)

    def test_issue_contains_rule_id(self) -> None:
        issue = self._parse()["issues"][0]
        self.assertEqual(issue["ruleId"], "depcheck:outdated-dependency")

    def test_issue_primary_location_file_path(self) -> None:
        issue = self._parse()["issues"][0]
        self.assertEqual(
            issue["primaryLocation"]["filePath"], "requirements.txt"
        )

    def test_issue_message_contains_versions(self) -> None:
        issue = self._parse()["issues"][0]
        msg = issue["primaryLocation"]["message"]
        self.assertIn("2.28.0", msg)
        self.assertIn("2.31.0", msg)

    def test_no_issues_when_all_current(self) -> None:
        result = _Result(
            ecosystem="node",
            manifest_path="package.json",
            dependencies=[_Dep("lodash", "4.17.21", "4.17.21", False)],
        )
        payload = json.loads(self.reporter.render([result]))
        self.assertEqual(payload["issues"], [])

    def test_multiple_results_aggregated(self) -> None:
        r1 = _make_result("python", "requirements.txt",
                          [_Dep("requests", outdated=True)])
        r2 = _make_result("node", "package.json",
                          [_Dep("lodash", outdated=True)])
        payload = json.loads(self.reporter.render([r1, r2]))
        self.assertEqual(len(payload["issues"]), 2)


if __name__ == "__main__":
    unittest.main()
