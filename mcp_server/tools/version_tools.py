"""Read-only tools for consulting CV generation history."""

from __future__ import annotations

from typing import Optional

from mcp_server.core.storage import StorageRepository


def list_cv_versions(repo: StorageRepository, job_id: Optional[str] = None):
    if job_id is not None:
        versions = repo.list_versions(job_id)
        return {"job_id": job_id, "versions": versions}

    all_jobs = repo.list_versions()
    return all_jobs


def get_cv(repo: StorageRepository, job_id: str, version: Optional[int] = None) -> dict:
    meta, snapshot = repo.get_version(job_id, version=version)
    if meta is None:
        return {"error": "not_found"}

    return {
        "job_id": job_id,
        "version": meta.get("version"),
        "variant": meta.get("variant"),
        "pdf_path": meta.get("pdf_path"),
        "meta": meta,
        "config_used": snapshot.get("config") if snapshot else None,
    }
