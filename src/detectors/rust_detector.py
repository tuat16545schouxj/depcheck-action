import re
import toml
from pathlib import Path
from typing import List
from .base import BaseDetector, Dependency, DetectionResult


class RustDetector(BaseDetector):
    """Detector for Rust projects using Cargo.toml and Cargo.lock."""

    MANIFEST_FILES = {"Cargo.toml", "Cargo.lock"}

    def supports(self, filename: str) -> bool:
        return Path(filename).name in self.MANIFEST_FILES

    def detect(self, filepath: str) -> DetectionResult:
        name = Path(filepath).name
        if name == "Cargo.toml":
            deps = self._parse_cargo_toml(filepath)
        elif name == "Cargo.lock":
            deps = self._parse_cargo_lock(filepath)
        else:
            deps = []
        return DetectionResult(ecosystem="rust", source_file=filepath, dependencies=deps)

    def _parse_cargo_toml(self, filepath: str) -> List[Dependency]:
        deps: List[Dependency] = []
        try:
            data = toml.load(filepath)
        except Exception:
            return deps

        sections = [
            data.get("dependencies", {}),
            data.get("dev-dependencies", {}),
            data.get("build-dependencies", {}),
        ]
        for section in sections:
            for pkg, spec in section.items():
                if isinstance(spec, str):
                    version = self._clean_version(spec)
                elif isinstance(spec, dict):
                    version = self._clean_version(spec.get("version", ""))
                else:
                    version = None
                deps.append(Dependency(name=pkg, current_version=version))
        return deps

    def _parse_cargo_lock(self, filepath: str) -> List[Dependency]:
        deps: List[Dependency] = []
        try:
            data = toml.load(filepath)
        except Exception:
            return deps

        for package in data.get("package", []):
            name = package.get("name")
            version = package.get("version")
            if name:
                deps.append(Dependency(name=name, current_version=version))
        return deps

    def _clean_version(self, version: str) -> str:
        """Strip leading comparison operators from version strings."""
        return re.sub(r'^[^\d]*', '', version).strip() or None
