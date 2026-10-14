import copy

from mcp_server.core.cv_config_builder import build_config, condense_data


SAMPLE_DATA = {
    "profile": {"first_name": "Ada", "last_name": "Lovelace", "summary": "..."},
    "positions": [
        {"title": "Lead Eng", "company": "Acme", "description": "line1\nline2\nline3\nline4"},
        {"title": "Eng", "company": "Beta", "description": "x"},
        {"title": "Junior", "company": "Gamma", "description": "y"},
    ],
    "education": [{"degree": "MSc"}, {"degree": "BSc"}],
    "skills": ["Python", "SQL", "AWS"],
    "languages": [{"name": "English"}],
    "certifications": [{"name": "AWS Cert"}],
}


def test_build_config_long_includes_all_sections():
    config = build_config("long", {}, SAMPLE_DATA)

    assert config["sections"]["languages"] is True
    assert config["sections"]["certifications"] is True
    assert config["experience_visible"] == [0, 1, 2]
    assert config["education_visible"] == [0, 1]
    assert config["skills_selected"] is None


def test_build_config_short_limits_sections_and_skills():
    overrides = {
        "experience_selection": {"visible_indices": [0, 1]},
        "education_visible_indices": [0],
        "skills_selected": ["Python", "AWS"],
    }
    config = build_config("short", overrides, SAMPLE_DATA)

    assert config["sections"]["languages"] is False
    assert config["sections"]["certifications"] is False
    assert config["experience_visible"] == [0, 1]
    assert config["education_visible"] == [0]
    assert config["skills_selected"] == ["Python", "AWS"]


def test_build_config_unknown_variant_raises():
    try:
        build_config("medium", {}, SAMPLE_DATA)
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_condense_data_truncates_missions_to_two_bullets():
    condensed = condense_data(SAMPLE_DATA, visible_indices=[0], emphasis_notes={})

    desc_lines = condensed["positions"][0]["description"].split("\n")
    assert len(desc_lines) <= 2


def test_condense_data_never_mutates_input():
    original = copy.deepcopy(SAMPLE_DATA)
    condense_data(SAMPLE_DATA, visible_indices=[0], emphasis_notes={})

    assert SAMPLE_DATA == original


def test_condense_data_uses_emphasis_note_when_provided():
    condensed = condense_data(
        SAMPLE_DATA, visible_indices=[0], emphasis_notes={"0": "custom focus text"}
    )

    assert condensed["positions"][0]["description"] == "custom focus text"


def test_build_config_puts_photo_on_left_for_every_variant():
    custom_overrides = {"experiences": [{"index": 0}]}
    for variant, overrides in (("short", {}), ("long", {}), ("custom", custom_overrides)):
        config = build_config(variant, overrides, SAMPLE_DATA)
        assert config["photo_position"] == "left", variant


def test_build_config_photo_position_can_be_overridden():
    config = build_config("long", {"photo_position": "right"}, SAMPLE_DATA)

    assert config["photo_position"] == "right"


def test_build_config_rejects_unknown_photo_position():
    import pytest

    with pytest.raises(ValueError, match="photo_position"):
        build_config("long", {"photo_position": "centre"}, SAMPLE_DATA)
