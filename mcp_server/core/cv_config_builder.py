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


VARIANT_BUILDERS = {
    "short": build_short_config,
    "long": build_long_config,
}


def build_config(variant: str, overrides: dict, data: dict) -> dict:
    builder = VARIANT_BUILDERS.get(variant)
    if builder is None:
        raise ValueError(
            f"Unknown CV variant '{variant}'. Known variants: {sorted(VARIANT_BUILDERS)}"
        )

    config = builder(overrides, data)

    colors = overrides.get("colors")
    if colors:
        config["colors"] = colors

    template = overrides.get("template")
    if template:
        config["template"] = template

    return config


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
