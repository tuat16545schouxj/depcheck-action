import io
import unittest
from src.reporters.console_reporter import ConsoleReporter
from src.detectors.base import Dependency, DetectionResult


class TestConsoleReporter(unittest.TestCase):
    def setUp(self):
        self.stream = io.StringIO()
        self.reporter = ConsoleReporter(use_color=False, stream=self.stream)

        self.dep_ok = Dependency(
            name="requests", current_version="2.28.0", latest_version="2.28.0"
        )
        self.dep_outdated = Dependency(
            name="flask", current_version="2.0.0", latest_version="3.0.1"
        )
        self.result = DetectionResult(
            ecosystem="python",
            manifest_path="requirements.txt",
            dependencies=[self.dep_ok, self.dep_outdated],
        )

    def _output(self, results):
        self.stream = io.StringIO()
        reporter = ConsoleReporter(use_color=False, stream=self.stream)
        return reporter.render(results)

    def test_render_contains_title(self):
        output = self._output([self.result])
        self.assertIn("Dependency Audit Report", output)

    def test_render_shows_ecosystem(self):
        output = self._output([self.result])
        self.assertIn("python", output)

    def test_render_shows_manifest_path(self):
        output = self._output([self.result])
        self.assertIn("requirements.txt", output)

    def test_render_shows_outdated_dependency(self):
        output = self._output([self.result])
        self.assertIn("flask", output)
        self.assertIn("2.0.0", output)
        self.assertIn("3.0.1", output)
        self.assertIn("OUTDATED", output)

    def test_render_shows_ok_dependency(self):
        output = self._output([self.result])
        self.assertIn("requests", output)
        self.assertIn("ok", output)

    def test_summary_totals(self):
        output = self._output([self.result])
        self.assertIn("Total deps    : 2", output)
        self.assertIn("Outdated      : 1", output)
        self.assertIn("Files scanned : 1", output)

    def test_empty_results(self):
        output = self._output([])
        self.assertIn("No dependency files detected", output)

    def test_multiple_results_aggregate_summary(self):
        result2 = DetectionResult(
            ecosystem="node",
            manifest_path="package.json",
            dependencies=[
                Dependency(name="lodash", current_version="4.0.0", latest_version="4.17.21")
            ],
        )
        output = self._output([self.result, result2])
        self.assertIn("Files scanned : 2", output)
        self.assertIn("Total deps    : 3", output)
        self.assertIn("Outdated      : 2", output)

    def test_no_color_mode_has_no_escape_codes(self):
        output = self._output([self.result])
        self.assertNotIn("\033[", output)

    def test_render_returns_string(self):
        result = self._output([self.result])
        self.assertIsInstance(result, str)


if __name__ == "__main__":
    unittest.main()
