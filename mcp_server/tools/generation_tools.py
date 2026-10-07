"""Tools that assemble/render a tailored CV for a job posting, via CVGenerator.

No LLM calls happen here: the tailoring content (tailored_summary,
experience_selection, skills_selected) is decided by the calling bot's own
LLM loop and simply passed through. This module only builds config, filters
data, calls CVGenerator.generate(), writes the PDF to disk, and persists a
version snapshot.
"""

from __future__ import annotations

import copy
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from mcp_server.core.cv_config_builder import build_config, condense_data
from mcp_server.core.storage import StorageRepository

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from backend.cv_generator import CVGenerator  # noqa: E402

DEFAULT_CV_OUTPUT_DIR = _REPO_ROOT / "cv"


def _slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "na"


def _make_job_id(company: str, job_title: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return f"{_slugify(company)}-{_slugify(job_title)}-{timestamp}"


def _render_and_save_pdf(data: dict, config: dict, cv_output_dir: Path) -> str:
    generator = CVGenerator(data, config)
    buffer = generator.generate()
    cv_output_dir.mkdir(parents=True, exist_ok=True)
    filename = generator.suggested_filename()
    pdf_path = cv_output_dir / filename
    pdf_path.write_bytes(buffer.read())
    return str(pdf_path)


def generate_cv_from_job(
    repo: StorageRepository,
    job_title: str,
    company: str,
    variant: str = "long",
    tailored_summary: Optional[str] = None,
    experience_selection: Optional[dict] = None,
    skills_selected: Optional[list] = None,
    education_visible_indices: Optional[list] = None,
    colors: Optional[dict] = None,
    template: Optional[str] = None,
    cv_output_dir: Path = DEFAULT_CV_OUTPUT_DIR,
) -> dict:
    base_data = repo.load_base_profile()
    if base_data is None:
        return {"status": "error", "error": "no_base_profile"}

    overrides = {
        "experience_selection": experience_selection or {},
        "skills_selected": skills_selected,
        "education_visible_indices": education_visible_indices,
        "colors": colors,
        "template": template,
    }
    config = build_config(variant, overrides, base_data)

    data = copy.deepcopy(base_data)
    if variant == "short":
        data = condense_data(
            data,
            visible_indices=config["experience_visible"],
            emphasis_notes=(experience_selection or {}).get("emphasis_notes") or {},
        )
    if tailored_summary:
        data.setdefault("profile", {})["summary"] = tailored_summary

    pdf_path = _render_and_save_pdf(data, config, Path(cv_output_dir))

    job_id = _make_job_id(company, job_title)
    created_at = datetime.now(timezone.utc).isoformat()
    meta = {
        "job_id": job_id,
        "created_at": created_at,
        "job_title": job_title,
        "company": company,
        "variant": variant,
        "pdf_path": pdf_path,
        "status": "generated",
    }
    snapshot = {"data": data, "config": config}
    repo.save_version(job_id, meta, snapshot, version=1)

    return {"job_id": job_id, "pdf_path": pdf_path, "variant": variant, "version": 1}


def _improve_cv(
    repo: StorageRepository,
    job_id: str,
    base_version: int,
    variant: str,
    tailored_summary: Optional[str],
    experience_selection: Optional[dict],
    skills_selected: Optional[list],
    cv_output_dir: Path,
) -> dict:
    meta, snapshot = repo.get_version(job_id, version=base_version)
    if meta is None or snapshot is None:
        return {"status": "error", "error": "version_not_found"}

    data = copy.deepcopy(snapshot["data"])
    config = copy.deepcopy(snapshot["config"])

    overrides = {
        "experience_selection": experience_selection or {},
        "skills_selected": skills_selected if skills_selected is not None else config.get("skills_selected"),
        "education_visible_indices": config.get("education_visible"),
    }
    base_profile_for_defaults = {"positions": data.get("positions", []), "education": data.get("education", [])}
    config = build_config(variant, overrides, base_profile_for_defaults)

    if variant == "short":
        data = condense_data(
            data,
            visible_indices=config["experience_visible"],
            emphasis_notes=(experience_selection or {}).get("emphasis_notes") or {},
        )
    if tailored_summary:
        data.setdefault("profile", {})["summary"] = tailored_summary

    pdf_path = _render_and_save_pdf(data, config, Path(cv_output_dir))

    next_version = meta.get("latest_version", base_version) + 1
    new_meta = dict(meta)
    new_meta.update(
        {
            "variant": variant,
            "pdf_path": pdf_path,
            "status": "improved",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    new_snapshot = {"data": data, "config": config}
    repo.save_version(job_id, new_meta, new_snapshot, version=next_version)

    return {"job_id": job_id, "pdf_path": pdf_path, "variant": variant, "version": next_version}


def improve_cv_short(
    repo: StorageRepository,
    job_id: str,
    base_version: int = 1,
    tailored_summary: Optional[str] = None,
    experience_selection: Optional[dict] = None,
    skills_selected: Optional[list] = None,
    cv_output_dir: Path = DEFAULT_CV_OUTPUT_DIR,
) -> dict:
    return _improve_cv(
        repo,
        job_id,
        base_version,
        variant="short",
        tailored_summary=tailored_summary,
        experience_selection=experience_selection,
        skills_selected=skills_selected,
        cv_output_dir=cv_output_dir,
    )


def improve_cv_long(
    repo: StorageRepository,
    job_id: str,
    base_version: int = 1,
    tailored_summary: Optional[str] = None,
    experience_selection: Optional[dict] = None,
    skills_selected: Optional[list] = None,
    cv_output_dir: Path = DEFAULT_CV_OUTPUT_DIR,
) -> dict:
    return _improve_cv(
        repo,
        job_id,
        base_version,
        variant="long",
        tailored_summary=tailored_summary,
        experience_selection=experience_selection,
        skills_selected=skills_selected,
        cv_output_dir=cv_output_dir,
    )
