import os
import tempfile
import unittest
from pathlib import Path

from src.detectors.base import Dependency
from src.updaters.ruby_updater import RubyUpdater


class TestRubyUpdater(unittest.TestCase):
    def setUp(self):
        self.updater = RubyUpdater()
        self.tmp = tempfile.mkdtemp()

    def _write(self, filename: str, content: str) -> str:
        path = os.path.join(self.tmp, filename)
        Path(path).write_text(content, encoding="utf-8")
        return path

    def _dep(self, name, current, latest):
        return Dependency(name=name, current_version=current, latest_version=latest, ecosystem="ruby")

    # --- supports ---

    def test_supports_gemfile(self):
        self.assertTrue(self.updater.supports("Gemfile"))

    def test_does_not_support_gemfile_lock(self):
        self.assertFalse(self.updater.supports("Gemfile.lock"))

    def test_does_not_support_random_file(self):
        self.assertFalse(self.updater.supports("requirements.txt"))

    # --- update ---

    def test_updates_single_gem(self):
        path = self._write("Gemfile", 'gem "rails", "6.1.0"\n')
        dep = self._dep("rails", "6.1.0", "7.0.4")
        summary = self.updater.update(path, [dep])
        updated = Path(path).read_text()
        self.assertIn('"7.0.4"', updated)
        self.assertEqual(len(summary.succeeded()), 1)

    def test_updates_single_quoted_gem(self):
        path = self._write("Gemfile", "gem 'nokogiri', '1.12.0'\n")
        dep = self._dep("nokogiri", "1.12.0", "1.15.2")
        summary = self.updater.update(path, [dep])
        updated = Path(path).read_text()
        self.assertIn("'1.15.2'", updated)

    def test_no_update_when_no_latest(self):
        path = self._write("Gemfile", 'gem "rack", "2.0.0"\n')
        dep = Dependency(name="rack", current_version="2.0.0", latest_version=None, ecosystem="ruby")
        summary = self.updater.update(path, [dep])
        self.assertEqual(len(summary.failed()), 1)
        self.assertIn("No latest version", summary.failed()[0].message)

    def test_no_update_when_gem_not_pinned(self):
        path = self._write("Gemfile", 'gem "devise"\n')
        dep = self._dep("devise", None, "4.9.0")
        summary = self.updater.update(path, [dep])
        self.assertEqual(len(summary.failed()), 1)

    def test_updates_multiple_gems(self):
        content = 'gem "rails", "6.0.0"\ngem "rspec", "3.10.0"\n'
        path = self._write("Gemfile", content)
        deps = [
            self._dep("rails", "6.0.0", "7.0.4"),
            self._dep("rspec", "3.10.0", "3.12.0"),
        ]
        summary = self.updater.update(path, deps)
        updated = Path(path).read_text()
        self.assertIn('"7.0.4"', updated)
        self.assertIn('"3.12.0"', updated)
        self.assertEqual(len(summary.succeeded()), 2)

    def test_file_unchanged_when_nothing_to_update(self):
        content = 'gem "devise"\n'
        path = self._write("Gemfile", content)
        dep = self._dep("devise", None, "4.9.0")
        self.updater.update(path, [dep])
        self.assertEqual(Path(path).read_text(), content)


if __name__ == "__main__":
    unittest.main()
