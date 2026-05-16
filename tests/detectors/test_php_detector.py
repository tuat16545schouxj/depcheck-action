import json
import tempfile
import unittest
from pathlib import Path

from src.detectors.php_detector import PhpDetector


class TestPhpDetector(unittest.TestCase):
    def setUp(self):
        self.detector = PhpDetector()
        self.tmp = tempfile.mkdtemp()

    def _write_temp(self, filename: str, content: str) -> Path:
        p = Path(self.tmp) / filename
        p.write_text(content)
        return p

    def test_supports_composer_json(self):
        self.assertTrue(self.detector.supports(Path("composer.json")))

    def test_supports_composer_lock(self):
        self.assertTrue(self.detector.supports(Path("composer.lock")))

    def test_does_not_support_other_files(self):
        self.assertFalse(self.detector.supports(Path("package.json")))
        self.assertFalse(self.detector.supports(Path("requirements.txt")))

    def test_parse_composer_json(self):
        data = {
            "require": {
                "php": ">=8.0",
                "ext-json": "*",
                "laravel/framework": "^10.0",
                "guzzlehttp/guzzle": "^7.5",
            },
            "require-dev": {
                "phpunit/phpunit": "^10.1"
            },
        }
        p = self._write_temp("composer.json", json.dumps(data))
        result = self.detector.detect(p)
        self.assertEqual(result.ecosystem, "php")
        names = [d.name for d in result.dependencies]
        self.assertIn("laravel/framework", names)
        self.assertIn("guzzlehttp/guzzle", names)
        self.assertIn("phpunit/phpunit", names)
        self.assertNotIn("php", names)
        self.assertNotIn("ext-json", names)

    def test_parse_composer_json_dev_flag(self):
        data = {
            "require": {"laravel/framework": "^10.0"},
            "require-dev": {"phpunit/phpunit": "^10.1"},
        }
        p = self._write_temp("composer.json", json.dumps(data))
        result = self.detector.detect(p)
        dev_deps = {d.name: d.dev for d in result.dependencies}
        self.assertFalse(dev_deps["laravel/framework"])
        self.assertTrue(dev_deps["phpunit/phpunit"])

    def test_parse_composer_lock(self):
        data = {
            "packages": [
                {"name": "laravel/framework", "version": "v10.3.0"},
                {"name": "guzzlehttp/guzzle", "version": "7.5.1"},
            ],
            "packages-dev": [
                {"name": "phpunit/phpunit", "version": "10.1.3"}
            ],
        }
        p = self._write_temp("composer.lock", json.dumps(data))
        result = self.detector.detect(p)
        names = [d.name for d in result.dependencies]
        self.assertIn("laravel/framework", names)
        self.assertIn("phpunit/phpunit", names)
        fw = next(d for d in result.dependencies if d.name == "laravel/framework")
        self.assertEqual(fw.current_version, "10.3.0")

    def test_parse_invalid_json(self):
        p = self._write_temp("composer.json", "not valid json {{{")
        result = self.detector.detect(p)
        self.assertEqual(result.dependencies, [])


if __name__ == "__main__":
    unittest.main()
