import tempfile
import unittest
from pathlib import Path

from src.updaters.dotnet_updater import DotnetUpdater
from src.detectors.base import Dependency


def _dep(name, current, latest):
    return Dependency(name=name, current=current, latest=latest, ecosystem="dotnet")


CSPROJ_TEMPLATE = """<Project Sdk="Microsoft.NET.Sdk">
  <ItemGroup>
    <PackageReference Include="Newtonsoft.Json" Version="12.0.3" />
    <PackageReference Include="Serilog" Version="2.10.0" />
  </ItemGroup>
</Project>
"""


class TestDotnetUpdater(unittest.TestCase):

    def setUp(self):
        self.updater = DotnetUpdater()
        self.tmp = tempfile.mkdtemp()

    def _write(self, filename: str, content: str) -> str:
        path = Path(self.tmp) / filename
        path.write_text(content)
        return str(path)

    def test_supports_csproj(self):
        self.assertTrue(self.updater.supports("MyApp.csproj"))

    def test_does_not_support_packages_lock(self):
        self.assertFalse(self.updater.supports("packages.lock.json"))

    def test_does_not_support_random_file(self):
        self.assertFalse(self.updater.supports("go.mod"))

    def test_update_single_package(self):
        path = self._write("App.csproj", CSPROJ_TEMPLATE)
        dep = _dep("Newtonsoft.Json", "12.0.3", "13.0.3")
        summary = self.updater.update(path, [dep])
        content = Path(path).read_text()
        self.assertIn('Version="13.0.3"', content)
        self.assertEqual(summary.updated, 1)

    def test_update_multiple_packages(self):
        path = self._write("App.csproj", CSPROJ_TEMPLATE)
        deps = [
            _dep("Newtonsoft.Json", "12.0.3", "13.0.3"),
            _dep("Serilog", "2.10.0", "3.1.1"),
        ]
        summary = self.updater.update(path, deps)
        content = Path(path).read_text()
        self.assertIn('Version="13.0.3"', content)
        self.assertIn('Version="3.1.1"', content)
        self.assertEqual(summary.updated, 2)

    def test_missing_package_reports_failure(self):
        path = self._write("App.csproj", CSPROJ_TEMPLATE)
        dep = _dep("Missing.Package", "1.0.0", "2.0.0")
        summary = self.updater.update(path, [dep])
        self.assertEqual(summary.updated, 0)
        self.assertEqual(summary.skipped, 1)

    def test_no_latest_reports_failure(self):
        path = self._write("App.csproj", CSPROJ_TEMPLATE)
        dep = _dep("Newtonsoft.Json", "12.0.3", None)
        summary = self.updater.update(path, [dep])
        self.assertEqual(summary.updated, 0)
        self.assertEqual(summary.skipped, 1)

    def test_original_unchanged_when_no_updates(self):
        path = self._write("App.csproj", CSPROJ_TEMPLATE)
        dep = _dep("Ghost.Pkg", "1.0", None)
        self.updater.update(path, [dep])
        self.assertEqual(Path(path).read_text(), CSPROJ_TEMPLATE)

    def test_summary_ecosystem(self):
        path = self._write("App.csproj", CSPROJ_TEMPLATE)
        summary = self.updater.update(path, [])
        self.assertEqual(summary.ecosystem, "dotnet")


if __name__ == "__main__":
    unittest.main()
