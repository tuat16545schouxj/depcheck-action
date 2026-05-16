import os
import tempfile
import unittest
from src.detectors.rust_detector import RustDetector


class TestRustDetector(unittest.TestCase):

    def setUp(self):
        self.detector = RustDetector()
        self.tmpdir = tempfile.mkdtemp()

    def _write_temp(self, filename: str, content: str) -> str:
        path = os.path.join(self.tmpdir, filename)
        with open(path, "w") as f:
            f.write(content)
        return path

    def test_supports_cargo_toml(self):
        self.assertTrue(self.detector.supports("Cargo.toml"))

    def test_supports_cargo_lock(self):
        self.assertTrue(self.detector.supports("Cargo.lock"))

    def test_does_not_support_other_files(self):
        self.assertFalse(self.detector.supports("setup.py"))
        self.assertFalse(self.detector.supports("package.json"))

    def test_parse_cargo_toml_basic(self):
        content = """
[package]
name = "my_crate"
version = "0.1.0"

[dependencies]
serde = "1.0"
tokio = { version = "1.28", features = ["full"] }

[dev-dependencies]
pretty_assertions = "1.3"
"""
        path = self._write_temp("Cargo.toml", content)
        result = self.detector.detect(path)
        self.assertEqual(result.ecosystem, "rust")
        names = [d.name for d in result.dependencies]
        self.assertIn("serde", names)
        self.assertIn("tokio", names)
        self.assertIn("pretty_assertions", names)

    def test_parse_cargo_toml_versions(self):
        content = """
[dependencies]
serde = "^1.0.150"
log = ">=0.4"
"""
        path = self._write_temp("Cargo.toml", content)
        result = self.detector.detect(path)
        version_map = {d.name: d.current_version for d in result.dependencies}
        self.assertEqual(version_map["serde"], "1.0.150")
        self.assertEqual(version_map["log"], "0.4")

    def test_parse_cargo_lock(self):
        content = """
[[package]]
name = "serde"
version = "1.0.152"

[[package]]
name = "tokio"
version = "1.28.0"
"""
        path = self._write_temp("Cargo.lock", content)
        result = self.detector.detect(path)
        self.assertEqual(result.ecosystem, "rust")
        names = [d.name for d in result.dependencies]
        self.assertIn("serde", names)
        self.assertIn("tokio", names)

    def test_empty_cargo_toml(self):
        content = "[package]\nname = \"empty\"\nversion = \"0.1.0\"\n"
        path = self._write_temp("Cargo.toml", content)
        result = self.detector.detect(path)
        self.assertEqual(result.dependencies, [])


if __name__ == "__main__":
    unittest.main()
