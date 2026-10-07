import pytest

from mcp_server.core.storage import StorageRepository
from mcp_server.tools.profile_tools import (
    add_experience,
    add_skill,
    remove_experience,
    remove_skill,
    update_education,
    update_experience,
    update_profile_field,
)


def _repo_with_profile(tmp_path, profile=None):
    repo = StorageRepository(base_dir=tmp_path)
    repo.save_base_profile(
        profile
        or {
            "profile": {"headline": "Dev", "summary": "..."},
            "positions": [{"title": "Eng", "company": "Acme"}],
            "education": [{"degree": "BSc"}],
            "skills": ["Python"],
            "languages": [],
            "certifications": [],
        }
    )
    return repo


def test_update_profile_field_nominal(tmp_path):
    repo = _repo_with_profile(tmp_path)

    result = update_profile_field(repo, field="headline", value="Lead Dev")

    assert result["status"] == "ok"
    assert repo.load_base_profile()["profile"]["headline"] == "Lead Dev"


def test_add_experience_defaults_to_head(tmp_path):
    repo = _repo_with_profile(tmp_path)

    result = add_experience(repo, title="New Role", company="NewCo")

    data = repo.load_base_profile()
    assert data["positions"][0]["title"] == "New Role"
    assert result["positions_count"] == 2


def test_update_experience_merges_fields(tmp_path):
    repo = _repo_with_profile(tmp_path)

    result = update_experience(repo, index=0, fields={"title": "Senior Eng"})

    assert result["position"]["title"] == "Senior Eng"
    assert result["position"]["company"] == "Acme"


def test_update_experience_out_of_range_returns_error(tmp_path):
    repo = _repo_with_profile(tmp_path)

    result = update_experience(repo, index=5, fields={"title": "x"})

    assert result["status"] == "error"
    assert result["error"] == "index_out_of_range"


def test_remove_experience_nominal(tmp_path):
    repo = _repo_with_profile(tmp_path)

    result = remove_experience(repo, index=0)

    assert result["status"] == "ok"
    assert result["positions_count"] == 0


def test_remove_experience_out_of_range_returns_error(tmp_path):
    repo = _repo_with_profile(tmp_path)

    result = remove_experience(repo, index=99)

    assert result["status"] == "error"
    assert result["error"] == "index_out_of_range"


def test_add_skill_nominal(tmp_path):
    repo = _repo_with_profile(tmp_path)

    result = add_skill(repo, skill="Kubernetes")

    assert "Kubernetes" in result["skills"]


def test_remove_skill_not_present_is_noop_ok(tmp_path):
    repo = _repo_with_profile(tmp_path)

    result = remove_skill(repo, skill="DoesNotExist")

    assert result["status"] == "ok"
    assert result["skills"] == ["Python"]


def test_update_education_add_when_index_none(tmp_path):
    repo = _repo_with_profile(tmp_path)

    update_education(repo, index=None, fields={"degree": "MSc"})

    data = repo.load_base_profile()
    assert len(data["education"]) == 2
    assert data["education"][-1]["degree"] == "MSc"
