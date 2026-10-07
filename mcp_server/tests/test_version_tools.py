from mcp_server.core.storage import StorageRepository
from mcp_server.tools.version_tools import get_cv, list_cv_versions


def _seed(repo):
    repo.save_version(
        "acme-lead-20260101-120000",
        {
            "job_id": "acme-lead-20260101-120000",
            "variant": "long",
            "created_at": "t1",
            "pdf_path": "/cv/a.pdf",
        },
        {"data": {}, "config": {"a": 1}},
        version=1,
    )
    repo.save_version(
        "acme-lead-20260101-120000",
        {
            "job_id": "acme-lead-20260101-120000",
            "variant": "short",
            "created_at": "t2",
            "pdf_path": "/cv/b.pdf",
        },
        {"data": {}, "config": {"a": 2}},
        version=2,
    )


def test_list_cv_versions_for_specific_job(tmp_path):
    repo = StorageRepository(base_dir=tmp_path)
    _seed(repo)

    result = list_cv_versions(repo, job_id="acme-lead-20260101-120000")

    assert result["job_id"] == "acme-lead-20260101-120000"
    assert [v["version"] for v in result["versions"]] == [1, 2]


def test_list_cv_versions_returns_latest_per_job_when_omitted(tmp_path):
    repo = StorageRepository(base_dir=tmp_path)
    _seed(repo)
    repo.save_version(
        "beta-eng-20260102-090000",
        {"job_id": "beta-eng-20260102-090000", "variant": "long", "created_at": "t3"},
        {"data": {}, "config": {}},
        version=1,
    )

    result = list_cv_versions(repo, job_id=None)

    assert set(result.keys()) == {"acme-lead-20260101-120000", "beta-eng-20260102-090000"}
    assert result["acme-lead-20260101-120000"]["version"] == 2


def test_get_cv_defaults_to_latest_version(tmp_path):
    repo = StorageRepository(base_dir=tmp_path)
    _seed(repo)

    result = get_cv(repo, job_id="acme-lead-20260101-120000")

    assert result["version"] == 2
    assert result["variant"] == "short"
    assert result["pdf_path"] == "/cv/b.pdf"
    assert result["config_used"] == {"a": 2}


def test_get_cv_specific_version(tmp_path):
    repo = StorageRepository(base_dir=tmp_path)
    _seed(repo)

    result = get_cv(repo, job_id="acme-lead-20260101-120000", version=1)

    assert result["version"] == 1
    assert result["variant"] == "long"


def test_get_cv_missing_job_returns_error(tmp_path):
    repo = StorageRepository(base_dir=tmp_path)

    result = get_cv(repo, job_id="does-not-exist")

    assert result == {"error": "not_found"}
