"""Updater for Python dependency manifests (requirements.txt, pyproject.toml)."""
import re
from pathlib import Path

from .base import BaseUpdater, UpdateResult


class PythonUpdater(BaseUpdater):
    ecosystem = "python"

    def supports(self, file_path: str) -> bool:
        name = Path(file_path).name
        return name in ("requirements.txt", "pyproject.toml")

    def update(self, file_path: str, name: str, old_version: str, new_version: str) -> UpdateResult:
        path = Path(file_path)
        try:
            content = path.read_text()
            updated = self._replace(content, path.name, name, old_version, new_version)
            if updated == content:
                return UpdateResult(file_path, self.ecosystem, name, old_version, new_version,
                                    False, "Pattern not found in file")
            path.write_text(updated)
            return UpdateResult(file_path, self.ecosystem, name, old_version, new_version, True)
        except Exception as exc:
            return UpdateResult(file_path, self.ecosystem, name, old_version, new_version,
                                False, str(exc))

    def _replace(self, content: str, filename: str, name: str, old: str, new: str) -> str:
        if filename == "requirements.txt":
            pattern = re.compile(
                r'(?i)(^' + re.escape(name) + r'\s*[=~!<>]+\s*)' + re.escape(old),
                re.MULTILINE,
            )
            return pattern.sub(lambda m: m.group(1) + new, content)
        if filename == "pyproject.toml":
            pattern = re.compile(
                r'(?i)("' + re.escape(name) + r'"\s*=\s*"[^"]*?)' + re.escape(old),
            )
            return pattern.sub(lambda m: m.group(1) + new, content)
        return content
