import json
import tempfile
import unittest
from pathlib import Path

from src.updaters.php_updater import PhpUpdater
from src.detectors.base import Dependency


def _dep(name, current, latest):
    return Dependency(name=name, current=current, latest=latest, ecosystem="php")


class TestPhpUpdater(unittest.TestCase):

    def setUp(self):
        self.updater = PhpUpdater()
        self.tmp = tempfile.mkdtemp()

    def _write(self, filename: str, content: str) -> str:
        path = Path(self.tmp) / filename
        path.write_text(content)
        return str(path)

    def test_supports_composer_json(self):
        self.assertTrue(self.updater.supports("composer.json"))

    def test_does_not_support_composer_lock(self):
        self.assertFalse(self.updater.supports("composer.lock"))

    def test_does_not_support_random_file(self):
        self.assertFalse(self.updater.supports("package.json"))

    def test_update_require_section(self):
        data = {"require": {"guzzlehttp/guzzle": "^6.5"}}
        path = self._write("composer.json", json.dumps(data))
        dep = _dep("guzzlehttp/guzzle", "6.5", "7.8.0")
        summary = self.updater.update(path, [dep])
        updated_data = json.loads(Path(path).read_text())
        self.assertEqual(updated_data["require"]["guzzlehttp/guzzle"], "^7.8.0")
        self.assertEqual(summary.updated, 1)

    def test_update_require_dev_section(self):
        data = {"require-dev": {"phpunit/phpunit": "~9.0"}}
        path = self._write("composer.json", json.dumps(data))
        dep = _dep("phpunit/phpunit", "9.0", "10.5.0")
        summary = self.updater.update(path, [dep])
        updated_data = json.loads(Path(path).read_text())
        self.assertEqual(updated_data["require-dev"]["phpunit/phpunit"], "~10.5.0")
        self.assertEqual(summary.updated, 1)

    def test_dep_not_in_file_reports_failure(self):
        data = {"require": {}}
        path = self._write("composer.json", json.dumps(data))
        dep = _dep("missing/pkg", "1.0", "2.0")
        summary = self.updater.update(path, [dep])
        self.assertEqual(summary.updated, 0)
        self.assertEqual(summary.skipped, 1)

    def test_no_latest_reports_failure(self):
        data = {"require": {"vendor/pkg": "^1.0"}}
        path = self._write("composer.json", json.dumps(data))
        dep = _dep("vendor/pkg", "1.0", None)
        summary = self.updater.update(path, [dep])
        self.assertEqual(summary.updated, 0)
        self.assertEqual(summary.skipped, 1)

    def test_preserve_constraint_caret(self):
        result = self.updater._preserve_constraint("^1.2.3", "2.0.0")
        self.assertEqual(result, "^2.0.0")

    def test_preserve_constraint_tilde(self):
        result = self.updater._preserve_constraint("~1.2", "1.5.0")
        self.assertEqual(result, "~1.5.0")

    def test_preserve_constraint_no_prefix(self):
        result = self.updater._preserve_constraint("1.0.0", "2.0.0")
        self.assertEqual(result, "2.0.0")

    def test_summary_ecosystem(self):
        data = {"require": {}}
        path = self._write("composer.json", json.dumps(data))
        summary = self.updater.update(path, [])
        self.assertEqual(summary.ecosystem, "php")


if __name__ == "__main__":
    unittest.main()
