import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List

from .base import BaseDetector, Dependency, DetectionResult


class DotnetDetector(BaseDetector):
    """Detector for .NET / C# projects (*.csproj and packages.lock.json)."""

    SUPPORTED_FILES = {"*.csproj", "packages.lock.json"}

    def supports(self, filename: str) -> bool:
        name = Path(filename).name
        return name.endswith(".csproj") or name == "packages.lock.json"

    def detect(self, filepath: str) -> DetectionResult:
        path = Path(filepath)
        if path.name == "packages.lock.json":
            deps = self._parse_packages_lock(path)
        else:
            deps = self._parse_csproj(path)
        return DetectionResult(ecosystem="dotnet", source_file=filepath, dependencies=deps)

    def _parse_csproj(self, path: Path) -> List[Dependency]:
        deps: List[Dependency] = []
        try:
            tree = ET.parse(path)
            root = tree.getroot()
            for ref in root.iter("PackageReference"):
                name = ref.get("Include") or ref.get("Update")
                version = ref.get("Version") or ""
                if not version:
                    ver_elem = ref.find("Version")
                    version = ver_elem.text.strip() if ver_elem is not None and ver_elem.text else ""
                if name:
                    deps.append(Dependency(name=name, current_version=self._clean(version)))
        except ET.ParseError:
            pass
        return deps

    def _parse_packages_lock(self, path: Path) -> List[Dependency]:
        import json
        deps: List[Dependency] = []
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            for framework_deps in data.get("dependencies", {}).values():
                for pkg_name, meta in framework_deps.items():
                    version = meta.get("resolved", "")
                    deps.append(Dependency(name=pkg_name, current_version=self._clean(version)))
        except (json.JSONDecodeError, AttributeError):
            pass
        return deps

    def _clean(self, version: str) -> str:
        return re.sub(r"[\[\]()]", "", version).split(",")[0].strip()
