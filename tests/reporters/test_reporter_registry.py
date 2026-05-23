"""Tests for reporter_registry."""
from __future__ import annotations

import unittest

from src.reporters.reporter_registry import (
    available_reporters,
    get_reporter,
    get_reporter_class,
)


class TestReporterRegistry(unittest.TestCase):
    def test_available_reporters_returns_list(self) -> None:
        self.assertIsInstance(available_reporters(), list)

    def test_available_reporters_sorted(self) -> None:
        names = available_reporters()
        self.assertEqual(names, sorted(names))

    def test_available_reporters_includes_badge(self) -> None:
        self.assertIn("badge", available_reporters())

    def test_available_reporters_includes_dashboard(self) -> None:
        self.assertIn("dashboard", available_reporters())

    def test_available_reporters_includes_datadog(self) -> None:
        self.assertIn("datadog", available_reporters())

    def test_available_reporters_includes_prometheus(self) -> None:
        self.assertIn("prometheus", available_reporters())

    def test_available_reporters_includes_graphite(self) -> None:
        self.assertIn("graphite", available_reporters())

    def test_get_reporter_class_returns_class(self) -> None:
        from src.reporters.json_reporter import JsonReporter
        self.assertIs(get_reporter_class("json"), JsonReporter)

    def test_get_reporter_class_case_insensitive(self) -> None:
        from src.reporters.json_reporter import JsonReporter
        self.assertIs(get_reporter_class("JSON"), JsonReporter)

    def test_get_reporter_class_unknown_raises(self) -> None:
        with self.assertRaises(KeyError):
            get_reporter_class("nonexistent")

    def test_get_reporter_returns_instance(self) -> None:
        from src.reporters.json_reporter import JsonReporter
        reporter = get_reporter("json")
        self.assertIsInstance(reporter, JsonReporter)

    def test_get_reporter_datadog_no_post(self) -> None:
        from src.reporters.datadog_reporter import DatadogReporter
        reporter = get_reporter("datadog", post=False)
        self.assertIsInstance(reporter, DatadogReporter)

    def test_all_reporters_have_render(self) -> None:
        for name in available_reporters():
            if name in ("email", "github_pr", "slack"):  # require live credentials
                continue
            cls = get_reporter_class(name)
            self.assertTrue(callable(getattr(cls, "render", None)), name)
