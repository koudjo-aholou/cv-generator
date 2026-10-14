from mcp_server.core.storage import StorageRepository
from mcp_server.tools.generation_tools import (
    generate_cv_from_job,
    generate_custom_cv,
    improve_cv_long,
    improve_cv_short,
)

SAMPLE_DATA = {
    "profile": {"first_name": "Ada", "last_name": "Lovelace", "summary": "Base summary"},
    "positions": [
        {"title": "Lead Eng", "company": "Acme", "description": "a"},
        {"title": "Eng", "company": "Beta", "description": "b"},
    ],
    "education": [{"degree": "MSc", "school": "MIT"}],
    "skills": ["Python"],
    "languages": [],
    "certifications": [],
    "photo": "",
}


def _repo(tmp_path):
    repo = StorageRepository(base_dir=tmp_path / "storage")
    repo.save_base_profile(SAMPLE_DATA)
    return repo


def _saved_photo_position(repo, result):
    _, snapshot = repo.get_version(result["job_id"], version=result["version"])
    return snapshot["config"]["photo_position"]


def test_generate_cv_from_job_defaults_photo_to_left(tmp_path):
    repo = _repo(tmp_path)

    result = generate_cv_from_job(repo, "Dev", "Acme", cv_output_dir=tmp_path / "cv")

    assert _saved_photo_position(repo, result) == "left"


def test_generate_cv_from_job_without_photo(tmp_path):
    repo = _repo(tmp_path)

    result = generate_cv_from_job(repo, "Dev", "Acme", photo_position="none", cv_output_dir=tmp_path / "cv")

    assert _saved_photo_position(repo, result) == "none"


def test_generate_custom_cv_without_photo(tmp_path):
    repo = _repo(tmp_path)

    result = generate_custom_cv(
        repo,
        job_title="Dev",
        company="Acme",
        about="About text",
        experiences=[{"index": 1}],
        company_research="Research",
        photo_position="none",
        cv_output_dir=tmp_path / "cv",
    )

    assert _saved_photo_position(repo, result) == "none"


def test_improve_keeps_previous_photo_position(tmp_path):
    repo = _repo(tmp_path)
    first = generate_cv_from_job(repo, "Dev", "Acme", photo_position="none", cv_output_dir=tmp_path / "cv")

    improved = improve_cv_short(repo, first["job_id"], cv_output_dir=tmp_path / "cv")

    assert _saved_photo_position(repo, improved) == "none"


def test_improve_can_change_photo_position(tmp_path):
    repo = _repo(tmp_path)
    first = generate_cv_from_job(repo, "Dev", "Acme", photo_position="none", cv_output_dir=tmp_path / "cv")

    improved = improve_cv_long(repo, first["job_id"], photo_position="left", cv_output_dir=tmp_path / "cv")

    assert _saved_photo_position(repo, improved) == "left"


def test_improve_keeps_right_photo_for_versions_saved_without_position(tmp_path):
    repo = _repo(tmp_path)
    first = generate_cv_from_job(repo, "Dev", "Acme", cv_output_dir=tmp_path / "cv")
    meta, snapshot = repo.get_version(first["job_id"], version=1)
    del snapshot["config"]["photo_position"]
    repo.save_version(first["job_id"], meta, snapshot, version=1)

    improved = improve_cv_long(repo, first["job_id"], cv_output_dir=tmp_path / "cv")

    assert _saved_photo_position(repo, improved) == "right"


def test_invalid_photo_position_returns_error_dict(tmp_path):
    repo = _repo(tmp_path)

    result = generate_cv_from_job(repo, "Dev", "Acme", photo_position="centre", cv_output_dir=tmp_path / "cv")

    assert result["status"] == "error"
    assert "photo_position" in result["error"]
