"""Tests for NodeDetector."""
import json
import tempfile
from pathlib import Path
import unittest

from src.detectors.node_detector import NodeDetector


class TestNodeDetector(unittest.TestCase):
    def setUp(self):
        self.detector = NodeDetector()
        self.tmp = tempfile.mkdtemp()
        self.repo = Path(self.tmp)

    def _write_package_json(self, data: dict) -> Path:
        p = self.repo / "package.json"
        p.write_text(json.dumps(data), encoding="utf-8")
        return p

    # --- supports() ---

    def test_supports_package_json(self):
        self.assertTrue(self.detector.supports(Path("package.json")))

    def test_does_not_support_other_files(self):
        self.assertFalse(self.detector.supports(Path("requirements.txt")))
        self.assertFalse(self.detector.supports(Path("Pipfile")))

    # --- detect() ---

    def test_no_manifest_returns_empty(self):
        result = self.detector.detect(self.repo)
        self.assertEqual(result.ecosystem, "node")
        self.assertEqual(result.dependencies, [])
        self.assertEqual(result.manifests, [])

    def test_parses_dependencies(self):
        self._write_package_json({"dependencies": {"express": "^4.18.2", "lodash": "~4.17.21"}})
        result = self.detector.detect(self.repo)
        names = {d.name for d in result.dependencies}
        self.assertIn("express", names)
        self.assertIn("lodash", names)

    def test_parses_dev_dependencies(self):
        self._write_package_json({"devDependencies": {"jest": "^29.0.0"}})
        result = self.detector.detect(self.repo)
        self.assertEqual(len(result.dependencies), 1)
        self.assertEqual(result.dependencies[0].name, "jest")

    def test_version_stripping(self):
        self._write_package_json({"dependencies": {"react": "^18.2.0"}})
        result = self.detector.detect(self.repo)
        self.assertEqual(result.dependencies[0].current_version, "18.2.0")

    def test_wildcard_version_is_none(self):
        self._write_package_json({"dependencies": {"some-pkg": "*"}})
        result = self.detector.detect(self.repo)
        self.assertIsNone(result.dependencies[0].current_version)

    def test_ecosystem_is_node(self):
        self._write_package_json({"dependencies": {"axios": "1.6.0"}})
        result = self.detector.detect(self.repo)
        self.assertEqual(result.dependencies[0].ecosystem, "node")

    def test_invalid_json_returns_empty(self):
        (self.repo / "package.json").write_text("not valid json", encoding="utf-8")
        result = self.detector.detect(self.repo)
        self.assertEqual(result.dependencies, [])


if __name__ == "__main__":
    unittest.main()
