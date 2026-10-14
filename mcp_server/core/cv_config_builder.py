"""Maps short/long CV variants onto CVGenerator's existing config contract.

CVGenerator (backend/cv_generator.py) is reused unmodified: all tailoring
happens here, either by shaping `config` (sections/experience_visible/
education_visible/skills_selected) or by filtering/truncating `data`
(see `condense_data`) before it is handed to CVGenerator.
"""

from __future__ import annotations

import copy
from typing import Any, Optional


def _all_indices(items: Optional[list]) -> list:
    return list(range(len(items or [])))


def build_long_config(overrides: dict, data: dict) -> dict:
    return {
        "sections": {
            "summary": True,
            "experience": True,
            "education": True,
            "skills": True,
            "languages": True,
            "certifications": True,
        },
        "experience_visible": _all_indices(data.get("positions")),
        "education_visible": _all_indices(data.get("education")),
        "skills_selected": None,
    }


def build_short_config(overrides: dict, data: dict) -> dict:
    experience_selection = overrides.get("experience_selection") or {}
    visible_indices = experience_selection.get("visible_indices")
    if visible_indices is None:
        visible_indices = _all_indices(data.get("positions"))[:3]

    education_visible = overrides.get("education_visible_indices")
    if education_visible is None:
        education_visible = _all_indices(data.get("education"))[:1]

    return {
        "sections": {
            "summary": True,
            "experience": True,
            "education": True,
            "skills": True,
            "languages": False,
            "certifications": False,
        },
        "experience_visible": list(visible_indices),
        "education_visible": list(education_visible),
        "skills_selected": overrides.get("skills_selected"),
    }


def build_custom_config(overrides: dict, data: dict) -> dict:
    """Every section on, experiences in the caller's relevance order.

    CVGenerator renders positions in the order of `experience_visible`, so
    ordering by relevance is just a matter of passing the indices in order.
    """
    education_visible = overrides.get("education_visible_indices")
    if education_visible is None:
        education_visible = _all_indices(data.get("education"))

    return {
        "sections": {
            "summary": True,
            "experience": True,
            "education": True,
            "skills": True,
            "languages": True,
            "certifications": True,
        },
        "experience_visible": [item["index"] for item in overrides.get("experiences") or []],
        "education_visible": list(education_visible),
        "skills_selected": overrides.get("skills_selected"),
    }


PHOTO_POSITIONS = ("left", "right", "none")
# CVGenerator itself falls back to "right" when the key is absent (web app
# behaviour); the MCP layer deliberately prefers "left" for every variant.
DEFAULT_PHOTO_POSITION = "left"
BACKEND_PHOTO_POSITION = "right"

VARIANT_BUILDERS = {
    "short": build_short_config,
    "long": build_long_config,
    "custom": build_custom_config,
}


def build_config(variant: str, overrides: dict, data: dict) -> dict:
    builder = VARIANT_BUILDERS.get(variant)
    if builder is None:
        raise ValueError(
            f"Unknown CV variant '{variant}'. Known variants: {sorted(VARIANT_BUILDERS)}"
        )

    config = builder(overrides, data)
    photo_position = overrides.get("photo_position") or DEFAULT_PHOTO_POSITION
    if photo_position not in PHOTO_POSITIONS:
        raise ValueError(
            f"Unknown photo_position '{photo_position}'. Allowed: {list(PHOTO_POSITIONS)}"
        )
    config["photo_position"] = photo_position

    colors = overrides.get("colors")
    if colors:
        config["colors"] = colors

    template = overrides.get("template")
    if template:
        config["template"] = template

    return config


def _validate_custom_content(experiences: list, about: Optional[str], positions_count: int) -> None:
    if not about or not about.strip():
        raise ValueError("about must be a non-empty text")
    if not experiences:
        raise ValueError("experiences must list at least one position index")

    seen = set()
    for item in experiences:
        index = item.get("index")
        if not isinstance(index, int) or isinstance(index, bool) or index < 0 or index >= positions_count:
            raise ValueError(
                f"experience index {index!r} is out of range (base profile has {positions_count} positions)"
            )
        if index in seen:
            raise ValueError(f"experience index {index} is listed more than once")
        seen.add(index)


def apply_custom_content(
    data: dict,
    experiences: list,
    headline: Optional[str],
    about: str,
) -> dict:
    """Inject the custom CV's wording into a deep copy of `data`.

    Truthfulness guard: the caller may only reword a position's
    `description`. Every factual field (title, company, dates, location,
    missions) stays locked to the base profile; extra keys are ignored.
    """
    positions_count = len(data.get("positions") or [])
    _validate_custom_content(experiences, about, positions_count)

    custom = copy.deepcopy(data)
    profile = custom.setdefault("profile", {})
    profile["summary"] = about
    if headline:
        profile["headline"] = headline

    for item in experiences:
        description = item.get("description")
        if description:
            custom["positions"][item["index"]]["description"] = description

    return custom


def _truncate_to_two_bullets(description: str) -> str:
    if not description:
        return description
    lines = [line for line in description.split("\n") if line.strip()]
    return "\n".join(lines[:2])


def condense_data(data: dict, visible_indices: list, emphasis_notes: Optional[dict] = None) -> dict:
    """Deep-copy `data` and truncate each visible position's description.

    Never mutates the input (base_profile.json must stay untouched by
    tailoring). `emphasis_notes` keys are string indices (as they arrive
    from JSON over MCP), mapping to a hand-written replacement description.
    """
    emphasis_notes = emphasis_notes or {}
    condensed = copy.deepcopy(data)
    positions = condensed.get("positions", [])

    for index in visible_indices:
        if index >= len(positions):
            continue
        note = emphasis_notes.get(str(index))
        if note:
            positions[index]["description"] = note
        else:
            positions[index]["description"] = _truncate_to_two_bullets(
                positions[index].get("description", "")
            )

    return condensed
