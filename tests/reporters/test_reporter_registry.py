"""Tests for reporter_registry."""
from __future__ import annotations

import unittest

from src.reporters.reporter_registry import (
    available_reporters,
    get_reporter,
    get_reporter_class,
)
from src.reporters.toml_reporter import TomlReporter
from src.reporters.json_reporter import JsonReporter
from src.reporters.markdown_reporter import MarkdownReporter
from src.reporters.badge_reporter import BadgeReporter
from src.reporters.dashboard_reporter import DashboardReporter


class TestReporterRegistry(unittest.TestCase):
    def test_available_reporters_returns_list(self):
        self.assertIsInstance(available_reporters(), list)

    def test_available_reporters_sorted(self):
        names = available_reporters()
        self.assertEqual(names, sorted(names))

    def test_available_reporters_includes_badge(self):
        self.assertIn("badge", available_reporters())

    def test_available_reporters_includes_dashboard(self):
        self.assertIn("dashboard", available_reporters())

    def test_available_reporters_includes_toml(self):
        self.assertIn("toml", available_reporters())

    def test_available_reporters_includes_json(self):
        self.assertIn("json", available_reporters())

    def test_available_reporters_includes_markdown(self):
        self.assertIn("markdown", available_reporters())

    def test_get_reporter_class_toml(self):
        self.assertIs(get_reporter_class("toml"), TomlReporter)

    def test_get_reporter_class_json(self):
        self.assertIs(get_reporter_class("json"), JsonReporter)

    def test_get_reporter_class_unknown_returns_none(self):
        self.assertIsNone(get_reporter_class("nonexistent_reporter"))

    def test_get_reporter_returns_instance(self):
        reporter = get_reporter("toml")
        self.assertIsInstance(reporter, TomlReporter)

    def test_get_reporter_json_instance(self):
        reporter = get_reporter("json")
        self.assertIsInstance(reporter, JsonReporter)

    def test_get_reporter_unknown_raises_value_error(self):
        with self.assertRaises(ValueError) as ctx:
            get_reporter("does_not_exist")
        self.assertIn("does_not_exist", str(ctx.exception))

    def test_get_reporter_error_lists_available(self):
        with self.assertRaises(ValueError) as ctx:
            get_reporter("does_not_exist")
        for name in ("toml", "json", "markdown"):
            self.assertIn(name, str(ctx.exception))
