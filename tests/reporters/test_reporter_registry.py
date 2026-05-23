"""Tests for reporter_registry."""
import unittest

from src.reporters.reporter_registry import available_reporters, get_reporter, get_reporter_class


class TestReporterRegistry(unittest.TestCase):
    def test_available_reporters_returns_list(self):
        reporters = available_reporters()
        self.assertIsInstance(reporters, list)
        self.assertGreater(len(reporters), 0)

    def test_available_reporters_sorted(self):
        reporters = available_reporters()
        self.assertEqual(reporters, sorted(reporters))

    def test_available_reporters_includes_badge(self):
        self.assertIn("badge", available_reporters())

    def test_available_reporters_includes_dashboard(self):
        self.assertIn("dashboard", available_reporters())

    def test_available_reporters_includes_core(self):
        for name in ("json", "markdown", "console", "csv", "html", "xml", "sarif", "junit"):
            with self.subTest(name=name):
                self.assertIn(name, available_reporters())

    def test_get_reporter_class_returns_class(self):
        cls = get_reporter_class("json")
        self.assertIsNotNone(cls)
        self.assertTrue(callable(cls))

    def test_get_reporter_class_unknown_returns_none(self):
        self.assertIsNone(get_reporter_class("nonexistent"))

    def test_get_reporter_instantiates(self):
        reporter = get_reporter("json")
        self.assertTrue(hasattr(reporter, "render"))

    def test_get_reporter_dashboard_instantiates(self):
        reporter = get_reporter("dashboard")
        self.assertTrue(hasattr(reporter, "render"))

    def test_get_reporter_unknown_raises_value_error(self):
        with self.assertRaises(ValueError) as ctx:
            get_reporter("totally_unknown")
        self.assertIn("totally_unknown", str(ctx.exception))

    def test_get_reporter_error_message_lists_available(self):
        try:
            get_reporter("nope")
        except ValueError as exc:
            self.assertIn("json", str(exc))


if __name__ == "__main__":
    unittest.main()
