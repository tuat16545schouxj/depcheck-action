"""Tests for reporter_registry."""
from __future__ import annotations

import unittest

from src.reporters.reporter_registry import (
    available_reporters,
    get_reporter,
    get_reporter_class,
)
from src.reporters.badge_reporter import BadgeReporter
from src.reporters.markdown_reporter import MarkdownReporter
from src.reporters.json_reporter import JsonReporter


class TestReporterRegistry(unittest.TestCase):
    def test_available_reporters_returns_list(self):
        result = available_reporters()
        self.assertIsInstance(result, list)

    def test_available_reporters_sorted(self):
        names = available_reporters()
        self.assertEqual(names, sorted(names))

    def test_available_reporters_includes_badge(self):
        self.assertIn("badge", available_reporters())

    def test_available_reporters_includes_core(self):
        for name in ("markdown", "json", "console", "sarif", "html", "csv", "xml"):
            with self.subTest(name=name):
                self.assertIn(name, available_reporters())

    def test_get_reporter_class_badge(self):
        cls = get_reporter_class("badge")
        self.assertIs(cls, BadgeReporter)

    def test_get_reporter_class_markdown(self):
        cls = get_reporter_class("markdown")
        self.assertIs(cls, MarkdownReporter)

    def test_get_reporter_class_case_insensitive(self):
        cls = get_reporter_class("JSON")
        self.assertIs(cls, JsonReporter)

    def test_get_reporter_class_unknown_raises(self):
        with self.assertRaises(KeyError):
            get_reporter_class("nonexistent")

    def test_get_reporter_returns_instance(self):
        reporter = get_reporter("badge")
        self.assertIsInstance(reporter, BadgeReporter)

    def test_get_reporter_badge_custom_label(self):
        reporter = get_reporter("badge", label="my-deps")
        self.assertEqual(reporter.label, "my-deps")

    def test_get_reporter_unknown_raises(self):
        with self.assertRaises(KeyError):
            get_reporter("ghost")

    def test_all_reporters_have_render(self):
        for name in available_reporters():
            cls = get_reporter_class(name)
            self.assertTrue(hasattr(cls, "render"), f"{name} missing render()")


if __name__ == "__main__":
    unittest.main()
