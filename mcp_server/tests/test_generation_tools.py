from mcp_server.core.storage import StorageRepository
from mcp_server.tools.generation_tools import (
    generate_cv_from_job,
    improve_cv_long,
    improve_cv_short,
)

SAMPLE_DATA = {
    "profile": {"first_name": "Ada", "last_name": "Lovelace", "summary": "Base summary"},
    "positions": [
        {"title": "Lead Eng", "company": "Acme", "description": "line1\nline2\nline3"},
        {"title": "Eng", "company": "Beta", "description": "x"},
        {"title": "Junior", "company": "Gamma", "description": "y"},
        {"title": "Intern", "company": "Delta", "description": "z"},
    ],
    "education": [{"degree": "MSc", "school": "MIT"}],
    "skills": ["Python", "SQL", "AWS", "Kubernetes"],
    "languages": [{"name": "English", "proficiency": "Fluent"}],
    "certifications": [],
    "photo": "",
}


def _repo(tmp_path):
    repo = StorageRepository(base_dir=tmp_path / "storage")
    repo.save_base_profile(SAMPLE_DATA)
    return repo


def test_generate_cv_from_job_creates_version_and_pdf(tmp_path):
    repo = _repo(tmp_path)
    cv_dir = tmp_path / "cv"

    result = generate_cv_from_job(
        repo,
        job_title="Lead Data Engineer",
        company="Acme Corp",
        variant="long",
        cv_output_dir=cv_dir,
    )

    assert result["version"] == 1
    assert result["variant"] == "long"
    pdf_path = result["pdf_path"]
    import os

    assert os.path.exists(pdf_path)
    assert os.path.getsize(pdf_path) > 0


def test_generate_cv_from_job_short_variant_filters_positions(tmp_path):
    repo = _repo(tmp_path)
    cv_dir = tmp_path / "cv"

    result = generate_cv_from_job(
        repo,
        job_title="Backend Dev",
        company="Beta Inc",
        variant="short",
        experience_selection={"visible_indices": [0, 1]},
        skills_selected=["Python", "AWS"],
        cv_output_dir=cv_dir,
    )

    meta, snapshot = repo.get_version(result["job_id"])
    assert snapshot["config"]["experience_visible"] == [0, 1]
    assert snapshot["config"]["skills_selected"] == ["Python", "AWS"]


def test_improve_cv_short_increments_version_from_base(tmp_path):
    repo = _repo(tmp_path)
    cv_dir = tmp_path / "cv"

    first = generate_cv_from_job(
        repo,
        job_title="Backend Dev",
        company="Beta Inc",
        variant="long",
        cv_output_dir=cv_dir,
    )

    second = improve_cv_short(
        repo,
        job_id=first["job_id"],
        base_version=1,
        tailored_summary="Tailored for Beta",
        skills_selected=["Python"],
        cv_output_dir=cv_dir,
    )

    assert second["version"] == 2
    assert second["variant"] == "short"
    _, snapshot = repo.get_version(first["job_id"], version=2)
    assert snapshot["data"]["profile"]["summary"] == "Tailored for Beta"


def test_improve_cv_long_forces_long_variant(tmp_path):
    repo = _repo(tmp_path)
    cv_dir = tmp_path / "cv"

    first = generate_cv_from_job(
        repo,
        job_title="Backend Dev",
        company="Beta Inc",
        variant="short",
        cv_output_dir=cv_dir,
    )

    second = improve_cv_long(
        repo,
        job_id=first["job_id"],
        base_version=1,
        cv_output_dir=cv_dir,
    )

    assert second["variant"] == "long"
