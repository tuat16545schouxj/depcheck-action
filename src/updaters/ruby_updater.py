import re
import subprocess
from pathlib import Path
from typing import List

from src.detectors.base import Dependency
from src.updaters.base import UpdateResult, UpdateSummary


class RubyUpdater:
    """Updater for Ruby Gemfile dependencies."""

    SUPPORTED = {"Gemfile"}

    def supports(self, filename: str) -> bool:
        return Path(filename).name in self.SUPPORTED

    def update(self, filepath: str, dependencies: List[Dependency]) -> UpdateSummary:
        results: List[UpdateResult] = []
        path = Path(filepath)

        if not path.exists():
            return UpdateSummary(results)

        original = path.read_text(encoding="utf-8")
        content = original

        for dep in dependencies:
            if not dep.latest:
                results.append(UpdateResult(
                    dependency=dep,
                    success=False,
                    message="No latest version available",
                ))
                continue

            updated, new_content = self._replace(content, dep)
            if updated:
                content = new_content
                results.append(UpdateResult(
                    dependency=dep,
                    success=True,
                    message=f"Updated {dep.name} to {dep.latest}",
                ))
            else:
                results.append(UpdateResult(
                    dependency=dep,
                    success=False,
                    message=f"Could not find pinned version for {dep.name} in Gemfile",
                ))

        if content != original:
            path.write_text(content, encoding="utf-8")

        return UpdateSummary(results)

    def _replace(self, content: str, dep: Dependency):
        """Replace a gem version constraint in Gemfile content."""
        pattern = re.compile(
            r"(gem\s+['\"]" + re.escape(dep.name) + r"['"]\s*,\s*['\"])([^'\"]+)(['\"])",
            re.IGNORECASE,
        )
        match = pattern.search(content)
        if not match:
            return False, content

        new_content = pattern.sub(
            lambda m: m.group(1) + dep.latest + m.group(3),
            content,
            count=1,
        )
        return True, new_content
