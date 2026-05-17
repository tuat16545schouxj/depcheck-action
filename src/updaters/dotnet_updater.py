import re
from pathlib import Path
from typing import List

from src.updaters.base import UpdateResult, UpdateSummary
from src.detectors.base import Dependency


class DotnetUpdater:
    """Updates .NET dependencies in .csproj files."""

    SUPPORTED = {".csproj"}

    def supports(self, filename: str) -> bool:
        return Path(filename).suffix in self.SUPPORTED

    def update(self, filepath: str, deps: List[Dependency]) -> UpdateSummary:
        path = Path(filepath)
        results: List[UpdateResult] = []

        if path.suffix == ".csproj":
            results = self._update_csproj(path, deps)

        succeeded = [r for r in results if r.success]
        failed = [r for r in results if not r.success]
        return UpdateSummary(
            file=filepath,
            ecosystem="dotnet",
            results=results,
            total=len(results),
            updated=len(succeeded),
            skipped=len(failed),
        )

    def _update_csproj(self, path: Path, deps: List[Dependency]) -> List[UpdateResult]:
        try:
            content = path.read_text()
        except OSError as exc:
            return [UpdateResult(name=d.name, success=False, error=str(exc)) for d in deps]

        results: List[UpdateResult] = []
        new_content = content

        for dep in deps:
            if dep.latest is None:
                results.append(UpdateResult(name=dep.name, success=False, error="no latest version"))
                continue

            pattern = re.compile(
                r'(<PackageReference\s+Include="' + re.escape(dep.name) + r'"\s+Version=")([^"]+)(")',
                re.IGNORECASE,
            )
            updated, count = pattern.subn(lambda m: m.group(1) + dep.latest + m.group(3), new_content)

            if count > 0:
                new_content = updated
                results.append(UpdateResult(name=dep.name, success=True,
                                            old_version=dep.current, new_version=dep.latest))
            else:
                results.append(UpdateResult(name=dep.name, success=False,
                                            error=f"{dep.name} not found in {path.name}"))

        if new_content != content:
            path.write_text(new_content)

        return results
