from typing import List, Dict

from .base import DetectionResult
from .python_detector import PythonDetector
from .node_detector import NodeDetector
from .ruby_detector import RubyDetector
from .go_detector import GoDetector
from .rust_detector import RustDetector
from .java_detector import JavaDetector
from .php_detector import PhpDetector
from .dotnet_detector import DotnetDetector

_DETECTORS = [
    PythonDetector(),
    NodeDetector(),
    RubyDetector(),
    GoDetector(),
    RustDetector(),
    JavaDetector(),
    PhpDetector(),
    DotnetDetector(),
]


def get_all_detectors():
    """Return all registered detector instances."""
    return list(_DETECTORS)


def detect_for_file(filepath: str) -> List[DetectionResult]:
    """Run every detector that claims to support *filepath* and return results."""
    results = []
    for detector in _DETECTORS:
        if detector.supports(filepath):
            results.append(detector.detect(filepath))
    return results


def detect_all(filepaths: List[str]) -> List[DetectionResult]:
    """Run detection across a list of file paths, skipping unsupported ones."""
    results = []
    for fp in filepaths:
        results.extend(detect_for_file(fp))
    return results


def summary(results: List[DetectionResult]) -> Dict[str, int]:
    """Return a dict mapping ecosystem -> total outdated dependency count."""
    counts: Dict[str, int] = {}
    for result in results:
        outdated = sum(1 for d in result.dependencies if d.outdated())
        counts[result.ecosystem] = counts.get(result.ecosystem, 0) + outdated
    return counts
