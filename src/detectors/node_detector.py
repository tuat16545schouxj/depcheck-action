"""Node.js/npm dependency detector."""
import json
from pathlib import Path
from typing import Optional

from .base import Dependency, DetectionResult, BaseDetector


class NodeDetector(BaseDetector):
    """Detects outdated Node.js dependencies via package.json."""

    SUPPORTED_MANIFESTS = ("package.json",)

    def supports(self, path: Path) -> bool:
        return path.name in self.SUPPORTED_MANIFESTS

    def detect(self, repo_path: Path) -> DetectionResult:
        dependencies: list[Dependency] = []
        manifests_found: list[str] = []

        for manifest_name in self.SUPPORTED_MANIFESTS:
            manifest_path = repo_path / manifest_name
            if manifest_path.exists():
                manifests_found.append(str(manifest_path))
                deps = self._parse_package_json(manifest_path)
                dependencies.extend(deps)

        return DetectionResult(
            ecosystem="node",
            manifests=manifests_found,
            dependencies=dependencies,
        )

    def _parse_package_json(self, path: Path) -> list[Dependency]:
        """Parse dependencies and devDependencies from package.json."""
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []

        deps: list[Dependency] = []
        for section in ("dependencies", "devDependencies", "peerDependencies"):
            for name, version_spec in data.get(section, {}).items():
                current = self._clean_version(version_spec)
                deps.append(
                    Dependency(
                        name=name,
                        current_version=current,
                        latest_version=None,
                        ecosystem="node",
                        manifest=str(path),
                    )
                )
        return deps

    @staticmethod
    def _clean_version(version_spec: str) -> Optional[str]:
        """Strip semver range prefixes to get a plain version string."""
        if not version_spec or version_spec in ("*", "latest"):
            return None
        return version_spec.lstrip("^~>= ").split(" ")[0] or None
