import re
from pathlib import Path
from typing import List
from .base import BaseDetector, Dependency, DetectionResult


class JavaDetector(BaseDetector):
    """Detector for Java/Maven and Gradle projects."""

    SUPPORTED_FILES = {"pom.xml", "build.gradle", "build.gradle.kts"}

    def supports(self, filename: str) -> bool:
        return Path(filename).name in self.SUPPORTED_FILES

    def detect(self, filepath: str) -> DetectionResult:
        path = Path(filepath)
        name = path.name
        if name == "pom.xml":
            deps = self._parse_pom_xml(path)
        elif name in ("build.gradle", "build.gradle.kts"):
            deps = self._parse_build_gradle(path)
        else:
            deps = []
        return DetectionResult(ecosystem="java", source_file=filepath, dependencies=deps)

    def _parse_pom_xml(self, path: Path) -> List[Dependency]:
        deps = []
        content = path.read_text(encoding="utf-8")
        # Match <dependency> blocks
        block_re = re.compile(r"<dependency>(.*?)</dependency>", re.DOTALL)
        group_re = re.compile(r"<groupId>([^<]+)</groupId>")
        artifact_re = re.compile(r"<artifactId>([^<]+)</artifactId>")
        version_re = re.compile(r"<version>([^<]+)</version>")
        for block in block_re.findall(content):
            group = group_re.search(block)
            artifact = artifact_re.search(block)
            version = version_re.search(block)
            if group and artifact:
                name = f"{group.group(1)}:{artifact.group(1)}"
                ver = version.group(1) if version else "unknown"
                # Skip property placeholders
                if ver.startswith("${"):
                    ver = "unknown"
                deps.append(Dependency(name=name, current_version=ver, ecosystem="java"))
        return deps

    def _parse_build_gradle(self, path: Path) -> List[Dependency]:
        deps = []
        content = path.read_text(encoding="utf-8")
        # Match patterns like: implementation 'group:artifact:version'
        # or implementation("group:artifact:version")
        dep_re = re.compile(
            r"(?:implementation|api|compileOnly|runtimeOnly|testImplementation|testRuntimeOnly)"
            r"[\s(]+['\"]([\w.\-]+):([\w.\-]+):([\w.\-]+)['\"]",
            re.MULTILINE,
        )
        for match in dep_re.finditer(content):
            group, artifact, version = match.group(1), match.group(2), match.group(3)
            deps.append(
                Dependency(
                    name=f"{group}:{artifact}",
                    current_version=version,
                    ecosystem="java",
                )
            )
        return deps
