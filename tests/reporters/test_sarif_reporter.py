"""Tests for SarifReporter."""
import json
import unittest

from src.reporters.sarif_reporter import SarifReporter, SARIF_VERSION, RULE_ID, TOOL_NAME
from src.detectors.base import Dependency, DetectionResult


class TestSarifReporter(unittest.TestCase):
    def setUp(self):
        self.reporter = SarifReporter(tool_version="1.2.3")
        outdated_dep = Dependency(name="requests", current_version="2.20.0", latest_version="2.31.0", outdated=True)
        current_dep = Dependency(name="urllib3", current_version="2.0.0", latest_version="2.0.0", outdated=False)
        self.results = [
            DetectionResult(
                ecosystem="python",
                manifest_path="requirements.txt",
                dependencies=[outdated_dep, current_dep],
            )
        ]
        self.empty_results = []

    def _parse(self, results=None):
        if results is None:
            results = self.results
        return json.loads(self.reporter.render(results))

    def test_output_is_valid_json(self):
        output = self.reporter.render(self.results)
        parsed = json.loads(output)
        self.assertIsInstance(parsed, dict)

    def test_sarif_version_field(self):
        sarif = self._parse()
        self.assertEqual(sarif["version"], SARIF_VERSION)

    def test_schema_field_present(self):
        sarif = self._parse()
        self.assertIn("$schema", sarif)
        self.assertIn("sarif", sarif["$schema"])

    def test_tool_name(self):
        sarif = self._parse()
        driver = sarif["runs"][0]["tool"]["driver"]
        self.assertEqual(driver["name"], TOOL_NAME)

    def test_tool_version(self):
        sarif = self._parse()
        driver = sarif["runs"][0]["tool"]["driver"]
        self.assertEqual(driver["version"], "1.2.3")

    def test_only_outdated_deps_in_results(self):
        sarif = self._parse()
        run_results = sarif["runs"][0]["results"]
        self.assertEqual(len(run_results), 1)

    def test_result_rule_id(self):
        sarif = self._parse()
        result = sarif["runs"][0]["results"][0]
        self.assertEqual(result["ruleId"], RULE_ID)

    def test_result_message_contains_dep_name(self):
        sarif = self._parse()
        message = sarif["runs"][0]["results"][0]["message"]["text"]
        self.assertIn("requests", message)

    def test_result_message_contains_latest_version(self):
        sarif = self._parse()
        message = sarif["runs"][0]["results"][0]["message"]["text"]
        self.assertIn("2.31.0", message)

    def test_result_location_uri(self):
        sarif = self._parse()
        location = sarif["runs"][0]["results"][0]["locations"][0]
        uri = location["physicalLocation"]["artifactLocation"]["uri"]
        self.assertEqual(uri, "requirements.txt")

    def test_fingerprint_present(self):
        sarif = self._parse()
        fingerprints = sarif["runs"][0]["results"][0]["fingerprints"]
        self.assertIn("depcheck/v1", fingerprints)
        self.assertIn("requests", fingerprints["depcheck/v1"])

    def test_empty_results_produce_no_run_results(self):
        sarif = self._parse(self.empty_results)
        self.assertEqual(sarif["runs"][0]["results"], [])

    def test_invocations_execution_successful(self):
        sarif = self._parse()
        invocation = sarif["runs"][0]["invocations"][0]
        self.assertTrue(invocation["executionSuccessful"])


if __name__ == "__main__":
    unittest.main()
