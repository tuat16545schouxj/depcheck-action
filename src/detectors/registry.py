from typing import List, Dict
from .base import DetectionResult
from .python_detector import PythonDetector
from .node_detector import NodeDetector
from .ruby_detector import RubyDetector
from .go_detector import GoDetector


def get_all_detectors():
    """Return an instance of every registered detector."""
    return [
        PythonDetector(),
        NodeDetector(),
        RubyDetector(),
        GoDetector(),
    ]


def detect_for_file(filepath: str) -> List[DetectionResult]:
    """Run all detectors that support the given file and return results."""
    results = []
    for detector in get_all_detectors():
        if detector.supports(filepath):
            results.append(detector.detect(filepath))
    return results


def detect_all(filepaths: List[str]) -> List[DetectionResult]:
    """Run detection across a list of file paths."""
    results = []
    for filepath in filepaths:
        results.extend(detect_for_file(filepath))
    return results


def summary(results: List[DetectionResult]) -> Dict:
    """Produce a summary dict grouped by ecosystem."""
    grouped: Dict[str, Dict] = {}
    for result in results:
        eco = result.ecosystem
        if eco not in grouped:
            grouped[eco] = {"source_files": [], "total": 0, "outdated": 0, "dependencies": []}
        grouped[eco]["source_files"].append(result.source_file)
        grouped[eco]["total"] += len(result.dependencies)
        outdated = [d for d in result.dependencies if d.outdated]
        grouped[eco]["outdated"] += len(outdated)
        grouped[eco]["dependencies"].extend([d.to_dict() for d in result.dependencies])
    return {
        "ecosystems": grouped,
        "total_dependencies": sum(v["total"] for v in grouped.values()),
        "total_outdated": sum(v["outdated"] for v in grouped.values()),
    }
