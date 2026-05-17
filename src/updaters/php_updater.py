import json
import re
from pathlib import Path
from typing import List

from src.updaters.base import UpdateResult, UpdateSummary
from src.detectors.base import Dependency


class PhpUpdater:
    """Updates PHP dependencies in composer.json."""

    SUPPORTED = {"composer.json"}

    def supports(self, filename: str) -> bool:
        return Path(filename).name in self.SUPPORTED

    def update(self, filepath: str, deps: List[Dependency]) -> UpdateSummary:
        path = Path(filepath)
        results: List[UpdateResult] = []

        if path.name == "composer.json":
            results = self._update_composer_json(path, deps)

        succeeded = [r for r in results if r.success]
        failed = [r for r in results if not r.success]
        return UpdateSummary(
            file=filepath,
            ecosystem="php",
            results=results,
            total=len(results),
            updated=len(succeeded),
            skipped=len(failed),
        )

    def _update_composer_json(self, path: Path, deps: List[Dependency]) -> List[UpdateResult]:
        try:
            data = json.loads(path.read_text())
        except (json.JSONDecodeError, OSError) as exc:
            return [UpdateResult(name=d.name, success=False, error=str(exc)) for d in deps]

        results: List[UpdateResult] = []
        changed = False

        for dep in deps:
            if dep.latest is None:
                results.append(UpdateResult(name=dep.name, success=False, error="no latest version"))
                continue

            updated = False
            for section in ("require", "require-dev"):
                if section in data and dep.name in data[section]:
                    old = data[section][dep.name]
                    data[section][dep.name] = self._preserve_constraint(old, dep.latest)
                    changed = True
                    updated = True
                    results.append(UpdateResult(name=dep.name, success=True,
                                                old_version=dep.current, new_version=dep.latest))
                    break

            if not updated:
                results.append(UpdateResult(name=dep.name, success=False,
                                            error=f"{dep.name} not found in composer.json"))

        if changed:
            path.write_text(json.dumps(data, indent=4) + "\n")

        return results

    def _preserve_constraint(self, old_constraint: str, new_version: str) -> str:
        """Keep leading constraint characters (^, ~, >=) and replace version number."""
        match = re.match(r'^([^0-9]*)(.*)', old_constraint)
        prefix = match.group(1) if match else ""
        return f"{prefix}{new_version}"
