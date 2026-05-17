import unittest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch

from src.updaters.rust_updater import RustUpdater
from src.detectors.base import Dependency


def _dep(name, current, latest=None, outdated=True):
    return Dependency(
        name=name,
        current_version=current,
        latest_version=latest,
        ecosystem="rust",
        outdated=outdated,
    )


class TestRustUpdater(unittest.TestCase):
    def setUp(self):
        self.updater = RustUpdater()
        self.tmpdir = tempfile.mkdtemp()

    def _write(self, filename, content):
        path = os.path.join(self.tmpdir, filename)
        Path(path).write_text(content)
        return path

    def test_supports_cargo_toml(self):
        self.assertTrue(self.updater.supports("Cargo.toml"))

    def test_does_not_support_cargo_lock(self):
        self.assertFalse(self.updater.supports("Cargo.lock"))

    def test_does_not_support_other_files(self):
        self.assertFalse(self.updater.supports("go.mod"))

    @patch.object(RustUpdater, "_run_cargo_update")
    def test_updates_simple_version(self, mock_cargo):
        content = '[dependencies]\nserde = "1.0.100"\n'
        path = self._write("Cargo.toml", content)
        dep = _dep("serde", "1.0.100", latest="1.0.197")
        summary = self.updater.update(path, [dep])
        updated = Path(path).read_text()
        self.assertIn('"1.0.197"', updated)
        self.assertTrue(summary.results[0].success)

    @patch.object(RustUpdater, "_run_cargo_update")
    def test_updates_inline_table_version(self, mock_cargo):
        content = '[dependencies]\ntokio = { version = "1.20.0", features = ["full"] }\n'
        path = self._write("Cargo.toml", content)
        dep = _dep("tokio", "1.20.0", latest="1.37.0")
        summary = self.updater.update(path, [dep])
        updated = Path(path).read_text()
        self.assertIn('"1.37.0"', updated)
        self.assertTrue(summary.results[0].success)

    @patch.object(RustUpdater, "_run_cargo_update")
    def test_skips_non_outdated(self, mock_cargo):
        content = '[dependencies]\nrand = "0.8.5"\n'
        path = self._write("Cargo.toml", content)
        dep = _dep("rand", "0.8.5", latest="0.8.5", outdated=False)
        self.updater.update(path, [dep])
        self.assertEqual(Path(path).read_text(), content)
        mock_cargo.assert_not_called()

    @patch.object(RustUpdater, "_run_cargo_update")
    def test_returns_failure_for_missing_dep(self, mock_cargo):
        content = '[dependencies]\nserde = "1.0.0"\n'
        path = self._write("Cargo.toml", content)
        dep = _dep("nonexistent", "0.1.0", latest="0.2.0")
        summary = self.updater.update(path, [dep])
        self.assertFalse(summary.results[0].success)
        self.assertIsNotNone(summary.results[0].error)

    def test_missing_file_returns_empty_summary(self):
        summary = self.updater.update("/nonexistent/Cargo.toml", [])
        self.assertEqual(len(summary.results), 0)

    @patch.object(RustUpdater, "_run_cargo_update")
    def test_cargo_update_called_on_change(self, mock_cargo):
        content = '[dependencies]\nlog = "0.4.0"\n'
        path = self._write("Cargo.toml", content)
        dep = _dep("log", "0.4.0", latest="0.4.21")
        self.updater.update(path, [dep])
        mock_cargo.assert_called_once()
