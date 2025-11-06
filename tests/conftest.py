"""
Pytest configuration and shared fixtures for CV Generator tests.

This module provides common fixtures and configurations used across all test modules.
"""

import pytest
import sys
import os
import tempfile
import shutil
from pathlib import Path

# Add backend directory to Python path
backend_dir = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.insert(0, os.path.abspath(backend_dir))

from app import app as flask_app


@pytest.fixture
def app():
    """Create Flask app instance for testing."""
    flask_app.config['TESTING'] = True
    flask_app.config['DEBUG'] = False
    yield flask_app


@pytest.fixture
def client(app):
    """Create Flask test client."""
    return app.test_client()


@pytest.fixture
def temp_upload_dir():
    """Create temporary upload directory for tests."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


@pytest.fixture
def mock_csv_file():
    """Create a mock CSV file for testing."""
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8')
    temp_file.write("header1,header2,header3\n")
    temp_file.write("value1,value2,value3\n")
    temp_file.close()
    yield temp_file.name
    # Cleanup
    if os.path.exists(temp_file.name):
        os.remove(temp_file.name)


@pytest.fixture
def mock_profile_csv():
    """Create a mock Profile.csv for testing."""
    # Use prefix with 'profile' so parser recognizes it
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='_profile.csv', delete=False, encoding='utf-8', prefix='test_')
    temp_file.write("First Name,Last Name,Email Address,Phone Number,Summary\n")
    temp_file.write("John,Doe,john.doe@example.com,+1234567890,Software Engineer with 5 years experience\n")
    temp_file.close()
    yield temp_file.name
    if os.path.exists(temp_file.name):
        os.remove(temp_file.name)


@pytest.fixture
def mock_positions_csv():
    """Create a mock Positions.csv for testing."""
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='_positions.csv', delete=False, encoding='utf-8', prefix='test_')
    temp_file.write("Company Name,Title,Started On,Finished On,Description\n")
    temp_file.write("Tech Corp,Senior Developer,2020-01-01,2023-12-31,Developed web applications\n")
    temp_file.write("StartUp Inc,Developer,2018-06-01,2019-12-31,Built mobile apps\n")
    temp_file.close()
    yield temp_file.name
    if os.path.exists(temp_file.name):
        os.remove(temp_file.name)


@pytest.fixture
def mock_education_csv():
    """Create a mock Education.csv for testing."""
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='_education.csv', delete=False, encoding='utf-8', prefix='test_')
    temp_file.write("School Name,Degree Name,Start Date,End Date\n")
    temp_file.write("University of Example,Bachelor of Science,2014-09-01,2018-06-01\n")
    temp_file.close()
    yield temp_file.name
    if os.path.exists(temp_file.name):
        os.remove(temp_file.name)


@pytest.fixture
def mock_skills_csv():
    """Create a mock Skills.csv for testing."""
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='_skills.csv', delete=False, encoding='utf-8', prefix='test_')
    temp_file.write("Name\n")
    temp_file.write("Python\n")
    temp_file.write("JavaScript\n")
    temp_file.write("Docker\n")
    temp_file.close()
    yield temp_file.name
    if os.path.exists(temp_file.name):
        os.remove(temp_file.name)


@pytest.fixture
def mock_languages_csv():
    """Create a mock Languages.csv for testing."""
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='_languages.csv', delete=False, encoding='utf-8', prefix='test_')
    temp_file.write("Name,Proficiency\n")
    temp_file.write("English,Native or bilingual proficiency\n")
    temp_file.write("French,Professional working proficiency\n")
    temp_file.close()
    yield temp_file.name
    if os.path.exists(temp_file.name):
        os.remove(temp_file.name)


@pytest.fixture
def mock_certifications_csv():
    """Create a mock Certifications.csv for testing."""
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='_certifications.csv', delete=False, encoding='utf-8', prefix='test_')
    temp_file.write("Name,Authority,Started On,Finished On\n")
    temp_file.write("AWS Certified Developer,Amazon,2021-01-01,2024-01-01\n")
    temp_file.close()
    yield temp_file.name
    if os.path.exists(temp_file.name):
        os.remove(temp_file.name)


@pytest.fixture
def mock_parsed_data():
    """Create mock parsed LinkedIn data matching actual parser output."""
    return {
        "profile": {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone": "+1234567890",
            "summary": "Software Engineer with 5 years experience"
        },
        "positions": [
            {
                "company": "Tech Corp",
                "title": "Senior Developer",
                "duration": "2020-01-01 - 2023-12-31",
                "description": "Developed web applications",
                "started_on": "2020-01-01",
                "finished_on": "2023-12-31",
                "location": "New York"
            }
        ],
        "education": [
            {
                "school": "University of Example",
                "degree": "Bachelor of Science",
                "start_date": "2014-09-01",
                "end_date": "2018-06-01",
                "field_of_study": "Computer Science"
            }
        ],
        "skills": ["Python", "JavaScript", "Docker"],
        "languages": [
            {"name": "English", "proficiency": "Native or bilingual proficiency"}
        ],
        "certifications": [
            {
                "name": "AWS Certified Developer",
                "authority": "Amazon",
                "start_date": "2021-01-01",
                "end_date": "2024-01-01"
            }
        ]
    }


@pytest.fixture
def mock_large_file_content():
    """Create content for a large file (11MB)."""
    # Create 11MB of data
    return "a" * (11 * 1024 * 1024)


@pytest.fixture
def mock_base64_image():
    """Create a mock base64-encoded image."""
    # 1x1 pixel PNG
    return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="


@pytest.fixture
def mock_large_base64_image():
    """Create a mock large base64-encoded image (6MB)."""
    # Create base64 string representing ~6MB
    return "a" * (8 * 1024 * 1024)  # Base64 is ~33% larger, so 8MB base64 = ~6MB binary
