from pathlib import Path

from mcp_server.core.storage import StorageRepository
from mcp_server.tools.profile_tools import (
    get_base_profile,
    import_linkedin_csv,
    set_base_profile,
)

MOCK_DIR = Path(__file__).resolve().parents[2] / "mock"


def test_set_and_get_base_profile_roundtrip(tmp_path):
    repo = StorageRepository(base_dir=tmp_path)
    data = {"profile": {"first_name": "Ada"}, "positions": []}

    set_result = set_base_profile(repo, data=data)
    get_result = get_base_profile(repo)

    assert set_result["status"] == "ok"
    assert get_result == data


def test_get_base_profile_not_found(tmp_path):
    repo = StorageRepository(base_dir=tmp_path)

    result = get_base_profile(repo)

    assert result == {"error": "not_found"}


def test_import_linkedin_csv_saves_as_base_profile(tmp_path):
    repo = StorageRepository(base_dir=tmp_path)
    file_paths = [str(MOCK_DIR / "Profile.csv"), str(MOCK_DIR / "Positions.csv")]

    result = import_linkedin_csv(repo, file_paths=file_paths)

    assert result["saved_as_base_profile"] is True
    assert repo.load_base_profile() == result["data"]
    assert "profile" in result["data"]
