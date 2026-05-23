"""Tests for reporter_registry."""
from __future__ import annotations

import unittest

from src.reporters.reporter_registry import (
    available_reporters,
    get_reporter,
    get_reporter_class,
)
from src.reporters.pdf_reporter import PdfReporter
from src.reporters.markdown_reporter import MarkdownReporter
from src.reporters.json_reporter import JsonReporter


class TestReporterRegistry(unittest.TestCase):
    def test_available_reporters_returns_list(self):
        result = available_reporters()
        self.assertIsInstance(result, list)

    def test_available_reporters_sorted(self):
        result = available_reporters()
        self.assertEqual(result, sorted(result))

    def test_available_reporters_includes_badge(self):
        self.assertIn("badge", available_reporters())

    def test_available_reporters_includes_dashboard(self):
        self.assertIn("dashboard", available_reporters())

    def test_available_reporters_includes_pdf(self):
        self.assertIn("pdf", available_reporters())

    def test_available_reporters_includes_markdown(self):
        self.assertIn("markdown", available_reporters())

    def test_available_reporters_includes_json(self):
        self.assertIn("json", available_reporters())

    def test_available_reporters_includes_junit(self):
        self.assertIn("junit", available_reporters())

    def test_available_reporters_includes_sarif(self):
        self.assertIn("sarif", available_reporters())

    def test_get_reporter_class_pdf(self):
        cls = get_reporter_class("pdf")
        self.assertIs(cls, PdfReporter)

    def test_get_reporter_class_markdown(self):
        cls = get_reporter_class("markdown")
        self.assertIs(cls, MarkdownReporter)

    def test_get_reporter_class_unknown_raises(self):
        with self.assertRaises(KeyError) as ctx:
            get_reporter_class("nonexistent_reporter")
        self.assertIn("nonexistent_reporter", str(ctx.exception))

    def test_get_reporter_class_unknown_lists_available(self):
        with self.assertRaises(KeyError) as ctx:
            get_reporter_class("nope")
        self.assertIn("pdf", str(ctx.exception))

    def test_get_reporter_returns_instance(self):
        reporter = get_reporter("pdf")
        self.assertIsInstance(reporter, PdfReporter)

    def test_get_reporter_json_returns_instance(self):
        reporter = get_reporter("json")
        self.assertIsInstance(reporter, JsonReporter)

    def test_get_reporter_unknown_raises(self):
        with self.assertRaises(KeyError):
            get_reporter("does_not_exist")
