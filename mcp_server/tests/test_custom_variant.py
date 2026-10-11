import copy

import pytest

from mcp_server.core.cv_config_builder import (
    VARIANT_BUILDERS,
    apply_custom_content,
    build_config,
)

DATA = {
    "profile": {"first_name": "Ada", "headline": "Dev", "summary": "Base"},
    "positions": [
        {
            "title": "Lead Eng",
            "company": "Acme",
            "duration": "2021 - Present",
            "location": "Remote",
            "started_on": "2021",
            "finished_on": "",
            "description": "Acme desc",
            "missions": [{"client": "Bank", "title": "Architect", "duration": "2022", "description": "m"}],
        },
        {"title": "Eng", "company": "Beta", "duration": "2018 - 2021", "description": "Beta desc"},
        {"title": "Junior", "company": "Gamma", "duration": "2016 - 2018", "description": "Gamma desc"},
    ],
    "education": [{"degree": "MSc"}, {"degree": "BSc"}],
    "skills": ["Python", "SQL"],
    "languages": [{"name": "English"}],
    "certifications": [{"name": "AWS"}],
}


# -- build_custom_config -------------------------------------------------


def test_custom_variant_is_registered():
    assert "custom" in VARIANT_BUILDERS


def test_build_custom_config_keeps_relevance_order_and_all_sections():
    overrides = {"experiences": [{"index": 2}, {"index": 0}]}

    config = build_config("custom", overrides, DATA)

    assert config["experience_visible"] == [2, 0]
    assert all(config["sections"].values())
    assert set(config["sections"]) == {
        "summary", "experience", "education", "skills", "languages", "certifications",
    }
    assert config["education_visible"] == [0, 1]
    assert config["skills_selected"] is None


def test_build_custom_config_honours_education_and_skills_overrides():
    overrides = {
        "experiences": [{"index": 1}],
        "education_visible_indices": [1],
        "skills_selected": ["SQL", "Python"],
    }

    config = build_config("custom", overrides, DATA)

    assert config["education_visible"] == [1]
    assert config["skills_selected"] == ["SQL", "Python"]


# -- apply_custom_content ------------------------------------------------


def test_apply_custom_content_sets_about_headline_and_descriptions():
    result = apply_custom_content(
        DATA,
        experiences=[{"index": 1, "description": "Reworded Beta"}, {"index": 0, "description": None}],
        headline="Data Engineer",
        about="Real about text",
    )

    assert result["profile"]["summary"] == "Real about text"
    assert result["profile"]["headline"] == "Data Engineer"
    assert result["positions"][1]["description"] == "Reworded Beta"
    assert result["positions"][0]["description"] == "Acme desc"


def test_apply_custom_content_keeps_headline_when_not_given():
    result = apply_custom_content(DATA, experiences=[{"index": 0}], headline=None, about="About")

    assert result["profile"]["headline"] == "Dev"


def test_apply_custom_content_never_mutates_input():
    original = copy.deepcopy(DATA)

    apply_custom_content(
        DATA, experiences=[{"index": 0, "description": "x"}], headline="H", about="A"
    )

    assert DATA == original


def test_apply_custom_content_locks_factual_fields():
    """Only the description can be reworded; any other key is ignored."""
    result = apply_custom_content(
        DATA,
        experiences=[
            {
                "index": 0,
                "description": "New",
                "title": "CTO",
                "company": "Google",
                "duration": "1990 - Present",
                "location": "Mars",
                "started_on": "1990",
                "finished_on": "2030",
                "missions": [{"client": "Fake", "title": "Fake", "duration": "x"}],
            }
        ],
        headline=None,
        about="About",
    )

    position = result["positions"][0]
    original = DATA["positions"][0]
    for key in ("title", "company", "duration", "location", "started_on", "finished_on", "missions"):
        assert position[key] == original[key]
    assert position["description"] == "New"


@pytest.mark.parametrize(
    "experiences, about",
    [
        ([{"index": 5}], "About"),          # out of range
        ([{"index": -1}], "About"),         # negative index
        ([{"index": 0}, {"index": 0}], "About"),  # duplicate
        ([], "About"),                       # empty experiences
        ([{"index": 0}], ""),                # empty about
        ([{"index": 0}], "   \n "),          # blank about
    ],
)
def test_apply_custom_content_guards_raise_value_error(experiences, about):
    with pytest.raises(ValueError):
        apply_custom_content(DATA, experiences=experiences, headline=None, about=about)
