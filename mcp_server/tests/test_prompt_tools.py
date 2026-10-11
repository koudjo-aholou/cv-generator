import json

from mcp_server.core.storage import StorageRepository
from mcp_server.tools.prompt_tools import custom_cv_brief

PROFILE = {
    "profile": {"first_name": "Ada", "headline": "Data Engineer"},
    "positions": [{"title": "Lead Data Engineer", "company": "Acme Corp"}],
    "skills": ["Python"],
}
POSTING = "Northwind recrute un Data Engineer senior (Airflow, Kubernetes)."
RESEARCH = "Northwind develops open-source data tooling for hospitals since 2015."


def test_custom_cv_brief_embeds_profile_posting_and_research(tmp_path):
    repo = StorageRepository(base_dir=tmp_path)
    repo.save_base_profile(PROFILE)

    text = custom_cv_brief(repo, job_posting=POSTING, company_research=RESEARCH)

    assert json.dumps(PROFILE, indent=2, ensure_ascii=False) in text
    assert POSTING in text
    assert RESEARCH in text
    assert "generate_custom_cv" in text


def test_custom_cv_brief_states_truthfulness_rules(tmp_path):
    repo = StorageRepository(base_dir=tmp_path)
    repo.save_base_profile(PROFILE)

    text = custom_cv_brief(repo, job_posting=POSTING, company_research=RESEARCH).lower()

    assert "invent" in text
    assert "français" in text or "french" in text


def test_custom_cv_brief_without_base_profile_asks_for_one(tmp_path):
    repo = StorageRepository(base_dir=tmp_path)

    text = custom_cv_brief(repo, job_posting=POSTING, company_research=RESEARCH)

    assert "import_linkedin_csv" in text or "set_base_profile" in text
    assert "generate_custom_cv" not in text
