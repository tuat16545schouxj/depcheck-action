import os
import tempfile
import unittest
from pathlib import Path

from src.updaters.java_updater import JavaUpdater
from src.detectors.base import Dependency


def _dep(name, current, latest=None):
    return Dependency(name=name, current_version=current, latest=latest, ecosystem="java")


class TestJavaUpdater(unittest.TestCase):
    def setUp(self):
        self.updater = JavaUpdater()
        self.tmpdir = tempfile.mkdtemp()

    def _write(self, filename, content):
        path = os.path.join(self.tmpdir, filename)
        Path(path).write_text(content)
        return path

    def test_supports_pom_xml(self):
        self.assertTrue(self.updater.supports("pom.xml"))

    def test_supports_build_gradle(self):
        self.assertTrue(self.updater.supports("build.gradle"))

    def test_does_not_support_other_files(self):
        self.assertFalse(self.updater.supports("settings.gradle"))
        self.assertFalse(self.updater.supports("requirements.txt"))

    def test_update_pom_xml(self):
        content = (
            "<dependency>\n"
            "  <artifactId>jackson-databind</artifactId>\n"
            "  <version>2.13.0</version>\n"
            "</dependency>\n"
        )
        path = self._write("pom.xml", content)
        dep = _dep("jackson-databind", "2.13.0", latest="2.15.2")
        summary = self.updater.update(path, [dep])
        updated = Path(path).read_text()
        self.assertIn("2.15.2", updated)
        self.assertNotIn("2.13.0", updated)
        self.assertTrue(summary.results[0].success)

    def test_update_pom_xml_no_match(self):
        content = "<project></project>\n"
        path = self._write("pom.xml", content)
        dep = _dep("missing-lib", "1.0.0", latest="2.0.0")
        summary = self.updater.update(path, [dep])
        self.assertFalse(summary.results[0].success)
        self.assertIn("Pattern not found", summary.results[0].error)

    def test_update_build_gradle(self):
        content = 'implementation "com.google.guava:guava:30.1-jre"\n'
        path = self._write("build.gradle", content)
        dep = _dep("guava", "30.1-jre", latest="32.1.2-jre")
        summary = self.updater.update(path, [dep])
        updated = Path(path).read_text()
        self.assertIn("32.1.2-jre", updated)
        self.assertNotIn("30.1-jre", updated)
        self.assertTrue(summary.results[0].success)

    def test_update_build_gradle_no_match(self):
        content = 'implementation "org.example:other-lib:1.0.0"\n'
        path = self._write("build.gradle", content)
        dep = _dep("missing-lib", "1.0.0", latest="2.0.0")
        summary = self.updater.update(path, [dep])
        self.assertFalse(summary.results[0].success)

    def test_skips_dep_without_latest(self):
        content = (
            "<dependency>\n"
            "  <artifactId>some-lib</artifactId>\n"
            "  <version>1.0.0</version>\n"
            "</dependency>\n"
        )
        path = self._write("pom.xml", content)
        dep = _dep("some-lib", "1.0.0", latest=None)
        summary = self.updater.update(path, [dep])
        self.assertEqual(len(summary.results), 0)
        self.assertIn("1.0.0", Path(path).read_text())


if __name__ == "__main__":
    unittest.main()
