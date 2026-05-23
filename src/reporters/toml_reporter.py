"""TOML reporter – serialises detection results to TOML format."""
from __future__ import annotations

import datetime
from typing import List

from src.detectors.base import DetectionResult

try:
    import tomllib  # Python 3.11+
except ImportError:  # pragma: no cover
    import tomli as tomllib  # type: ignore

try:
    import tomli_w
except ImportError:  # pragma: no cover
    tomli_w = None  # type: ignore


class TomlReporter:
    """Render a list of DetectionResults as a TOML document."""

    name = "toml"

    def render(self, results: List[DetectionResult]) -> str:
        doc: dict = {
            "meta": {
                "generated_at": datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z",
                "total_dependencies": sum(r.total for r in results),
                "total_outdated": sum(r.outdated_count for r in results),
            },
            "ecosystems": [self._render_result(r) for r in results],
        }
        if tomli_w is not None:
            return tomli_w.dumps(doc)
        # Fallback: hand-roll minimal TOML so the reporter is usable without tomli_w
        return self._manual_dumps(doc)

    # ------------------------------------------------------------------
    def _render_result(self, result: DetectionResult) -> dict:
        return {
            "ecosystem": result.ecosystem,
            "manifest": result.manifest,
            "total": result.total,
            "outdated": result.outdated_count,
            "dependencies": [
                {
                    "name": d.name,
                    "current": d.current_version,
                    "latest": d.latest_version or "",
                    "outdated": d.outdated,
                }
                for d in result.dependencies
            ],
        }

    # ------------------------------------------------------------------
    @staticmethod
    def _manual_dumps(doc: dict) -> str:  # pragma: no cover
        """Very small TOML emitter used when tomli_w is unavailable."""
        lines: list[str] = []

        def _scalar(v):
            if isinstance(v, bool):
                return "true" if v else "false"
            if isinstance(v, int):
                return str(v)
            return f'"{v}"'

        meta = doc["meta"]
        lines.append("[meta]")
        for k, v in meta.items():
            lines.append(f"{k} = {_scalar(v)}")
        lines.append("")
        for eco in doc["ecosystems"]:
            lines.append("[[ecosystems]]")
            for k, v in eco.items():
                if k == "dependencies":
                    continue
                lines.append(f"{k} = {_scalar(v)}")
            for dep in eco.get("dependencies", []):
                lines.append("[[ecosystems.dependencies]]")
                for dk, dv in dep.items():
                    lines.append(f"  {dk} = {_scalar(dv)}")
            lines.append("")
        return "\n".join(lines)
