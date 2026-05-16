from typing import List, Dict
from .base import DetectionResult
from .python_detector import PythonDetector
from .node_detector import NodeDetector
from .ruby_detector import RubyDetector
from .go_detector import GoDetector
from .rust_detector import RustDetector


_DETECTORS = [
    PythonDetector(),
    NodeDetector(),
    RubyDetector(),
    GoDetector(),
    RustDetector(),
]


def get_all_detectors():
    """Return all registered detector instances."""
    return list(_DETECTORS)


def detect_for_file(filepath: str) -> List[DetectionResult]:
    """Run all detectors that support the given file and return results."""
    results = []
    for detector in _DETECTORS:
        if detector.supports(filepath):
            result = detector.detect(filepath)
            results.append(result)
    return results


def detect_all(filepaths: List[str]) -> List[DetectionResult]:
    """Run detection across a list of file paths."""
    results = []
    for filepath in filepaths:
        results.extend(detect_for_file(filepath))
    return results


def summary(results: List[DetectionResult]) -> Dict:
    """Produce a summary dict from a list of DetectionResults."""
    total_deps = 0
    outdated_deps = 0
    by_ecosystem: Dict[str, Dict] = {}

    for result in results:
        eco = result.ecosystem
        if eco not in by_ecosystem:
            by_ecosystem[eco] = {"total": 0, "outdated": 0, "files": []}
        by_ecosystem[eco]["files"].append(result.source_file)
        for dep in result.dependencies:
            total_deps += 1
            by_ecosystem[eco]["total"] += 1
            if dep.outdated:
                outdated_deps += 1
                by_ecosystem[eco]["outdated"] += 1

    return {
        "total_dependencies": total_deps,
        "outdated_dependencies": outdated_deps,
        "by_ecosystem": by_ecosystem,
    }
