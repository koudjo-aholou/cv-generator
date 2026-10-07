"""JSON-file persistence for the MCP server: base profile + CV version history.

No database — mirrors the repo's existing "100% local" philosophy (the `cv/`
folder for generated PDFs). All writes are atomic (temp file + os.replace).
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional


def _atomic_write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp_path, path)


def _read_json(path: Path) -> Optional[Any]:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


@dataclass
class StorageRepository:
    """Injectable repository for base profile + version JSON storage.

    `base_dir` is the only piece of state. Tests inject `tmp_path`; the
    server wires it from `MCP_STORAGE_DIR` (default `mcp_server/storage/`).
    """

    base_dir: Path

    def __post_init__(self) -> None:
        self.base_dir = Path(self.base_dir)

    @property
    def base_profile_path(self) -> Path:
        return self.base_dir / "base_profile.json"

    def versions_dir(self, job_id: str) -> Path:
        return self.base_dir / "versions" / job_id

    def meta_path(self, job_id: str) -> Path:
        return self.versions_dir(job_id) / "meta.json"

    def version_path(self, job_id: str, version: int) -> Path:
        return self.versions_dir(job_id) / f"v{version}.json"

    # -- base profile -------------------------------------------------

    def save_base_profile(self, data: dict) -> None:
        _atomic_write_json(self.base_profile_path, data)

    def load_base_profile(self) -> Optional[dict]:
        return _read_json(self.base_profile_path)

    # -- versions -------------------------------------------------------

    def save_version(self, job_id: str, meta: dict, snapshot: dict, version: int) -> None:
        meta_on_disk = _read_json(self.meta_path(job_id)) or {"history": {}}
        meta_on_disk.setdefault("history", {})
        meta_on_disk.update({k: v for k, v in meta.items() if k != "history"})
        meta_on_disk["latest_version"] = version
        meta_on_disk["history"][str(version)] = dict(meta)
        _atomic_write_json(self.meta_path(job_id), meta_on_disk)
        _atomic_write_json(self.version_path(job_id, version), snapshot)

    def get_version(self, job_id: str, version: Optional[int] = None):
        meta = _read_json(self.meta_path(job_id))
        if meta is None:
            return None, None
        resolved_version = version if version is not None else meta.get("latest_version")
        version_meta = meta.get("history", {}).get(str(resolved_version), meta)
        snapshot = _read_json(self.version_path(job_id, resolved_version))
        return version_meta, snapshot

    def list_versions(self, job_id: Optional[str] = None):
        if job_id is not None:
            meta = _read_json(self.meta_path(job_id))
            if meta is None:
                return []
            history = meta.get("history", {})
            versions = [
                {"version": int(number), **entry}
                for number, entry in sorted(history.items(), key=lambda kv: int(kv[0]))
            ]
            return versions

        all_jobs_dir = self.base_dir / "versions"
        if not all_jobs_dir.exists():
            return {}
        result = {}
        for job_dir in sorted(all_jobs_dir.iterdir()):
            if not job_dir.is_dir():
                continue
            meta = _read_json(job_dir / "meta.json")
            if meta is None:
                continue
            result[job_dir.name] = {
                "version": meta.get("latest_version"),
                "meta": meta,
            }
        return result
