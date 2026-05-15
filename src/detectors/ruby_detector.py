import re
from pathlib import Path
from typing import List

import requests

from .base import Dependency, DetectionResult, BaseDetector


GEMFILE_LOCK = "Gemfile.lock"
GEMFILE = "Gemfile"
SUPPORTED_FILES = {GEMFILE_LOCK, GEMFILE}


class RubyDetector(BaseDetector):
    """Detects outdated Ruby gems via Gemfile / Gemfile.lock."""

    name = "ruby"

    def supports(self, filename: str) -> bool:
        return Path(filename).name in SUPPORTED_FILES

    def detect(self, filepath: str) -> DetectionResult:
        path = Path(filepath)
        deps = self._parse_manifest(path)
        outdated = []
        for dep in deps:
            latest = self._fetch_latest(dep.name)
            if latest and latest != dep.current_version:
                dep.latest_version = latest
                outdated.append(dep)
        return DetectionResult(
            ecosystem="ruby",
            manifest_path=filepath,
            dependencies=deps,
            outdated=outdated,
        )

    def _parse_manifest(self, path: Path) -> List[Dependency]:
        if path.name == GEMFILE_LOCK:
            return self._parse_gemfile_lock(path)
        return self._parse_gemfile(path)

    def _parse_gemfile_lock(self, path: Path) -> List[Dependency]:
        deps: List[Dependency] = []
        in_gems_section = False
        gem_line = re.compile(r"^    (\S+) \(([^)]+)\)")
        for line in path.read_text().splitlines():
            if line.strip() == "GEM":
                in_gems_section = True
                continue
            if in_gems_section and line.startswith("  ") and not line.startswith("    "):
                # sub-section header like 'remote:' or 'specs:'
                continue
            if in_gems_section and not line.startswith(" "):
                break
            if in_gems_section:
                m = gem_line.match(line)
                if m:
                    deps.append(Dependency(name=m.group(1), current_version=m.group(2)))
        return deps

    def _parse_gemfile(self, path: Path) -> List[Dependency]:
        deps: List[Dependency] = []
        gem_line = re.compile(r"^\s*gem ['\"]([^'\"]+)['\"](?:,\s*['\"]([^'\"]+)['\"])?")
        for line in path.read_text().splitlines():
            m = gem_line.match(line)
            if m:
                version = m.group(2) or "unknown"
                deps.append(Dependency(name=m.group(1), current_version=version))
        return deps

    def _fetch_latest(self, gem_name: str) -> str | None:
        try:
            resp = requests.get(
                f"https://rubygems.org/api/v1/gems/{gem_name}.json", timeout=5
            )
            if resp.status_code == 200:
                return resp.json().get("version")
        except requests.RequestException:
            pass
        return None
