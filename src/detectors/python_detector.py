"""Detector for Python dependencies via requirements.txt and pyproject.toml."""

import os
import re
import urllib.request
import json
from typing import Optional

from .base import BaseDetector, Dependency, DetectionResult


PYPI_API = "https://pypi.org/pypi/{package}/json"


class PythonDetector(BaseDetector):
    ecosystem = "python"
    manifest_files = ["requirements.txt", "pyproject.toml"]

    def detect(self, repo_path: str) -> list[DetectionResult]:
        results = []
        for root, _, files in os.walk(repo_path):
            for filename in files:
                if not self.supports(filename):
                    continue
                filepath = os.path.join(root, filename)
                rel_path = os.path.relpath(filepath, repo_path)
                deps, errors = self._parse_manifest(filepath, filename)
                resolved = [self.resolve_latest(d) for d in deps]
                results.append(
                    DetectionResult(
                        ecosystem=self.ecosystem,
                        manifest_file=rel_path,
                        dependencies=resolved,
                        errors=errors,
                    )
                )
        return results

    def _parse_manifest(self, filepath: str, filename: str) -> tuple[list[Dependency], list[str]]:
        deps, errors = [], []
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
        except OSError as e:
            errors.append(f"Cannot read {filepath}: {e}")
            return deps, errors

        if filename == "requirements.txt":
            deps = self._parse_requirements(content, filepath)
        elif filename == "pyproject.toml":
            deps = self._parse_pyproject(content, filepath)
        return deps, errors

    def _parse_requirements(self, content: str, source: str) -> list[Dependency]:
        deps = []
        pattern = re.compile(r"^([A-Za-z0-9_\-\.]+)==([^\s]+)", re.MULTILINE)
        for match in pattern.finditer(content):
            deps.append(
                Dependency(
                    name=match.group(1),
                    current_version=match.group(2),
                    ecosystem=self.ecosystem,
                    manifest_file=source,
                )
            )
        return deps

    def _parse_pyproject(self, content: str, source: str) -> list[Dependency]:
        deps = []
        pattern = re.compile(r'"([A-Za-z0-9_\-\.]+)>=([^"\s,]+)', re.MULTILINE)
        for match in pattern.finditer(content):
            deps.append(
                Dependency(
                    name=match.group(1),
                    current_version=match.group(2),
                    ecosystem=self.ecosystem,
                    manifest_file=source,
                )
            )
        return deps

    def resolve_latest(self, dependency: Dependency) -> Dependency:
        latest = self._fetch_latest_pypi(dependency.name)
        if latest:
            dependency.latest_version = latest
            dependency.__post_init__()
        return dependency

    def _fetch_latest_pypi(self, package: str) -> Optional[str]:
        try:
            url = PYPI_API.format(package=package)
            with urllib.request.urlopen(url, timeout=5) as resp:
                data = json.loads(resp.read())
                return data["info"]["version"]
        except Exception:
            return None
