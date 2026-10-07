"""End-to-end MCP stdio client smoke test.

Spawns mcp_server/server.py as a subprocess (real MCP client/server over
stdio, exactly how the Telegram bot will talk to this server) and drives a
realistic sequence of tool calls that produce real PDF files under cv/:

  set_base_profile -> generate_cv_from_job(long) -> generate_cv_from_job(short)
  -> improve_cv_short -> list_cv_versions -> get_cv

Runnable standalone (`python mcp_server/scripts/test_client.py`) or via
pytest (`pytest mcp_server/scripts/test_client.py`).
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SERVER_PATH = REPO_ROOT / "mcp_server" / "server.py"

SAMPLE_PROFILE = {
    "profile": {
        "first_name": "Ada",
        "last_name": "Lovelace",
        "headline": "Senior Data Engineer",
        "summary": "10 years building data platforms.",
        "email": "ada@example.com",
        "phone": "+33 6 00 00 00 00",
        "address": "Paris, France",
    },
    "positions": [
        {
            "title": "Lead Data Engineer",
            "company": "Acme Corp",
            "duration": "2021 - Present",
            "location": "Remote",
            "description": "Led migration to Kubernetes.\nBuilt streaming pipelines.\nMentored 4 engineers.",
        },
        {
            "title": "Data Engineer",
            "company": "Beta Inc",
            "duration": "2018 - 2021",
            "location": "Paris",
            "description": "Built ETL pipelines in Airflow.\nOwned the warehouse schema.",
        },
        {
            "title": "Junior Developer",
            "company": "Gamma SARL",
            "duration": "2016 - 2018",
            "location": "Lyon",
            "description": "Backend development in Python/Django.",
        },
    ],
    "education": [{"degree": "MSc Computer Science", "school": "Sorbonne", "start_date": "2014", "end_date": "2016"}],
    "skills": ["Python", "SQL", "AWS", "Kubernetes", "Terraform", "Airflow"],
    "languages": [{"name": "French", "proficiency": "Native"}, {"name": "English", "proficiency": "Fluent"}],
    "certifications": [],
    "photo": "",
}


async def run() -> dict:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    storage_dir = Path(tempfile.mkdtemp(prefix="mcp_cv_test_storage_"))
    cv_output_dir = REPO_ROOT / "cv"

    env = dict(os.environ)
    env["MCP_STORAGE_DIR"] = str(storage_dir)
    env["MCP_CV_OUTPUT_DIR"] = str(cv_output_dir)

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[str(SERVER_PATH)],
        env=env,
    )

    results = {}

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            await session.call_tool("set_base_profile", {"data": SAMPLE_PROFILE})

            long_cv = await session.call_tool(
                "generate_cv_from_job",
                {
                    "job_title": "Lead Data Platform Engineer",
                    "company": "Northwind Analytics",
                    "variant": "long",
                    "tailored_summary": "Data engineering leader specialised in Kubernetes-based platforms.",
                },
            )
            results["long_cv"] = _tool_result_json(long_cv)

            short_cv = await session.call_tool(
                "generate_cv_from_job",
                {
                    "job_title": "Backend Developer",
                    "company": "Contoso Freelance",
                    "variant": "short",
                    "experience_selection": {"visible_indices": [0, 1]},
                    "skills_selected": ["Python", "AWS", "Kubernetes"],
                },
            )
            results["short_cv"] = _tool_result_json(short_cv)

            improved = await session.call_tool(
                "improve_cv_short",
                {
                    "job_id": results["short_cv"]["job_id"],
                    "base_version": 1,
                    "skills_selected": ["Python", "Terraform"],
                },
            )
            results["improved_cv"] = _tool_result_json(improved)

            versions = await session.call_tool(
                "list_cv_versions", {"job_id": results["short_cv"]["job_id"]}
            )
            results["versions"] = _tool_result_json(versions)

            fetched = await session.call_tool("get_cv", {"job_id": results["short_cv"]["job_id"]})
            results["get_cv"] = _tool_result_json(fetched)

    return results


def _tool_result_json(call_tool_result) -> dict:
    """Extract the JSON payload from an MCP CallToolResult's text content."""
    text = call_tool_result.content[0].text
    return json.loads(text)


def main() -> None:
    results = asyncio.run(run())

    print(json.dumps(results, indent=2))

    for key in ("long_cv", "short_cv", "improved_cv"):
        pdf_path = Path(results[key]["pdf_path"])
        assert pdf_path.exists(), f"{key}: PDF not found at {pdf_path}"
        assert pdf_path.stat().st_size > 0, f"{key}: PDF at {pdf_path} is empty"
        print(f"OK {key}: {pdf_path} ({pdf_path.stat().st_size} bytes)")

    print("End-to-end MCP stdio smoke test passed.")


def test_end_to_end_mcp_stdio_client():
    """pytest entrypoint for the same scenario `main()` runs standalone."""
    results = asyncio.run(run())

    for key in ("long_cv", "short_cv", "improved_cv"):
        pdf_path = Path(results[key]["pdf_path"])
        assert pdf_path.exists()
        assert pdf_path.stat().st_size > 0

    assert results["improved_cv"]["version"] == 2
    assert len(results["versions"]["versions"]) == 2


if __name__ == "__main__":
    main()
