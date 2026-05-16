"""Registry that dispatches update requests to the correct ecosystem updater."""
from typing import List, Optional

from .base import BaseUpdater, UpdateResult, UpdateSummary
from .python_updater import PythonUpdater
from .node_updater import NodeUpdater

_UPDATERS: List[BaseUpdater] = [
    PythonUpdater(),
    NodeUpdater(),
]


def get_all_updaters() -> List[BaseUpdater]:
    """Return all registered updater instances."""
    return list(_UPDATERS)


def updater_for_file(file_path: str) -> Optional[BaseUpdater]:
    """Return the first updater that supports the given file, or None."""
    for updater in _UPDATERS:
        if updater.supports(file_path):
            return updater
    return None


def apply_updates(updates: List[dict]) -> UpdateSummary:
    """
    Apply a list of update requests.

    Each request dict must contain:
        file_path, name, old_version, new_version
    """
    summary = UpdateSummary()
    for req in updates:
        file_path = req["file_path"]
        updater = updater_for_file(file_path)
        if updater is None:
            summary.results.append(
                UpdateResult(
                    file_path=file_path,
                    ecosystem="unknown",
                    name=req.get("name", ""),
                    old_version=req.get("old_version", ""),
                    new_version=req.get("new_version", ""),
                    success=False,
                    error="No updater found for this file type",
                )
            )
        else:
            result = updater.update(
                file_path, req["name"], req["old_version"], req["new_version"]
            )
            summary.results.append(result)
    return summary
