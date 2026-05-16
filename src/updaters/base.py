"""Base classes and types for dependency updaters."""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class UpdateResult:
    """Result of attempting to update a dependency in a manifest file."""
    file_path: str
    ecosystem: str
    name: str
    old_version: str
    new_version: str
    success: bool
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "file_path": self.file_path,
            "ecosystem": self.ecosystem,
            "name": self.name,
            "old_version": self.old_version,
            "new_version": self.new_version,
            "success": self.success,
            "error": self.error,
        }


@dataclass
class UpdateSummary:
    """Aggregated results from an update run."""
    results: list = field(default_factory=list)

    @property
    def succeeded(self) -> list:
        return [r for r in self.results if r.success]

    @property
    def failed(self) -> list:
        return [r for r in self.results if not r.success]

    def to_dict(self) -> dict:
        return {
            "total": len(self.results),
            "succeeded": len(self.succeeded),
            "failed": len(self.failed),
            "results": [r.to_dict() for r in self.results],
        }


class BaseUpdater:
    """Abstract base class for ecosystem-specific updaters."""

    ecosystem: str = "unknown"

    def supports(self, file_path: str) -> bool:
        raise NotImplementedError

    def update(self, file_path: str, name: str, old_version: str, new_version: str) -> UpdateResult:
        raise NotImplementedError
