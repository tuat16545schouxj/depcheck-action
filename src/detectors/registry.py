from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from .base import BaseDetector, DetectionResult
from .node_detector import NodeDetector
from .python_detector import PythonDetector
from .ruby_detector import RubyDetector


_DETECTORS: List[BaseDetector] = [
    PythonDetector(),
    NodeDetector(),
    RubyDetector(),
]


def get_all_detectors() -> List[BaseDetector]:
    """Return every registered detector instance."""
    return list(_DETECTORS)


def detect_for_file(filepath: str) -> Optional[DetectionResult]:
    """Run the first matching detector against *filepath*."""
    filename = Path(filepath).name
    for detector in _DETECTORS:
        if detector.supports(filename):
            return detector.detect(filepath)
    return None


def detect_all(filepaths: List[str]) -> List[DetectionResult]:
    """Run appropriate detectors for each file path in *filepaths*."""
    results: List[DetectionResult] = []
    for fp in filepaths:
        result = detect_for_file(fp)
        if result is not None:
            results.append(result)
    return results


def summary(results: List[DetectionResult]) -> str:
    """Return a human-readable summary of all detection results."""
    if not results:
        return "No supported manifest files detected."
    lines = ["Dependency Audit Summary", "=" * 40]
    total_deps = 0
    total_outdated = 0
    for r in results:
        lines.append(r.summary())
        for dep in r.outdated:
            lines.append(
                f"  - {dep.name}: {dep.current_version} -> {dep.latest_version}"
            )
        total_deps += len(r.dependencies)
        total_outdated += len(r.outdated)
    lines.append("=" * 40)
    lines.append(f"Total: {total_outdated} outdated out of {total_deps} dependencies")
    return "\n".join(lines)
