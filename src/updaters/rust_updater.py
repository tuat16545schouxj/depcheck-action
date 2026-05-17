import re
import subprocess
from pathlib import Path
from typing import List

from src.updaters.base import UpdateResult, UpdateSummary
from src.detectors.base import Dependency


class RustUpdater:
    """Updater for Rust Cargo.toml dependency files."""

    SUPPORTED = {"Cargo.toml"}

    def supports(self, filename: str) -> bool:
        return Path(filename).name in self.SUPPORTED

    def update(self, filepath: str, dependencies: List[Dependency]) -> UpdateSummary:
        path = Path(filepath)
        if not path.exists():
            return UpdateSummary(results=[])

        original = path.read_text()
        content = original
        results: List[UpdateResult] = []

        for dep in dependencies:
            if not dep.outdated or dep.latest is None:
                continue
            updated, content = self._replace(content, dep)
            results.append(UpdateResult(
                dependency=dep,
                filepath=filepath,
                success=updated,
                error=None if updated else f"Could not find {dep.name} in {filepath}",
            ))

        if content != original:
            path.write_text(content)
            self._run_cargo_update(path.parent)

        return UpdateSummary(results=results)

    def _replace(self, content: str, dep: Dependency):
        """
        Replace version strings in Cargo.toml for a given dependency.
        Handles both `name = "version"` and `name = { version = "..." }` forms.
        """
        patterns = [
            # dep = "1.2.3"  or  dep = "^1.2.3"
            (r'(?m)^(\s*' + re.escape(dep.name) + r'\s*=\s*")[^"]*(")'),
            # dep = { version = "1.2.3", ... }
            (r'(?m)(\b' + re.escape(dep.name) + r'\s*=\s*\{[^}]*version\s*=\s*")[^"]*(")'),
        ]
        new_content = content
        replaced = False
        for pattern in patterns:
            result, count = re.subn(pattern, rf'\g<1>{dep.latest}\2', new_content)
            if count > 0:
                new_content = result
                replaced = True
                break
        return replaced, new_content

    def _run_cargo_update(self, cwd: Path):
        try:
            subprocess.run(
                ["cargo", "update"],
                cwd=str(cwd),
                capture_output=True,
                timeout=60,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
