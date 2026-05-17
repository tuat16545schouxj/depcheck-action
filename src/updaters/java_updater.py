import re
from pathlib import Path
from typing import List

from src.updaters.base import UpdateResult, UpdateSummary
from src.detectors.base import Dependency


class JavaUpdater:
    """Updater for Java projects (pom.xml and build.gradle)."""

    SUPPORTED = {"pom.xml", "build.gradle"}

    def supports(self, filename: str) -> bool:
        return Path(filename).name in self.SUPPORTED

    def update(self, filepath: str, dependencies: List[Dependency]) -> UpdateSummary:
        path = Path(filepath)
        name = path.name
        results: List[UpdateResult] = []

        if name == "pom.xml":
            results = self._update_pom(path, dependencies)
        elif name == "build.gradle":
            results = self._update_gradle(path, dependencies)

        return UpdateSummary(results=results)

    def _update_pom(self, path: Path, dependencies: List[Dependency]) -> List[UpdateResult]:
        content = path.read_text()
        results: List[UpdateResult] = []

        for dep in dependencies:
            if not dep.latest:
                continue
            # Match <version>OLD</version> preceded by the artifactId block
            pattern = (
                r'(<artifactId>' + re.escape(dep.name) + r'</artifactId>\s*'
                r'<version>)' + re.escape(dep.current_version) + r'(</version>)'
            )
            new_content, count = re.subn(pattern, rf'\g<1>{dep.latest}\2', content, flags=re.DOTALL)
            if count > 0:
                content = new_content
                results.append(UpdateResult(dependency=dep, success=True))
            else:
                results.append(UpdateResult(dependency=dep, success=False, error="Pattern not found in pom.xml"))

        path.write_text(content)
        return results

    def _update_gradle(self, path: Path, dependencies: List[Dependency]) -> List[UpdateResult]:
        content = path.read_text()
        results: List[UpdateResult] = []

        for dep in dependencies:
            if not dep.latest:
                continue
            # Match group:name:version strings in build.gradle
            pattern = r'(["\'])([^"\':]+:' + re.escape(dep.name) + r':)' + re.escape(dep.current_version) + r'\1'
            new_content, count = re.subn(pattern, rf'\1\g<2>{dep.latest}\1', content)
            if count > 0:
                content = new_content
                results.append(UpdateResult(dependency=dep, success=True))
            else:
                results.append(UpdateResult(dependency=dep, success=False, error="Pattern not found in build.gradle"))

        path.write_text(content)
        return results
