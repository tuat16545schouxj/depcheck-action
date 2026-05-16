"""Tests for the MarkdownReporter."""
import unittest
from src.reporters.markdown_reporter import MarkdownReporter
from src.detectors.base import Dependency, DetectionResult


class TestMarkdownReporter(unittest.TestCase):
    def setUp(self):
        self.reporter = MarkdownReporter()
        self.outdated_dep = Dependency(
            name="requests",
            current_version="2.20.0",
            latest_version="2.31.0",
        )
        self.current_dep = Dependency(
            name="flask",
            current_version="3.0.0",
            latest_version="3.0.0",
        )
        self.result = DetectionResult(
            manifest_path="requirements.txt",
            ecosystem="python",
            dependencies=[self.outdated_dep, self.current_dep],
        )

    def test_render_contains_title(self):
        output = self.reporter.render([self.result])
        self.assertIn("# 🔍 Dependency Audit Report", output)

    def test_render_shows_outdated_count(self):
        output = self.reporter.render([self.result])
        self.assertIn("Found **1** outdated", output)

    def test_render_shows_total_count(self):
        output = self.reporter.render([self.result])
        self.assertIn("Scanned **2** dependencies", output)

    def test_render_shows_manifest_path(self):
        output = self.reporter.render([self.result])
        self.assertIn("`requirements.txt`", output)

    def test_render_shows_ecosystem(self):
        output = self.reporter.render([self.result])
        self.assertIn("python", output)

    def test_render_outdated_table_row(self):
        output = self.reporter.render([self.result])
        self.assertIn("`requests`", output)
        self.assertIn("`2.20.0`", output)
        self.assertIn("`2.31.0`", output)

    def test_render_no_results(self):
        output = self.reporter.render([])
        self.assertIn("_No dependency files detected._", output)

    def test_render_all_up_to_date(self):
        result = DetectionResult(
            manifest_path="go.mod",
            ecosystem="go",
            dependencies=[self.current_dep],
        )
        output = self.reporter.render([result])
        self.assertIn("All dependencies are up to date", output)

    def test_render_show_up_to_date_toggle(self):
        reporter = MarkdownReporter(show_up_to_date=True)
        output = reporter.render([self.result])
        self.assertIn("Up-to-date dependencies", output)
        self.assertIn("`flask`", output)

    def test_render_hides_up_to_date_by_default(self):
        output = self.reporter.render([self.result])
        self.assertNotIn("Up-to-date dependencies", output)

    def test_custom_title(self):
        reporter = MarkdownReporter(title="Custom Report Title")
        output = reporter.render([self.result])
        self.assertIn("# Custom Report Title", output)

    def test_footer_present(self):
        output = self.reporter.render([self.result])
        self.assertIn("depcheck-action", output)


if __name__ == "__main__":
    unittest.main()
