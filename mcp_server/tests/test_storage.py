import json

import pytest

from mcp_server.core.storage import StorageRepository


def test_save_and_load_base_profile_roundtrip(tmp_path):
    repo = StorageRepository(base_dir=tmp_path)
    data = {"profile": {"first_name": "Ada"}, "positions": []}

    repo.save_base_profile(data)
    loaded = repo.load_base_profile()

    assert loaded == data


def test_load_base_profile_returns_none_when_missing(tmp_path):
    repo = StorageRepository(base_dir=tmp_path)
    assert repo.load_base_profile() is None


def test_save_base_profile_is_atomic_no_temp_file_left(tmp_path):
    repo = StorageRepository(base_dir=tmp_path)
    repo.save_base_profile({"a": 1})

    files = list(tmp_path.glob("*"))
    assert all(not f.name.endswith(".tmp") for f in files)


def test_save_and_get_version_roundtrip(tmp_path):
    repo = StorageRepository(base_dir=tmp_path)
    meta = {"job_id": "acme-lead-20260101-120000", "variant": "long"}
    snapshot = {"data": {"profile": {}}, "config": {}}

    repo.save_version("acme-lead-20260101-120000", meta, snapshot, version=1)
    loaded_meta, loaded_snapshot = repo.get_version("acme-lead-20260101-120000", version=1)

    assert loaded_meta["job_id"] == "acme-lead-20260101-120000"
    assert loaded_snapshot == snapshot


def test_get_version_defaults_to_latest(tmp_path):
    repo = StorageRepository(base_dir=tmp_path)
    job_id = "acme-lead-20260101-120000"
    repo.save_version(job_id, {"job_id": job_id, "variant": "long"}, {"v": 1}, version=1)
    repo.save_version(job_id, {"job_id": job_id, "variant": "short"}, {"v": 2}, version=2)

    meta, snapshot = repo.get_version(job_id)

    assert snapshot == {"v": 2}
    assert meta["variant"] == "short"


def test_get_version_missing_job_returns_none(tmp_path):
    repo = StorageRepository(base_dir=tmp_path)
    assert repo.get_version("does-not-exist") == (None, None)


def test_list_versions_for_single_job(tmp_path):
    repo = StorageRepository(base_dir=tmp_path)
    job_id = "acme-lead-20260101-120000"
    repo.save_version(job_id, {"job_id": job_id, "variant": "long", "created_at": "t1"}, {"v": 1}, version=1)
    repo.save_version(job_id, {"job_id": job_id, "variant": "short", "created_at": "t2"}, {"v": 2}, version=2)

    versions = repo.list_versions(job_id)

    assert [v["version"] for v in versions] == [1, 2]


def test_list_versions_all_jobs_latest_per_job(tmp_path):
    repo = StorageRepository(base_dir=tmp_path)
    repo.save_version("job-a", {"job_id": "job-a", "variant": "long"}, {"v": 1}, version=1)
    repo.save_version("job-b", {"job_id": "job-b", "variant": "short"}, {"v": 1}, version=1)
    repo.save_version("job-b", {"job_id": "job-b", "variant": "short"}, {"v": 2}, version=2)

    all_jobs = repo.list_versions()

    assert set(all_jobs.keys()) == {"job-a", "job-b"}
    assert all_jobs["job-b"]["version"] == 2
