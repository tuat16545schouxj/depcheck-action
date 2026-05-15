import os
import tempfile
import unittest
from pathlib import Path
from src.detectors.go_detector import GoDetector


class TestGoDetector(unittest.TestCase):
    def setUp(self):
        self.detector = GoDetector()
        self.tmpdir = tempfile.mkdtemp()

    def _write_temp(self, filename: str, content: str) -> str:
        path = os.path.join(self.tmpdir, filename)
        Path(path).write_text(content, encoding="utf-8")
        return path

    def test_supports_go_mod(self):
        self.assertTrue(self.detector.supports("go.mod"))

    def test_supports_go_sum(self):
        self.assertTrue(self.detector.supports("go.sum"))

    def test_does_not_support_other_files(self):
        self.assertFalse(self.detector.supports("package.json"))
        self.assertFalse(self.detector.supports("requirements.txt"))

    def test_parse_go_mod_single_require(self):
        content = 'module example.com/myapp\n\ngo 1.21\n\nrequire github.com/gin-gonic/gin v1.9.1\n'
        path = self._write_temp("go.mod", content)
        result = self.detector.detect(path)
        self.assertEqual(result.ecosystem, "go")
        self.assertEqual(len(result.dependencies), 1)
        dep = result.dependencies[0]
        self.assertEqual(dep.name, "github.com/gin-gonic/gin")
        self.assertEqual(dep.current_version, "1.9.1")

    def test_parse_go_mod_require_block(self):
        content = (
            "module example.com/myapp\n\ngo 1.21\n\nrequire (\n"
            "\tgithub.com/stretchr/testify v1.8.4\n"
            "\tgolang.org/x/net v0.20.0 // indirect\n"
            ")\n"
        )
        path = self._write_temp("go.mod", content)
        result = self.detector.detect(path)
        self.assertEqual(len(result.dependencies), 2)
        names = [d.name for d in result.dependencies]
        self.assertIn("github.com/stretchr/testify", names)
        self.assertIn("golang.org/x/net", names)

    def test_parse_go_sum(self):
        content = (
            "github.com/gin-gonic/gin v1.9.1 h1:abc123==\n"
            "github.com/gin-gonic/gin v1.9.1/go.mod h1:def456==\n"
            "golang.org/x/net v0.20.0 h1:xyz789==\n"
        )
        path = self._write_temp("go.sum", content)
        result = self.detector.detect(path)
        self.assertEqual(result.ecosystem, "go")
        names = [d.name for d in result.dependencies]
        self.assertIn("github.com/gin-gonic/gin", names)
        self.assertIn("golang.org/x/net", names)
        # Duplicate module entries should be deduplicated
        self.assertEqual(len([d for d in result.dependencies if d.name == "github.com/gin-gonic/gin"]), 1)

    def test_clean_version_strips_v(self):
        self.assertEqual(self.detector._clean_version("v1.2.3"), "1.2.3")
        self.assertEqual(self.detector._clean_version("1.2.3"), "1.2.3")

    def test_empty_go_mod(self):
        path = self._write_temp("go.mod", "module example.com/empty\n\ngo 1.21\n")
        result = self.detector.detect(path)
        self.assertEqual(result.dependencies, [])


if __name__ == "__main__":
    unittest.main()
