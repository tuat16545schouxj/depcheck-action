import json
import os
import tempfile
import unittest
from pathlib import Path

from src.detectors.dotnet_detector import DotnetDetector


class TestDotnetDetector(unittest.TestCase):
    def setUp(self):
        self.detector = DotnetDetector()
        self.tmpdir = tempfile.mkdtemp()

    def _write_temp(self, filename: str, content: str) -> str:
        path = os.path.join(self.tmpdir, filename)
        Path(path).write_text(content, encoding="utf-8")
        return path

    def test_supports_csproj(self):
        self.assertTrue(self.detector.supports("MyApp.csproj"))

    def test_supports_packages_lock(self):
        self.assertTrue(self.detector.supports("packages.lock.json"))

    def test_does_not_support_other_files(self):
        self.assertFalse(self.detector.supports("requirements.txt"))
        self.assertFalse(self.detector.supports("package.json"))

    def test_parse_csproj(self):
        content = """<Project Sdk="Microsoft.NET.Sdk">
  <ItemGroup>
    <PackageReference Include="Newtonsoft.Json" Version="13.0.1" />
    <PackageReference Include="Serilog" Version="2.12.0" />
  </ItemGroup>
</Project>"""
        path = self._write_temp("MyApp.csproj", content)
        result = self.detector.detect(path)
        self.assertEqual(result.ecosystem, "dotnet")
        names = [d.name for d in result.dependencies]
        self.assertIn("Newtonsoft.Json", names)
        self.assertIn("Serilog", names)
        versions = {d.name: d.current_version for d in result.dependencies}
        self.assertEqual(versions["Newtonsoft.Json"], "13.0.1")

    def test_parse_packages_lock_json(self):
        data = {
            "version": 1,
            "dependencies": {
                "net6.0": {
                    "Newtonsoft.Json": {"type": "Direct", "requested": "[13.0.1, )", "resolved": "13.0.1"},
                    "Serilog": {"type": "Direct", "requested": "[2.12.0, )", "resolved": "2.12.0"}
                }
            }
        }
        path = self._write_temp("packages.lock.json", json.dumps(data))
        result = self.detector.detect(path)
        self.assertEqual(result.ecosystem, "dotnet")
        names = [d.name for d in result.dependencies]
        self.assertIn("Newtonsoft.Json", names)
        self.assertIn("Serilog", names)

    def test_empty_csproj_returns_no_deps(self):
        content = '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup></PropertyGroup></Project>'
        path = self._write_temp("Empty.csproj", content)
        result = self.detector.detect(path)
        self.assertEqual(result.dependencies, [])

    def test_malformed_csproj_returns_no_deps(self):
        path = self._write_temp("Bad.csproj", "<<not valid xml>>")
        result = self.detector.detect(path)
        self.assertEqual(result.dependencies, [])


if __name__ == "__main__":
    unittest.main()
