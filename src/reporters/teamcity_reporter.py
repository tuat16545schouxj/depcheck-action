"""TeamCity service messages reporter.

Emits TeamCity-compatible service messages so that depcheck results
are surfaced natively inside a TeamCity build log.

See: https://www.jetbrains.com/help/teamcity/service-messages.html
"""

from __future__ import annotations

from typing import List

from src.detectors.base import DetectionResult


class TeamCityReporter:
    """Render detection results as TeamCity service messages."""

    # Severity used for outdated dependencies
    _STATUS = "WARNING"

    def render(self, results: List[DetectionResult]) -> str:
        lines: List[str] = []

        lines.append(self._msg("testSuiteStarted", name="depcheck"))

        for result in results:
            suite = result.ecosystem
            lines.append(self._msg("testSuiteStarted", name=suite))

            for dep in result.dependencies:
                test_name = f"{suite}:{dep.name}"
                lines.append(self._msg("testStarted", name=test_name))

                if dep.outdated:
                    detail = (
                        f"{dep.name} is outdated: "
                        f"current={dep.current_version}, "
                        f"latest={dep.latest_version}"
                    )
                    lines.append(
                        self._msg(
                            "testFailed",
                            name=test_name,
                            message=f"Outdated dependency: {dep.name}",
                            details=detail,
                        )
                    )

                lines.append(self._msg("testFinished", name=test_name))

            lines.append(self._msg("testSuiteFinished", name=suite))

        lines.append(self._msg("testSuiteFinished", name="depcheck"))

        total = sum(len(r.dependencies) for r in results)
        outdated = sum(
            sum(1 for d in r.dependencies if d.outdated) for r in results
        )
        lines.append(
            self._msg(
                "buildStatisticValue",
                key="depcheck.total",
                value=str(total),
            )
        )
        lines.append(
            self._msg(
                "buildStatisticValue",
                key="depcheck.outdated",
                value=str(outdated),
            )
        )

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _escape(value: str) -> str:
        """Escape special characters per TeamCity spec."""
        return (
            value
            .replace("|", "||")
            .replace("'", "|'")
            .replace("[", "|[")
            .replace("]", "|]")
            .replace("\n", "|n")
            .replace("\r", "|r")
        )

    def _msg(self, name: str, **kwargs: str) -> str:
        attrs = " ".join(
            f"{k}='{self._escape(v)}'" for k, v in kwargs.items()
        )
        return f"##teamcity[{name} {attrs}]" if attrs else f"##teamcity[{name}]"
