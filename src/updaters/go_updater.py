import re
import subprocess
from pathlib import Path
from typing import List

from src.detectors.base import Dependency
from src.updaters.base import UpdateResult, UpdateSummary


class GoUpdater:
    """Updater for Go modules (go.mod)."""

    SUPPORTED = {"go.mod"}

    def supports(self, filename: str) -> bool:
        return Path(filename).name in self.SUPPORTED

    def update(self, filepath: str, dependencies: List[Dependency]) -> UpdateSummary:
        results: List[UpdateResult] = []
        path = Path(filepath)

        if not path.exists():
            return UpdateSummary(results)

        content = path.read_text()

        for dep in dependencies:
            if not dep.latest:
                results.append(UpdateResult(
                    dependency=dep,
                    success=False,
                    error="No latest version available",
                ))
                continue

            updated, new_content = self._replace(content, dep)
            if updated:
                content = new_content
                results.append(UpdateResult(dependency=dep, success=True))
            else:
                results.append(UpdateResult(
                    dependency=dep,
                    success=False,
                    error=f"Could not find {dep.name} in {filepath}",
                ))

        if any(r.success for r in results):
            path.write_text(content)
            self._run_go_mod_tidy(path.parent)

        return UpdateSummary(results)

    def _replace(self, content: str, dep: Dependency):
        """
        Replace the version of a require directive in go.mod.
        Handles lines like:  require github.com/foo/bar v1.2.3
        and block require entries:  \tgithub.com/foo/bar v1.2.3
        """
        escaped = re.escape(dep.name)
        pattern = re.compile(
            r'(?m)^(\s*' + escaped + r'\s+)v[\w.+-]+'
        )
        new_content, count = pattern.subn(
            lambda m: m.group(1) + dep.latest, content
        )
        return count > 0, new_content

    def _run_go_mod_tidy(self, directory: Path) -> None:
        """Run `go mod tidy` to keep go.sum in sync (best-effort)."""
        try:
            subprocess.run(
                ["go", "mod", "tidy"],
                cwd=str(directory),
                capture_output=True,
                timeout=60,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
