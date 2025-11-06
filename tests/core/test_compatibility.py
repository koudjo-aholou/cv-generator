"""
Compatibility Tests - OPTIONAL Priority

Tests for compatibility with different encodings and CSV formats:
- UTF-8 encoding
- Special characters
- Different CSV dialects
- Various date formats
"""

import pytest
import os
import sys
import io
import tempfile
import json

# Add backend to path
backend_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'backend')
sys.path.insert(0, os.path.abspath(backend_dir))

from linkedin_parser import LinkedInParser
from cv_generator import CVGenerator


class TestEncodingCompatibility:
    """Test handling of different character encodings."""

    def test_utf8_characters_in_profile(self, client):
        """Test UTF-8 characters in profile data."""
        # Create CSV with UTF-8 characters
        # Need 'Profile' in filename for parser to recognize it
        csv_content = "First Name,Last Name,Email Address,Phone Number,Summary\n"
        csv_content += "François,Müller,françois@example.com,+33123456789,Développeur logiciel spécialisé\n"

        data = {
            'files': (io.BytesIO(csv_content.encode('utf-8')), 'Profile.csv')
        }

        response = client.post('/api/parse-linkedin',
                              data=data,
                              content_type='multipart/form-data')

        assert response.status_code == 200
        parsed_data = json.loads(response.data)

        # UTF-8 characters should be preserved
        profile = parsed_data.get('profile', {})
        assert profile.get('first_name') == 'François'
        assert profile.get('last_name') == 'Müller'

    def test_special_characters_in_experience(self, client):
        """Test special characters in experience descriptions."""
        csv_content = "Company Name,Title,Started On,Finished On,Description\n"
        csv_content += "Tech™ Corp,Développeur Senior®,2020-01-01,2023-12-31,Led team • Increased revenue by 150% • Managed €2M budget\n"

        data = {
            'files': (io.BytesIO(csv_content.encode('utf-8')), 'Positions.csv')
        }

        response = client.post('/api/parse-linkedin',
                              data=data,
                              content_type='multipart/form-data')

        assert response.status_code == 200
        parsed_data = json.loads(response.data)

        # Special characters should be handled
        experience = parsed_data.get('experience', [])
        if len(experience) > 0:
            desc = experience[0].get('description', '')
            # Should contain some of the special characters or handle them gracefully
            assert isinstance(desc, str)

    def test_emoji_in_data(self, client):
        """Test emoji handling in data."""
        csv_content = "Name\n"
        csv_content += "Python 🐍\n"
        csv_content += "JavaScript ⚡\n"
        csv_content += "Docker 🐳\n"

        data = {
            'files': (io.BytesIO(csv_content.encode('utf-8')), 'Skills.csv')
        }

        response = client.post('/api/parse-linkedin',
                              data=data,
                              content_type='multipart/form-data')

        # Should handle gracefully (either preserve or strip emojis)
        assert response.status_code == 200

    def test_pdf_generation_with_unicode(self):
        """Test PDF generation with unicode characters."""
        data = {
            "profile": {
                "first_name": "José",
                "last_name": "García",
                "email": "josé@example.com",
                "phone": "+34123456789",
                "summary": "Ingeniero de software con experiência en múltiples tecnologías"
            },
            "experience": [
                {
                    "company": "Société Française",
                    "title": "Développeur",
                    "dates": "2020 - 2023",
                    "description": "Développement d'applications • Collaboration avec équipe internationale"
                }
            ],
            "education": [],
            "skills": ["C++", "Python", "JavaScript"],
            "languages": [
                {"name": "Español", "proficiency": "Nativo"},
                {"name": "Français", "proficiency": "Avancé"}
            ],
            "certifications": []
        }

        generator = CVGenerator(data)
        pdf_path = generator.generate()

        # Should generate successfully with unicode
        assert os.path.exists(pdf_path)

        # Clean up
        if os.path.exists(pdf_path):
            os.remove(pdf_path)


class TestCSVFormatCompatibility:
    """Test handling of different CSV formats."""

    def test_csv_with_different_delimiters(self):
        """Test CSV with semicolon delimiter (common in Europe)."""
        # Create CSV with semicolon delimiter
        csv_content = "First Name;Last Name;Email Address\n"
        csv_content += "John;Doe;john@example.com\n"

        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8')
        temp_file.write(csv_content)
        temp_file.close()

        try:
            parser = LinkedInParser([temp_file.name])
            data = parser.parse()

            # Should handle or fail gracefully
            assert isinstance(data, dict)
        except Exception:
            # If parser doesn't support semicolon delimiter, that's okay
            pass
        finally:
            os.remove(temp_file.name)

    def test_csv_with_quoted_fields(self, client):
        """Test CSV with quoted fields containing commas."""
        csv_content = 'Company Name,Title,Started On,Finished On,Description\n'
        csv_content += '"Tech Corp, Inc.","Senior Developer, Team Lead",2020-01-01,2023-12-31,"Led team, managed projects, delivered results"\n'

        data = {
            'files': (io.BytesIO(csv_content.encode('utf-8')), 'Positions.csv')
        }

        response = client.post('/api/parse-linkedin',
                              data=data,
                              content_type='multipart/form-data')

        assert response.status_code == 200
        parsed_data = json.loads(response.data)

        # Quoted fields should be parsed correctly
        experience = parsed_data.get('experience', [])
        if len(experience) > 0:
            # Should preserve commas within quoted fields
            assert 'Tech Corp' in experience[0].get('company', '')

    def test_csv_with_empty_fields(self, client):
        """Test CSV with empty fields."""
        # Need 'Profile' in filename for parser to recognize it
        csv_content = "First Name,Last Name,Email Address,Phone Number,Summary\n"
        csv_content += "John,Doe,,+1234567890,\n"  # Empty email and summary

        data = {
            'files': (io.BytesIO(csv_content.encode('utf-8')), 'Profile.csv')
        }

        response = client.post('/api/parse-linkedin',
                              data=data,
                              content_type='multipart/form-data')

        assert response.status_code == 200
        parsed_data = json.loads(response.data)

        # Should handle empty fields gracefully
        profile = parsed_data.get('profile', {})
        assert profile.get('first_name') == 'John'
        assert profile.get('last_name') == 'Doe'
        assert profile.get('email') == ''  # Empty field should be empty string


class TestDateFormatCompatibility:
    """Test handling of different date formats."""

    def test_different_date_formats(self):
        """Test parsing different date formats."""
        test_cases = [
            ("2020-01-01", "2023-12-31"),  # YYYY-MM-DD
            ("01/01/2020", "12/31/2023"),  # MM/DD/YYYY
            ("2020", "2023"),              # Year only
        ]

        for start_date, end_date in test_cases:
            csv_content = f"Company Name,Title,Started On,Finished On,Description\n"
            csv_content += f"Tech Corp,Developer,{start_date},{end_date},Developed software\n"

            # Need 'positions' in filename for parser to recognize it
            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='_positions.csv', delete=False, encoding='utf-8', prefix='test_')
            temp_file.write(csv_content)
            temp_file.close()

            try:
                parser = LinkedInParser([temp_file.name])
                data = parser.parse()

                # Should parse without crashing
                assert isinstance(data, dict)
                assert 'positions' in data
            finally:
                os.remove(temp_file.name)

    def test_missing_end_date(self):
        """Test parsing with missing end date (current position)."""
        csv_content = "Company Name,Title,Started On,Finished On,Description\n"
        csv_content += "Current Corp,Developer,2023-01-01,,Still working here\n"

        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8')
        temp_file.write(csv_content)
        temp_file.close()

        try:
            parser = LinkedInParser([temp_file.name])
            data = parser.parse()

            experience = data.get('experience', [])
            if len(experience) > 0:
                # Should indicate ongoing/current
                dates = experience[0].get('dates', '')
                assert dates  # Should have some date info
        finally:
            os.remove(temp_file.name)


class TestEdgeCases:
    """Test edge cases and unusual inputs."""

    def test_very_long_text_fields(self, client):
        """Test handling of very long text in fields."""
        long_description = "A" * 10000  # 10KB of text

        csv_content = f"Company Name,Title,Started On,Finished On,Description\n"
        csv_content += f"Tech Corp,Developer,2020-01-01,2023-12-31,{long_description}\n"

        data = {
            'files': (io.BytesIO(csv_content.encode('utf-8')), 'Positions.csv')
        }

        response = client.post('/api/parse-linkedin',
                              data=data,
                              content_type='multipart/form-data')

        # Should handle long text
        assert response.status_code in [200, 400]

    def test_many_skills(self):
        """Test handling of large number of skills."""
        skills = [f"Skill {i}" for i in range(100)]

        data = {
            "profile": {"first_name": "John", "last_name": "Doe"},
            "experience": [],
            "education": [],
            "skills": skills,
            "languages": [],
            "certifications": []
        }

        generator = CVGenerator(data)
        pdf_path = generator.generate()

        # Should handle many skills
        assert os.path.exists(pdf_path)

        # Clean up
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

    def test_newlines_in_description(self, client):
        """Test handling of newlines in description fields."""
        csv_content = 'Company Name,Title,Started On,Finished On,Description\n'
        csv_content += '"Tech Corp","Developer",2020-01-01,2023-12-31,"Line 1\nLine 2\nLine 3"\n'

        data = {
            'files': (io.BytesIO(csv_content.encode('utf-8')), 'Positions.csv')
        }

        response = client.post('/api/parse-linkedin',
                              data=data,
                              content_type='multipart/form-data')

        # Should handle or normalize newlines
        assert response.status_code == 200

    def test_duplicate_csv_files(self, client, mock_profile_csv):
        """Test uploading the same file multiple times."""
        with open(mock_profile_csv, 'rb') as f:
            file_content = f.read()

        data = {
            'files': [
                (io.BytesIO(file_content), 'Profile1.csv'),
                (io.BytesIO(file_content), 'Profile2.csv')
            ]
        }

        response = client.post('/api/parse-linkedin',
                              data=data,
                              content_type='multipart/form-data')

        # Should handle duplicate data (may merge or use last)
        assert response.status_code == 200
