from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Dependency:
    name: str
    current_version: str
    latest_version: Optional[str] = None
    ecosystem: Optional[str] = None

    def __post_init__(self):
        self.current_version = self.current_version.lstrip("^~>= ")

    @property
    def outdated(self) -> bool:
        return (
            self.latest_version is not None
            and self.latest_version != self.current_version
        )

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "current_version": self.current_version,
            "latest_version": self.latest_version,
            "ecosystem": self.ecosystem,
            "outdated": self.outdated,
        }


@dataclass
class DetectionResult:
    ecosystem: str
    manifest_path: str
    dependencies: List[Dependency] = field(default_factory=list)
    outdated: List[Dependency] = field(default_factory=list)

    def summary(self) -> str:
        total = len(self.dependencies)
        out = len(self.outdated)
        return (
            f"[{self.ecosystem}] {self.manifest_path}: "
            f"{out} outdated out of {total} dependencies"
        )

    def to_dict(self) -> dict:
        return {
            "ecosystem": self.ecosystem,
            "manifest_path": self.manifest_path,
            "dependencies": [d.to_dict() for d in self.dependencies],
            "outdated": [d.to_dict() for d in self.outdated],
        }


class BaseDetector(ABC):
    """Abstract base class for all ecosystem detectors."""

    name: str = "base"

    @abstractmethod
    def supports(self, filename: str) -> bool:
        """Return True if this detector can handle the given filename."""

    @abstractmethod
    def detect(self, filepath: str) -> DetectionResult:
        """Analyse the manifest at *filepath* and return a DetectionResult."""
