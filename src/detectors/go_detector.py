import re
import json
from pathlib import Path
from typing import List
from .base import BaseDetector, Dependency, DetectionResult


class GoDetector(BaseDetector):
    """Detector for Go modules (go.mod / go.sum)."""

    SUPPORTED_FILES = {"go.mod", "go.sum"}

    def supports(self, filename: str) -> bool:
        return Path(filename).name in self.SUPPORTED_FILES

    def detect(self, filepath: str) -> DetectionResult:
        path = Path(filepath)
        if path.name == "go.mod":
            deps = self._parse_go_mod(path)
        elif path.name == "go.sum":
            deps = self._parse_go_sum(path)
        else:
            deps = []
        return DetectionResult(ecosystem="go", source_file=filepath, dependencies=deps)

    def _parse_go_mod(self, path: Path) -> List[Dependency]:
        deps: List[Dependency] = []
        in_require_block = False
        content = path.read_text(encoding="utf-8")
        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith("require ("):
                in_require_block = True
                continue
            if in_require_block and stripped == ")":
                in_require_block = False
                continue
            if in_require_block or stripped.startswith("require "):
                entry = stripped.removeprefix("require ").strip()
                entry = re.sub(r"//.*$", "", entry).strip()
                parts = entry.split()
                if len(parts) >= 2:
                    name, version = parts[0], self._clean_version(parts[1])
                    deps.append(Dependency(name=name, current_version=version))
        return deps

    def _parse_go_sum(self, path: Path) -> List[Dependency]:
        """Parse go.sum for a unique set of module/version pairs."""
        seen: dict = {}
        for line in path.read_text(encoding="utf-8").splitlines():
            parts = line.split()
            if len(parts) < 2:
                continue
            module = parts[0]
            version = self._clean_version(parts[1].split("/")[0])
            if module not in seen:
                seen[module] = version
                yield_dep = Dependency(name=module, current_version=version)
                seen[module] = yield_dep
        return list(seen.values())

    def _clean_version(self, version: str) -> str:
        """Strip leading 'v' from semver strings."""
        return version.lstrip("v")
