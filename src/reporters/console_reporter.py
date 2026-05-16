import sys
from typing import List, TextIO
from src.detectors.base import DetectionResult


class ConsoleReporter:
    """Renders dependency audit results to a console/terminal output."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[31m"
    YELLOW = "\033[33m"
    GREEN = "\033[32m"
    CYAN = "\033[36m"

    def __init__(self, use_color: bool = True, stream: TextIO = None):
        self.use_color = use_color
        self.stream = stream or sys.stdout

    def _c(self, text: str, *codes: str) -> str:
        if not self.use_color:
            return text
        return "".join(codes) + text + self.RESET

    def render(self, results: List[DetectionResult]) -> str:
        lines = []
        lines.append(self._c("=== Dependency Audit Report ===", self.BOLD, self.CYAN))
        lines.append("")

        if not results:
            lines.append(self._c("No dependency files detected.", self.YELLOW))
            output = "\n".join(lines)
            print(output, file=self.stream)
            return output

        total_deps = sum(r.total for r in results)
        total_outdated = sum(len(r.outdated) for r in results)

        for result in results:
            lines.append(self._render_result(result))

        lines.append("")
        lines.append(self._c("Summary", self.BOLD))
        lines.append(f"  Files scanned : {len(results)}")
        lines.append(f"  Total deps    : {total_deps}")

        outdated_color = self.RED if total_outdated > 0 else self.GREEN
        lines.append(
            f"  Outdated      : {self._c(str(total_outdated), outdated_color)}"
        )

        output = "\n".join(lines)
        print(output, file=self.stream)
        return output

    def _render_result(self, result: DetectionResult) -> str:
        lines = []
        header = f"[{result.ecosystem}] {result.manifest_path}"
        lines.append(self._c(header, self.BOLD))

        if not result.dependencies:
            lines.append("  (no dependencies found)")
            return "\n".join(lines)

        for dep in result.dependencies:
            if dep.outdated:
                status = self._c(
                    f"  OUTDATED  {dep.name:<30} {dep.current_version} -> {dep.latest_version}",
                    self.YELLOW,
                )
            else:
                status = self._c(
                    f"  ok        {dep.name:<30} {dep.current_version}",
                    self.GREEN,
                )
            lines.append(status)

        outdated_count = len(result.outdated)
        summary = f"  {outdated_count}/{result.total} outdated"
        lines.append(self._c(summary, self.RED if outdated_count > 0 else self.GREEN))
        return "\n".join(lines)
