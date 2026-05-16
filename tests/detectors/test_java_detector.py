import os
import tempfile
import unittest
from src.detectors.java_detector import JavaDetector


class TestJavaDetector(unittest.TestCase):
    def setUp(self):
        self.detector = JavaDetector()
        self.tmpdir = tempfile.mkdtemp()

    def _write_temp(self, filename: str, content: str) -> str:
        path = os.path.join(self.tmpdir, filename)
        with open(path, "w") as f:
            f.write(content)
        return path

    def test_supports_pom_xml(self):
        self.assertTrue(self.detector.supports("pom.xml"))

    def test_supports_build_gradle(self):
        self.assertTrue(self.detector.supports("build.gradle"))

    def test_supports_build_gradle_kts(self):
        self.assertTrue(self.detector.supports("build.gradle.kts"))

    def test_does_not_support_other_files(self):
        self.assertFalse(self.detector.supports("settings.gradle"))
        self.assertFalse(self.detector.supports("requirements.txt"))

    def test_parse_pom_xml(self):
        content = """<project>
  <dependencies>
    <dependency>
      <groupId>org.springframework</groupId>
      <artifactId>spring-core</artifactId>
      <version>5.3.20</version>
    </dependency>
    <dependency>
      <groupId>junit</groupId>
      <artifactId>junit</artifactId>
      <version>4.13.2</version>
    </dependency>
  </dependencies>
</project>"""
        path = self._write_temp("pom.xml", content)
        result = self.detector.detect(path)
        self.assertEqual(result.ecosystem, "java")
        self.assertEqual(len(result.dependencies), 2)
        names = [d.name for d in result.dependencies]
        self.assertIn("org.springframework:spring-core", names)
        self.assertIn("junit:junit", names)
        versions = {d.name: d.current_version for d in result.dependencies}
        self.assertEqual(versions["org.springframework:spring-core"], "5.3.20")

    def test_parse_pom_xml_skips_property_versions(self):
        content = """<project>
  <dependencies>
    <dependency>
      <groupId>com.example</groupId>
      <artifactId>my-lib</artifactId>
      <version>${my.lib.version}</version>
    </dependency>
  </dependencies>
</project>"""
        path = self._write_temp("pom.xml", content)
        result = self.detector.detect(path)
        self.assertEqual(result.dependencies[0].current_version, "unknown")

    def test_parse_build_gradle(self):
        content = """dependencies {
    implementation 'org.springframework.boot:spring-boot-starter:2.7.0'
    testImplementation 'junit:junit:4.13.2'
    api "com.google.guava:guava:31.1-jre"
}"""
        path = self._write_temp("build.gradle", content)
        result = self.detector.detect(path)
        self.assertEqual(result.ecosystem, "java")
        self.assertEqual(len(result.dependencies), 3)
        names = [d.name for d in result.dependencies]
        self.assertIn("org.springframework.boot:spring-boot-starter", names)
        self.assertIn("junit:junit", names)

    def test_empty_pom_returns_no_deps(self):
        path = self._write_temp("pom.xml", "<project></project>")
        result = self.detector.detect(path)
        self.assertEqual(result.dependencies, [])


if __name__ == "__main__":
    unittest.main()
