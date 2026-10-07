"""Fine-grained editing tools for the base profile (conversational assistant).

Each function is a plain function (SRP: one tool per function) that takes
the `StorageRepository` as its first argument (DIP: injected, never read
from a global env var) and operates on `base_profile.json`.
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from mcp_server.core.storage import StorageRepository

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from backend.linkedin_parser import LinkedInParser  # noqa: E402


def _load_or_empty(repo: StorageRepository) -> dict:
    data = repo.load_base_profile()
    if data is None:
        data = {
            "profile": {},
            "positions": [],
            "education": [],
            "skills": [],
            "languages": [],
            "certifications": [],
        }
    return data


def set_base_profile(repo: StorageRepository, data: dict) -> dict:
    repo.save_base_profile(data)
    return {"status": "ok", "saved_at": datetime.now(timezone.utc).isoformat()}


def get_base_profile(repo: StorageRepository) -> dict:
    data = repo.load_base_profile()
    if data is None:
        return {"error": "not_found"}
    return data


def import_linkedin_csv(repo: StorageRepository, file_paths: list) -> dict:
    data = LinkedInParser(file_paths).parse()
    repo.save_base_profile(data)
    return {"data": data, "saved_as_base_profile": True}


def update_profile_field(repo: StorageRepository, field: str, value: Any) -> dict:
    data = _load_or_empty(repo)
    data.setdefault("profile", {})[field] = value
    repo.save_base_profile(data)
    return {"status": "ok", "field": field, "value": value}


def add_experience(
    repo: StorageRepository,
    title: str = "",
    company: str = "",
    duration: str = "",
    location: str = "",
    description: str = "",
    missions: Optional[list] = None,
    index: Optional[int] = None,
) -> dict:
    data = _load_or_empty(repo)
    positions = data.setdefault("positions", [])
    new_position = {
        "title": title,
        "company": company,
        "duration": duration,
        "location": location,
        "description": description,
        "missions": missions or [],
    }
    insert_at = index if index is not None else 0
    positions.insert(insert_at, new_position)
    repo.save_base_profile(data)
    return {"status": "ok", "position_index": insert_at, "positions_count": len(positions)}


def update_experience(repo: StorageRepository, index: int, fields: dict) -> dict:
    data = _load_or_empty(repo)
    positions = data.setdefault("positions", [])
    if index < 0 or index >= len(positions):
        return {"status": "error", "error": "index_out_of_range"}
    positions[index].update(fields)
    repo.save_base_profile(data)
    return {"status": "ok", "position": positions[index]}


def remove_experience(repo: StorageRepository, index: int) -> dict:
    data = _load_or_empty(repo)
    positions = data.setdefault("positions", [])
    if index < 0 or index >= len(positions):
        return {"status": "error", "error": "index_out_of_range"}
    positions.pop(index)
    repo.save_base_profile(data)
    return {"status": "ok", "positions_count": len(positions)}


def add_skill(repo: StorageRepository, skill: str) -> dict:
    data = _load_or_empty(repo)
    skills = data.setdefault("skills", [])
    if skill not in skills:
        skills.append(skill)
    repo.save_base_profile(data)
    return {"status": "ok", "skills": skills}


def remove_skill(repo: StorageRepository, skill: str) -> dict:
    data = _load_or_empty(repo)
    skills = data.setdefault("skills", [])
    if skill in skills:
        skills.remove(skill)
    repo.save_base_profile(data)
    return {"status": "ok", "skills": skills}


def update_education(repo: StorageRepository, fields: dict, index: Optional[int] = None) -> dict:
    data = _load_or_empty(repo)
    education = data.setdefault("education", [])
    if index is None:
        education.append(fields)
        resolved_index = len(education) - 1
    else:
        if index < 0 or index >= len(education):
            return {"status": "error", "error": "index_out_of_range"}
        education[index].update(fields)
        resolved_index = index
    repo.save_base_profile(data)
    return {"status": "ok", "education": education[resolved_index]}
