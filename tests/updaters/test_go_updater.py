import unittest
from pathlib import Path
from unittest.mock import patch
import tempfile
import os

from src.updaters.go_updater import GoUpdater
from src.detectors.base import Dependency


def _dep(name: str, current: str, latest: str) -> Dependency:
    return Dependency(name=name, current_version=current, latest_version=latest, ecosystem="go")


class TestGoUpdater(unittest.TestCase):

    def setUp(self):
        self.updater = GoUpdater()
        self.tmp = tempfile.mkdtemp()

    def _write(self, filename: str, content: str) -> str:
        path = os.path.join(self.tmp, filename)
        Path(path).write_text(content)
        return path

    def test_supports_go_mod(self):
        self.assertTrue(self.updater.supports("go.mod"))
        self.assertTrue(self.updater.supports("/some/path/go.mod"))

    def test_does_not_support_go_sum(self):
        self.assertFalse(self.updater.supports("go.sum"))

    def test_does_not_support_other_files(self):
        self.assertFalse(self.updater.supports("package.json"))

    def test_updates_inline_require(self):
        content = (
            "module example.com/myapp\n\n"
            "require github.com/foo/bar v1.0.0\n"
        )
        path = self._write("go.mod", content)
        dep = _dep("github.com/foo/bar", "v1.0.0", "v1.2.3")

        with patch.object(self.updater, "_run_go_mod_tidy"):
            summary = self.updater.update(path, [dep])

        self.assertTrue(summary.results[0].success)
        updated = Path(path).read_text()
        self.assertIn("v1.2.3", updated)
        self.assertNotIn("v1.0.0", updated)

    def test_updates_block_require(self):
        content = (
            "module example.com/myapp\n\n"
            "require (\n"
            "\tgithub.com/pkg/errors v0.9.0\n"
            "\tgithub.com/stretchr/testify v1.7.0\n"
            ")\n"
        )
        path = self._write("go.mod", content)
        dep = _dep("github.com/pkg/errors", "v0.9.0", "v0.9.1")

        with patch.object(self.updater, "_run_go_mod_tidy"):
            summary = self.updater.update(path, [dep])

        self.assertTrue(summary.results[0].success)
        updated = Path(path).read_text()
        self.assertIn("v0.9.1", updated)
        self.assertIn("v1.7.0", updated)  # untouched

    def test_fails_gracefully_when_dep_not_found(self):
        content = "module example.com/myapp\n"
        path = self._write("go.mod", content)
        dep = _dep("github.com/missing/pkg", "v1.0.0", "v2.0.0")

        summary = self.updater.update(path, [dep])

        self.assertFalse(summary.results[0].success)
        self.assertIsNotNone(summary.results[0].error)

    def test_fails_gracefully_when_no_latest(self):
        content = "module example.com/myapp\n"
        path = self._write("go.mod", content)
        dep = Dependency(name="github.com/foo/bar", current_version="v1.0.0", latest_version=None, ecosystem="go")

        summary = self.updater.update(path, [dep])

        self.assertFalse(summary.results[0].success)

    def test_file_not_found_returns_empty_summary(self):
        dep = _dep("github.com/foo/bar", "v1.0.0", "v2.0.0")
        summary = self.updater.update("/nonexistent/go.mod", [dep])
        self.assertEqual(len(summary.results), 0)


if __name__ == "__main__":
    unittest.main()
