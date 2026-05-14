"""Base class for dependency detectors across different ecosystems."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Dependency:
    """Represents a single dependency with version information."""

    name: str
    current_version: str
    latest_version: Optional[str] = None
    ecosystem: str = ""
    manifest_file: str = ""
    is_outdated: bool = False

    def __post_init__(self):
        if self.latest_version and self.current_version != self.latest_version:
            self.is_outdated = True

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "current_version": self.current_version,
            "latest_version": self.latest_version,
            "ecosystem": self.ecosystem,
            "manifest_file": self.manifest_file,
            "is_outdated": self.is_outdated,
        }


@dataclass
class DetectionResult:
    """Result of a dependency detection run for a given ecosystem."""

    ecosystem: str
    manifest_file: str
    dependencies: list[Dependency] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def outdated(self) -> list[Dependency]:
        return [d for d in self.dependencies if d.is_outdated]

    @property
    def total(self) -> int:
        return len(self.dependencies)


class BaseDetector(ABC):
    """Abstract base class for all ecosystem-specific dependency detectors."""

    ecosystem: str = ""
    manifest_files: list[str] = []

    @abstractmethod
    def detect(self, repo_path: str) -> list[DetectionResult]:
        """Scan the repository and return detection results."""
        ...

    @abstractmethod
    def resolve_latest(self, dependency: Dependency) -> Dependency:
        """Fetch the latest available version for a dependency."""
        ...

    def supports(self, filename: str) -> bool:
        """Return True if this detector handles the given manifest filename."""
        return any(filename.endswith(m) for m in self.manifest_files)
