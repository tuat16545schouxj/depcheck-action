"""Updater for Node.js dependency manifests (package.json)."""
import json
from pathlib import Path

from .base import BaseUpdater, UpdateResult


class NodeUpdater(BaseUpdater):
    ecosystem = "node"

    def supports(self, file_path: str) -> bool:
        return Path(file_path).name == "package.json"

    def update(self, file_path: str, name: str, old_version: str, new_version: str) -> UpdateResult:
        path = Path(file_path)
        try:
            data = json.loads(path.read_text())
        except Exception as exc:
            return UpdateResult(file_path, self.ecosystem, name, old_version, new_version,
                                False, f"JSON parse error: {exc}")

        updated = False
        for section in ("dependencies", "devDependencies", "peerDependencies"):
            deps = data.get(section, {})
            if name in deps:
                prefix = ""
                raw = deps[name]
                if raw and raw[0] in ("^", "~"):
                    prefix = raw[0]
                deps[name] = prefix + new_version
                updated = True

        if not updated:
            return UpdateResult(file_path, self.ecosystem, name, old_version, new_version,
                                False, f"Dependency '{name}' not found in package.json")

        try:
            path.write_text(json.dumps(data, indent=2) + "\n")
            return UpdateResult(file_path, self.ecosystem, name, old_version, new_version, True)
        except Exception as exc:
            return UpdateResult(file_path, self.ecosystem, name, old_version, new_version,
                                False, str(exc))
