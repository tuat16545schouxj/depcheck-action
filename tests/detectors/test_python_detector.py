"""Tests for PythonDetector."""

import os
import tempfile
import unittest
from unittest.mock import patch

from src.detectors.python_detector import PythonDetector
from src.detectors.base import Dependency


class TestPythonDetector(unittest.TestCase):
    def setUp(self):
        self.detector = PythonDetector()

    def _write_temp(self, filename: str, content: str, base_dir: str) -> str:
        path = os.path.join(base_dir, filename)
        with open(path, "w") as f:
            f.write(content)
        return path

    def test_supports_requirements_txt(self):
        self.assertTrue(self.detector.supports("requirements.txt"))

    def test_supports_pyproject_toml(self):
        self.assertTrue(self.detector.supports("pyproject.toml"))

    def test_does_not_support_package_json(self):
        self.assertFalse(self.detector.supports("package.json"))

    def test_parse_requirements_txt(self):
        content = "requests==2.28.0\nnumpy==1.24.0\n"
        with tempfile.TemporaryDirectory() as tmpdir:
            self._write_temp("requirements.txt", content, tmpdir)
            with patch.object(self.detector, "_fetch_latest_pypi", return_value=None):
                results = self.detector.detect(tmpdir)

        self.assertEqual(len(results), 1)
        result = results[0]
        self.assertEqual(result.ecosystem, "python")
        self.assertEqual(result.total, 2)
        names = {d.name for d in result.dependencies}
        self.assertIn("requests", names)
        self.assertIn("numpy", names)

    def test_outdated_flagged_correctly(self):
        dep = Dependency(
            name="requests",
            current_version="2.28.0",
            latest_version="2.31.0",
            ecosystem="python",
        )
        self.assertTrue(dep.is_outdated)

    def test_up_to_date_not_flagged(self):
        dep = Dependency(
            name="requests",
            current_version="2.31.0",
            latest_version="2.31.0",
            ecosystem="python",
        )
        self.assertFalse(dep.is_outdated)

    def test_detect_marks_outdated_with_latest(self):
        content = "flask==2.0.0\n"
        with tempfile.TemporaryDirectory() as tmpdir:
            self._write_temp("requirements.txt", content, tmpdir)
            with patch.object(self.detector, "_fetch_latest_pypi", return_value="3.0.0"):
                results = self.detector.detect(tmpdir)

        self.assertEqual(len(results[0].outdated), 1)
        self.assertEqual(results[0].outdated[0].latest_version, "3.0.0")

    def test_empty_requirements_returns_no_deps(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            self._write_temp("requirements.txt", "# just a comment\n", tmpdir)
            with patch.object(self.detector, "_fetch_latest_pypi", return_value=None):
                results = self.detector.detect(tmpdir)
        self.assertEqual(results[0].total, 0)


if __name__ == "__main__":
    unittest.main()
