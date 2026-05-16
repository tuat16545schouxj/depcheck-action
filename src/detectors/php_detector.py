import json
import re
from pathlib import Path
from typing import List

from .base import BaseDetector, Dependency, DetectionResult


class PhpDetector(BaseDetector):
    """Detector for PHP projects using Composer."""

    SUPPORTED_FILES = {"composer.json", "composer.lock"}

    def supports(self, filepath: Path) -> bool:
        return filepath.name in self.SUPPORTED_FILES

    def detect(self, filepath: Path) -> DetectionResult:
        if filepath.name == "composer.json":
            deps = self._parse_composer_json(filepath)
        elif filepath.name == "composer.lock":
            deps = self._parse_composer_lock(filepath)
        else:
            deps = []
        return DetectionResult(ecosystem="php", source=str(filepath), dependencies=deps)

    def _parse_composer_json(self, filepath: Path) -> List[Dependency]:
        deps = []
        try:
            data = json.loads(filepath.read_text())
        except (json.JSONDecodeError, OSError):
            return deps

        for section in ("require", "require-dev"):
            for name, version_constraint in data.get(section, {}).items():
                if name == "php" or name.startswith("ext-"):
                    continue
                cleaned = self._clean_constraint(version_constraint)
                deps.append(
                    Dependency(
                        name=name,
                        current_version=cleaned,
                        ecosystem="php",
                        dev=(section == "require-dev"),
                    )
                )
        return deps

    def _parse_composer_lock(self, filepath: Path) -> List[Dependency]:
        deps = []
        try:
            data = json.loads(filepath.read_text())
        except (json.JSONDecodeError, OSError):
            return deps

        for section, is_dev in (("packages", False), ("packages-dev", True)):
            for pkg in data.get(section, []):
                name = pkg.get("name", "")
                version = pkg.get("version", "").lstrip("v")
                if name:
                    deps.append(
                        Dependency(
                            name=name,
                            current_version=version,
                            ecosystem="php",
                            dev=is_dev,
                        )
                    )
        return deps

    def _clean_constraint(self, constraint: str) -> str:
        """Strip leading version operators to get a bare version string."""
        cleaned = re.sub(r"^[^\d]*", "", constraint.strip())
        return cleaned or constraint.strip()
