"""Tests for Python and Node updaters, and the updater registry."""
import json
import os
import tempfile
import unittest

from src.updaters.python_updater import PythonUpdater
from src.updaters.node_updater import NodeUpdater
from src.updaters.registry import updater_for_file, apply_updates


class TestPythonUpdater(unittest.TestCase):
    def setUp(self):
        self.updater = PythonUpdater()
        self.tmp = tempfile.mkdtemp()

    def _write(self, name: str, content: str) -> str:
        path = os.path.join(self.tmp, name)
        with open(path, "w") as f:
            f.write(content)
        return path

    def test_supports_requirements_txt(self):
        self.assertTrue(self.updater.supports("/repo/requirements.txt"))

    def test_supports_pyproject_toml(self):
        self.assertTrue(self.updater.supports("/repo/pyproject.toml"))

    def test_does_not_support_other(self):
        self.assertFalse(self.updater.supports("/repo/package.json"))

    def test_update_requirements_txt(self):
        path = self._write("requirements.txt", "requests==2.28.0\nflask>=2.0.0\n")
        result = self.updater.update(path, "requests", "2.28.0", "2.31.0")
        self.assertTrue(result.success)
        content = open(path).read()
        self.assertIn("requests==2.31.0", content)

    def test_update_missing_dep_fails(self):
        path = self._write("requirements.txt", "flask==2.0.0\n")
        result = self.updater.update(path, "requests", "2.28.0", "2.31.0")
        self.assertFalse(result.success)


class TestNodeUpdater(unittest.TestCase):
    def setUp(self):
        self.updater = NodeUpdater()
        self.tmp = tempfile.mkdtemp()

    def _write_pkg(self, deps: dict, dev_deps: dict = None) -> str:
        data = {"name": "test", "version": "1.0.0", "dependencies": deps}
        if dev_deps:
            data["devDependencies"] = dev_deps
        path = os.path.join(self.tmp, "package.json")
        with open(path, "w") as f:
            json.dump(data, f)
        return path

    def test_supports_package_json(self):
        self.assertTrue(self.updater.supports("/repo/package.json"))

    def test_does_not_support_other(self):
        self.assertFalse(self.updater.supports("/repo/requirements.txt"))

    def test_update_dependency(self):
        path = self._write_pkg({"axios": "^0.27.0"})
        result = self.updater.update(path, "axios", "0.27.0", "1.4.0")
        self.assertTrue(result.success)
        data = json.loads(open(path).read())
        self.assertEqual(data["dependencies"]["axios"], "^1.4.0")

    def test_update_missing_dep_fails(self):
        path = self._write_pkg({"lodash": "4.17.21"})
        result = self.updater.update(path, "axios", "0.27.0", "1.4.0")
        self.assertFalse(result.success)


class TestUpdaterRegistry(unittest.TestCase):
    def test_updater_for_requirements_txt(self):
        updater = updater_for_file("requirements.txt")
        self.assertIsNotNone(updater)
        self.assertEqual(updater.ecosystem, "python")

    def test_updater_for_package_json(self):
        updater = updater_for_file("package.json")
        self.assertIsNotNone(updater)
        self.assertEqual(updater.ecosystem, "node")

    def test_updater_for_unknown_returns_none(self):
        self.assertIsNone(updater_for_file("Makefile"))

    def test_apply_updates_unknown_file(self):
        summary = apply_updates([{"file_path": "Makefile", "name": "foo",
                                   "old_version": "1.0", "new_version": "2.0"}])
        self.assertEqual(len(summary.failed), 1)
        self.assertEqual(summary.failed[0].ecosystem, "unknown")


if __name__ == "__main__":
    unittest.main()
