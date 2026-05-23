"""HTML reporter: renders detection results as a self-contained HTML page."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import List

from src.detectors.base import DetectionResult


class HtmlReporter:
    """Renders a list of DetectionResult objects as a standalone HTML report."""

    TITLE = "depcheck-action — Dependency Audit Report"

    def render(self, results: List[DetectionResult]) -> str:
        total = sum(r.total for r in results)
        outdated = sum(r.outdated_count for r in results)
        generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

        rows = "".join(self._render_result(r) for r in results)
        badge_class = "badge-ok" if outdated == 0 else "badge-warn"

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{self.TITLE}</title>
<style>
  body {{ font-family: sans-serif; margin: 2rem; color: #222; }}
  h1 {{ font-size: 1.4rem; }}
  .badge {{ display:inline-block; padding:.2rem .6rem; border-radius:4px; font-weight:bold; }}
  .badge-ok {{ background:#d4edda; color:#155724; }}
  .badge-warn {{ background:#fff3cd; color:#856404; }}
  table {{ border-collapse: collapse; width: 100%; margin-top: 1rem; }}
  th, td {{ border: 1px solid #dee2e6; padding: .4rem .7rem; text-align: left; }}
  th {{ background: #f8f9fa; }}
  .outdated {{ color: #c0392b; font-weight: bold; }}
  .footer {{ margin-top:2rem; font-size:.8rem; color:#888; }}
</style>
</head>
<body>
<h1>&#128269; {self.TITLE}</h1>
<p>Total dependencies: <strong>{total}</strong> &nbsp;
   Outdated: <span class="badge {badge_class}">{outdated}</span></p>
{rows}
<p class="footer">Generated: {generated}</p>
</body>
</html>"""

    def _render_result(self, result: DetectionResult) -> str:
        if not result.dependencies:
            return ""
        rows = ""
        for dep in result.dependencies:
            cls = ' class="outdated"' if dep.outdated else ""
            latest = dep.latest_version or "—"
            rows += (
                f"<tr><td>{dep.name}</td>"
                f"<td{cls}>{dep.current_version}</td>"
                f"<td>{latest}</td></tr>\n"
            )
        return (
            f"<h2>{result.ecosystem} "
            f"<small style='font-size:.8rem;color:#555'>({result.manifest_path})</small></h2>\n"
            f"<table><thead><tr><th>Package</th><th>Current</th><th>Latest</th></tr></thead>\n"
            f"<tbody>\n{rows}</tbody></table>\n"
        )
