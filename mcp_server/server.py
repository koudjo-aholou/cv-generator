"""MCP server entrypoint: exposes CV generation/editing tools over stdio.

No LLM calls, no API keys here — all "reasoning" (reading job postings,
deciding what to emphasize) happens in the calling bot's own LLM loop.
This server only assembles/renders, reusing backend.cv_generator.CVGenerator
and backend.linkedin_parser.LinkedInParser unmodified.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, Optional

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mcp.server.fastmcp import FastMCP

from mcp_server.core.storage import StorageRepository
from mcp_server.tools import generation_tools as gen_tools
from mcp_server.tools import profile_tools as prof_tools
from mcp_server.tools import prompt_tools
from mcp_server.tools import version_tools as ver_tools

STORAGE_DIR = Path(os.environ.get("MCP_STORAGE_DIR", _REPO_ROOT / "mcp_server" / "storage"))
CV_OUTPUT_DIR = Path(os.environ.get("MCP_CV_OUTPUT_DIR", _REPO_ROOT / "cv"))

_repo = StorageRepository(base_dir=STORAGE_DIR)

mcp = FastMCP("cv-generator")


# -- profile tools --------------------------------------------------------


@mcp.tool()
def set_base_profile(data: dict) -> dict:
    """Replace the canonical base CV profile in one shot."""
    return prof_tools.set_base_profile(_repo, data=data)


@mcp.tool()
def get_base_profile() -> dict:
    """Return the stored base CV profile, or {"error": "not_found"}."""
    return prof_tools.get_base_profile(_repo)


@mcp.tool()
def import_linkedin_csv(file_paths: list[str]) -> dict:
    """Parse local LinkedIn export CSVs and save the result as the base profile."""
    return prof_tools.import_linkedin_csv(_repo, file_paths=file_paths)


@mcp.tool()
def update_profile_field(field: str, value: Any) -> dict:
    """Update a single simple field on the base profile (headline, summary, ...)."""
    return prof_tools.update_profile_field(_repo, field=field, value=value)


@mcp.tool()
def add_experience(
    title: str = "",
    company: str = "",
    duration: str = "",
    location: str = "",
    description: str = "",
    missions: Optional[list] = None,
    index: Optional[int] = None,
) -> dict:
    """Add a position to the base profile (inserted at `index`, defaults to head)."""
    return prof_tools.add_experience(
        _repo,
        title=title,
        company=company,
        duration=duration,
        location=location,
        description=description,
        missions=missions,
        index=index,
    )


@mcp.tool()
def update_experience(index: int, fields: dict) -> dict:
    """Merge `fields` into the position at `index`."""
    return prof_tools.update_experience(_repo, index=index, fields=fields)


@mcp.tool()
def remove_experience(index: int) -> dict:
    """Remove the position at `index`."""
    return prof_tools.remove_experience(_repo, index=index)


@mcp.tool()
def add_skill(skill: str) -> dict:
    """Add a skill to the base profile's skills list (no-op if already present)."""
    return prof_tools.add_skill(_repo, skill=skill)


@mcp.tool()
def remove_skill(skill: str) -> dict:
    """Remove a skill from the base profile's skills list (no-op if absent)."""
    return prof_tools.remove_skill(_repo, skill=skill)


@mcp.tool()
def update_education(fields: dict, index: Optional[int] = None) -> dict:
    """Add (index=None) or merge-update (index set) an education entry."""
    return prof_tools.update_education(_repo, fields=fields, index=index)


# -- generation tools ------------------------------------------------------


@mcp.tool()
def generate_cv_from_job(
    job_title: str,
    company: str,
    variant: str = "long",
    tailored_summary: Optional[str] = None,
    experience_selection: Optional[dict] = None,
    skills_selected: Optional[list] = None,
    education_visible_indices: Optional[list] = None,
    colors: Optional[dict] = None,
    template: Optional[str] = None,
) -> dict:
    """Generate a tailored CV PDF for a job posting from the base profile."""
    return gen_tools.generate_cv_from_job(
        _repo,
        job_title=job_title,
        company=company,
        variant=variant,
        tailored_summary=tailored_summary,
        experience_selection=experience_selection,
        skills_selected=skills_selected,
        education_visible_indices=education_visible_indices,
        colors=colors,
        template=template,
        cv_output_dir=CV_OUTPUT_DIR,
    )


@mcp.tool()
def generate_custom_cv(
    job_title: str,
    company: str,
    about: str,
    experiences: list[dict],
    company_research: str,
    headline: Optional[str] = None,
    skills_selected: Optional[list] = None,
    education_visible_indices: Optional[list] = None,
    colors: Optional[dict] = None,
    template: Optional[str] = None,
    job_id: Optional[str] = None,
) -> dict:
    """Generate a CV tailored to one posting: experiences in relevance order
    (`experiences` = ordered [{"index": int, "description": str|null}]) and an
    "À propos" (`about`) linking the company research to the real profile.
    Only descriptions can be reworded; titles, companies and dates stay locked
    to the base profile. Pass `job_id` to save as a new version of an existing
    job. See the `custom_cv_brief` prompt for how to prepare the inputs.
    """
    return gen_tools.generate_custom_cv(
        _repo,
        job_title=job_title,
        company=company,
        about=about,
        experiences=experiences,
        company_research=company_research,
        headline=headline,
        skills_selected=skills_selected,
        education_visible_indices=education_visible_indices,
        colors=colors,
        template=template,
        job_id=job_id,
        cv_output_dir=CV_OUTPUT_DIR,
    )


@mcp.tool()
def improve_cv_short(
    job_id: str,
    base_version: int = 1,
    tailored_summary: Optional[str] = None,
    experience_selection: Optional[dict] = None,
    skills_selected: Optional[list] = None,
) -> dict:
    """Regenerate an existing CV job as the short variant with new deltas."""
    return gen_tools.improve_cv_short(
        _repo,
        job_id=job_id,
        base_version=base_version,
        tailored_summary=tailored_summary,
        experience_selection=experience_selection,
        skills_selected=skills_selected,
        cv_output_dir=CV_OUTPUT_DIR,
    )


@mcp.tool()
def improve_cv_long(
    job_id: str,
    base_version: int = 1,
    tailored_summary: Optional[str] = None,
    experience_selection: Optional[dict] = None,
    skills_selected: Optional[list] = None,
) -> dict:
    """Regenerate an existing CV job as the long variant with new deltas."""
    return gen_tools.improve_cv_long(
        _repo,
        job_id=job_id,
        base_version=base_version,
        tailored_summary=tailored_summary,
        experience_selection=experience_selection,
        skills_selected=skills_selected,
        cv_output_dir=CV_OUTPUT_DIR,
    )


# -- version tools ----------------------------------------------------------


@mcp.tool()
def list_cv_versions(job_id: Optional[str] = None):
    """List versions for one job_id, or the latest version of every job_id."""
    return ver_tools.list_cv_versions(_repo, job_id=job_id)


@mcp.tool()
def get_cv(job_id: str, version: Optional[int] = None) -> dict:
    """Fetch metadata + config for one CV version (defaults to latest)."""
    return ver_tools.get_cv(_repo, job_id=job_id, version=version)


# -- prompts ------------------------------------------------------------------


@mcp.prompt()
def custom_cv_brief(job_posting: str, company_research: str) -> str:
    """Instructions for preparing a truthful, original custom CV, embedding
    the current base profile. Executed by the client's LLM, not here."""
    return prompt_tools.custom_cv_brief(
        _repo, job_posting=job_posting, company_research=company_research
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")
