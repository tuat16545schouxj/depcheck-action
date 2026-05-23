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

    def test_update_does_not_modify_other_deps(self):
        """Ensure updating one dependency leaves other dependencies unchanged."""
        path = self._write("requirements.txt", "requests==2.28.0\nflask>=2.0.0\n")
        self.updater.update(path, "requests", "2.28.0", "2.31.0")
        content = open(path).read()
        self.assertIn("flask>=2.0.0", content)


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

    def test_update_dev_dependency(self):
        """Ensure a dev dependency can be updated when not present in dependencies."""
        path = self._write_pkg({"lodash": "4.17.21"}, dev_deps={"jest": "^28.0.0"})
        result = self.updater.update(path, "jest", "28.0.0", "29.0.0")
        self.assertTrue(result.success)
        data = json.loads(open(path).read())
        self.assertEqual(data["devDependencies"]["jest"], "^29.0.0")

    def test_update_missing_dep_fails(self):
        path = self._write_pkg({"lodash": "4.17.21"})
        result = self.updater.update(path, "axios", "0.27.0", "1.4.0")
        self.assertFalse(result.success)


class TestUpdaterRegistry(unittest.TestCase):
    def test_updater_for_requirements_txt(self):
        updater = updater_for_file("requirements.txt")
        self.assertIsNotNone(updater)
        self.assertEqual(updater.eco