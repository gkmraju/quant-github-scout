from __future__ import annotations

import json
from pathlib import Path


class SeenRepoStore:
    def __init__(self, path: Path) -> None:
        self._path = path

    def load(self) -> set[str]:
        if not self._path.exists():
            return set()
        data = json.loads(self._path.read_text(encoding="utf-8"))
        return set(data.get("repos", []))

    def save(self, repo_names: set[str]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"repos": sorted(repo_names)}
        self._path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
