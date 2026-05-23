"""Dashboard reporter: renders a self-contained HTML dashboard with charts."""
from __future__ import annotations

import json
from typing import List

from src.detectors.registry import DetectionResult


class DashboardReporter:
    """Produces a single-file HTML dashboard with a dependency health overview."""

    TITLE = "Dependency Health Dashboard"

    def render(self, results: List[DetectionResult]) -> str:
        ecosystems = []
        total_deps = 0
        total_outdated = 0

        for r in results:
            outdated = [d for d in r.dependencies if d.outdated]
            ecosystems.append({
                "name": r.ecosystem,
                "total": len(r.dependencies),
                "outdated": len(outdated),
            })
            total_deps += len(r.dependencies)
            total_outdated += len(outdated)

        chart_data = json.dumps(ecosystems)
        up_to_date = total_deps - total_outdated
        pct = round((up_to_date / total_deps * 100) if total_deps else 100, 1)

        rows = "".join(self._render_row(e) for e in ecosystems)
        return self._template(chart_data, total_deps, total_outdated, pct, rows)

    def _render_row(self, e: dict) -> str:
        status = "✅" if e["outdated"] == 0 else "⚠️"
        return (
            f"<tr><td>{status}</td><td>{e['name']}</td>"
            f"<td>{e['total']}</td><td>{e['outdated']}</td></tr>\n"
        )

    def _template(self, chart_data: str, total: int, outdated: int, pct: float, rows: str) -> str:
        return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>{self.TITLE}</title>
<style>
  body{{font-family:sans-serif;margin:2rem;background:#f8f9fa;}}
  h1{{color:#333;}}table{{border-collapse:collapse;width:100%;}}
  th,td{{border:1px solid #ddd;padding:.5rem;text-align:left;}}
  th{{background:#4a90d9;color:#fff;}}
  .score{{font-size:3rem;font-weight:bold;color:{self._score_color(pct)};}}
</style></head>
<body>
<h1>{self.TITLE}</h1>
<p>Total dependencies: <strong>{total}</strong> &nbsp;|&nbsp; Outdated: <strong>{outdated}</strong></p>
<p class="score">{pct}% up-to-date</p>
<table><thead><tr><th></th><th>Ecosystem</th><th>Total</th><th>Outdated</th></tr></thead>
<tbody>{rows}</tbody></table>
<script>
const data = {chart_data};
console.log('depcheck dashboard data', data);
</script>
</body></html>"""

    @staticmethod
    def _score_color(pct: float) -> str:
        if pct >= 90:
            return "#2ecc71"
        if pct >= 70:
            return "#f39c12"
        return "#e74c3c"
