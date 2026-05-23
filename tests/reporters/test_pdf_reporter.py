"""Tests for PdfReporter."""
from __future__ import annotations

import unittest

from src.detectors.base import Dependency, DetectionResult
from src.reporters.pdf_reporter import PdfReporter, _build_pdf


def _dep(name: str, current: str, latest: str) -> Dependency:
    return Dependency(name=name, current_version=current, latest_version=latest)


def _make_result(
    ecosystem: str = "python",
    manifest: str = "requirements.txt",
    deps=None,
) -> DetectionResult:
    if deps is None:
        deps = [
            _dep("requests", "2.28.0", "2.31.0"),
            _dep("flask", "2.3.0", "2.3.0"),
        ]
    return DetectionResult(ecosystem=ecosystem, manifest_path=manifest, dependencies=deps)


class TestPdfReporter(unittest.TestCase):
    def setUp(self):
        self.reporter = PdfReporter()

    # ------------------------------------------------------------------
    # basic output checks
    # ------------------------------------------------------------------

    def test_render_returns_bytes(self):
        result = self.reporter.render([_make_result()])
        self.assertIsInstance(result, bytes)

    def test_render_starts_with_pdf_header(self):
        result = self.reporter.render([_make_result()])
        self.assertTrue(result.startswith(b"%PDF-"), "PDF magic bytes missing")

    def test_render_ends_with_eof_marker(self):
        result = self.reporter.render([_make_result()])
        self.assertIn(b"%%EOF", result)

    def test_render_contains_xref(self):
        result = self.reporter.render([_make_result()])
        self.assertIn(b"xref", result)

    def test_render_contains_trailer(self):
        result = self.reporter.render([_make_result()])
        self.assertIn(b"trailer", result)

    def test_render_empty_results(self):
        result = self.reporter.render([])
        self.assertIsInstance(result, bytes)
        self.assertTrue(result.startswith(b"%PDF-"))

    # ------------------------------------------------------------------
    # content checks via text lines helper
    # ------------------------------------------------------------------

    def test_collect_text_lines_includes_title(self):
        lines = self.reporter._collect_text_lines([_make_result()])
        self.assertIn("Dependency Audit Report", lines)

    def test_collect_text_lines_includes_ecosystem(self):
        lines = self.reporter._collect_text_lines([_make_result()])
        combined = "\n".join(lines)
        self.assertIn("python", combined)

    def test_collect_text_lines_shows_outdated_dep(self):
        lines = self.reporter._collect_text_lines([_make_result()])
        combined = "\n".join(lines)
        self.assertIn("requests", combined)
        self.assertIn("2.31.0", combined)

    def test_collect_text_lines_does_not_show_uptodate_dep(self):
        """Up-to-date deps should not appear in the outdated section."""
        lines = self.reporter._collect_text_lines([_make_result()])
        combined = "\n".join(lines)
        # flask is up-to-date, so no arrow for it
        self.assertNotIn("flask: 2.3.0 ->", combined)

    def test_collect_text_lines_all_uptodate_message(self):
        result = _make_result(deps=[_dep("flask", "2.3.0", "2.3.0")])
        lines = self.reporter._collect_text_lines([result])
        combined = "\n".join(lines)
        self.assertIn("All dependencies up-to-date", combined)

    def test_collect_text_lines_summary_counts(self):
        result = _make_result()
        lines = self.reporter._collect_text_lines([result])
        combined = "\n".join(lines)
        self.assertIn("1 outdated", combined)
        self.assertIn("2 total", combined)

    # ------------------------------------------------------------------
    # _build_pdf low-level
    # ------------------------------------------------------------------

    def test_build_pdf_contains_title_in_catalog(self):
        pdf = _build_pdf("My Title", ["line one", "line two"])
        self.assertIn(b"My Title", pdf)

    def test_build_pdf_content_stream_present(self):
        pdf = _build_pdf("T", ["hello world"])
        self.assertIn(b"hello world", pdf)

    def test_multiple_ecosystems_all_present(self):
        results = [
            _make_result("python", "requirements.txt"),
            _make_result("node", "package.json", [_dep("lodash", "4.0.0", "4.17.21")]),
        ]
        lines = self.reporter._collect_text_lines(results)
        combined = "\n".join(lines)
        self.assertIn("python", combined)
        self.assertIn("node", combined)
        self.assertIn("lodash", combined)
