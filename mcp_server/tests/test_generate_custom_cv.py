from pathlib import Path

from mcp_server.core.storage import StorageRepository
from mcp_server.tools.generation_tools import generate_custom_cv, generate_cv_from_job

DATA = {
    "profile": {"first_name": "Ada", "last_name": "Lovelace", "headline": "Dev", "summary": "Base"},
    "positions": [
        {"title": "Lead Eng", "company": "Acme", "duration": "2021 - Present", "description": "a"},
        {"title": "Eng", "company": "Beta", "duration": "2018 - 2021", "description": "b"},
        {"title": "Junior", "company": "Gamma", "duration": "2016 - 2018", "description": "c"},
    ],
    "education": [{"degree": "MSc", "school": "MIT"}],
    "skills": ["Python", "SQL"],
    "languages": [],
    "certifications": [],
    "photo": "",
}

RESEARCH = "Northwind builds open-source data tooling for hospitals."
ABOUT = "Northwind's hospital data tooling matches the pipelines I built at Beta."


def _repo(tmp_path):
    repo = StorageRepository(base_dir=tmp_path / "storage")
    repo.save_base_profile(DATA)
    return repo


def _call(repo, tmp_path, **kwargs):
    params = {
        "job_title": "Data Engineer",
        "company": "Northwind",
        "about": ABOUT,
        "experiences": [{"index": 1, "description": "Reworded Beta"}, {"index": 0}],
        "company_research": RESEARCH,
        "cv_output_dir": tmp_path / "cv",
    }
    params.update(kwargs)
    return generate_custom_cv(repo, **params)


def test_generate_custom_cv_creates_new_job_with_snapshot(tmp_path):
    repo = _repo(tmp_path)

    result = _call(repo, tmp_path, headline="Data Engineer")

    assert result["version"] == 1
    assert result["variant"] == "custom"
    assert Path(result["pdf_path"]).stat().st_size > 0

    meta, snapshot = repo.get_version(result["job_id"])
    assert meta["variant"] == "custom"
    assert snapshot["company_research"] == RESEARCH
    assert snapshot["about"] == ABOUT
    assert snapshot["config"]["experience_visible"] == [1, 0]
    assert snapshot["data"]["profile"]["summary"] == ABOUT
    assert snapshot["data"]["profile"]["headline"] == "Data Engineer"
    assert snapshot["data"]["positions"][1]["description"] == "Reworded Beta"


def test_generate_custom_cv_existing_job_id_saves_next_version(tmp_path):
    repo = _repo(tmp_path)
    first = generate_cv_from_job(
        repo, job_title="Data Engineer", company="Northwind", variant="long",
        cv_output_dir=tmp_path / "cv",
    )

    result = _call(repo, tmp_path, job_id=first["job_id"])

    assert result["job_id"] == first["job_id"]
    assert result["version"] == 2
    assert [v["version"] for v in repo.list_versions(first["job_id"])] == [1, 2]


def test_generate_custom_cv_unknown_job_id_returns_error(tmp_path):
    repo = _repo(tmp_path)

    result = _call(repo, tmp_path, job_id="does-not-exist")

    assert result["status"] == "error"
    assert result["error"] == "job_not_found"


def test_generate_custom_cv_validation_error_returns_error_dict(tmp_path):
    repo = _repo(tmp_path)

    result = _call(repo, tmp_path, experiences=[{"index": 42}])

    assert result["status"] == "error"
    assert "out of range" in result["error"]
    assert repo.list_versions() == {}


def test_generate_custom_cv_without_base_profile_returns_error(tmp_path):
    repo = StorageRepository(base_dir=tmp_path / "storage")

    result = _call(repo, tmp_path)

    assert result == {"status": "error", "error": "no_base_profile"}
