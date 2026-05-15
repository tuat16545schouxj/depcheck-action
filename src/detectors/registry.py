"""Detector registry — discovers and returns the right detector for a repo."""
from pathlib import Path
from typing import Type

from .base import BaseDetector, DetectionResult
from .python_detector import PythonDetector
from .node_detector import NodeDetector

# All available detectors in priority order
_DETECTOR_CLASSES: list[Type[BaseDetector]] = [
    PythonDetector,
    NodeDetector,
]


def get_all_detectors() -> list[BaseDetector]:
    """Return one instance of every registered detector."""
    return [cls() for cls in _DETECTOR_CLASSES]


def detect_all(repo_path: Path) -> list[DetectionResult]:
    """Run every detector against *repo_path* and return non-empty results."""
    results: list[DetectionResult] = []
    for detector in get_all_detectors():
        result = detector.detect(repo_path)
        if result.manifests:  # only include ecosystems that found something
            results.append(result)
    return results


def detect_for_file(file_path: Path) -> list[BaseDetector]:
    """Return detectors that claim to support the given file path."""
    return [
        detector
        for detector in get_all_detectors()
        if detector.supports(file_path)
    ]


def summary(results: list[DetectionResult]) -> dict:
    """Produce a JSON-serialisable summary of all detection results."""
    return {
        "ecosystems_scanned": len(results),
        "total_dependencies": sum(len(r.dependencies) for r in results),
        "outdated_dependencies": sum(
            sum(1 for d in r.dependencies if d.latest_version and d.outdated)
            for r in results
        ),
        "results": [r.to_dict() for r in results],
    }
