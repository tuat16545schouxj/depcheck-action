"""Tests for HtmlReporter."""
import unittest
from src.reporters.html_reporter import HtmlReporter
from src.detectors.base import Dependency, DetectionResult


def _make_result(
    ecosystem: str = "python",
    manifest: str = "requirements.txt",
    deps=None,
) -> DetectionResult:
    if deps is None:
        deps = [
            Dependency("requests", "2.28.0", "2.31.0"),
            Dependency("flask", "2.0.0", "2.0.0"),
        ]
    return DetectionResult(ecosystem=ecosystem, manifest_path=manifest, dependencies=deps)


class TestHtmlReporter(unittest.TestCase):
    def setUp(self):
        self.reporter = HtmlReporter()

    def test_render_returns_string(self):
        html = self.reporter.render([_make_result()])
        self.assertIsInstance(html, str)

    def test_render_contains_doctype(self):
        html = self.reporter.render([_make_result()])
        self.assertIn("<!DOCTYPE html>", html)

    def test_render_shows_title(self):
        html = self.reporter.render([_make_result()])
        self.assertIn("depcheck-action", html)

    def test_render_shows_ecosystem(self):
        html = self.reporter.render([_make_result(ecosystem="node")])
        self.assertIn("node", html)

    def test_render_shows_dependency_name(self):
        html = self.reporter.render([_make_result()])
        self.assertIn("requests", html)

    def test_render_marks_outdated_class(self):
        html = self.reporter.render([_make_result()])
        self.assertIn('class="outdated"', html)

    def test_render_shows_total_count(self):
        html = self.reporter.render([_make_result()])
        self.assertIn("2", html)

    def test_render_shows_outdated_badge(self):
        html = self.reporter.render([_make_result()])
        self.assertIn("badge-warn", html)

    def test_render_ok_badge_when_no_outdated(self):
        deps = [Dependency("flask", "2.0.0", "2.0.0")]
        html = self.reporter.render([_make_result(deps=deps)])
        self.assertIn("badge-ok", html)

    def test_render_empty_results(self):
        html = self.reporter.render([])
        self.assertIn("Total dependencies: <strong>0</strong>", html)

    def test_render_shows_manifest_path(self):
        html = self.reporter.render([_make_result(manifest="path/to/requirements.txt")])
        self.assertIn("path/to/requirements.txt", html)

    def test_render_multiple_ecosystems(self):
        results = [
            _make_result(ecosystem="python"),
            _make_result(ecosystem="node", manifest="package.json"),
        ]
        html = self.reporter.render(results)
        self.assertIn("python", html)
        self.assertIn("node", html)


if __name__ == "__main__":
    unittest.main()
