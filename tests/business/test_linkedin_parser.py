"""
LinkedIn Parser Tests - HIGH Priority (Business Logic)

Tests for LinkedIn CSV parsing functionality including:
- Profile data parsing
- Experience parsing
- Education parsing
- Skills parsing
- Languages parsing
- Certifications parsing
- Date formatting
- Error handling
"""

import pytest
import os
import sys
import tempfile
import csv

# Add backend to path
backend_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'backend')
sys.path.insert(0, os.path.abspath(backend_dir))

from linkedin_parser import LinkedInParser


class TestProfileParsing:
    """Test profile data parsing."""

    def test_parse_complete_profile(self, mock_profile_csv):
        """Test parsing complete profile data."""
        parser = LinkedInParser([mock_profile_csv])
        data = parser.parse()

        assert 'profile' in data
        profile = data['profile']
        assert profile['first_name'] == 'John'
        assert profile['last_name'] == 'Doe'
        assert profile['email'] == 'john.doe@example.com'
        assert profile['phone'] == '+1234567890'
        assert 'Software Engineer' in profile['summary']

    def test_parse_profile_with_missing_fields(self):
        """Test parsing profile with missing optional fields."""
        # Need 'profile' in filename so parser recognizes it
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='_profile.csv', delete=False, encoding='utf-8', prefix='test_')
        temp_file.write("First Name,Last Name,Email Address\n")
        temp_file.write("Jane,Smith,jane@example.com\n")
        temp_file.close()

        try:
            parser = LinkedInParser([temp_file.name])
            data = parser.parse()

            profile = data['profile']
            assert profile['first_name'] == 'Jane'
            assert profile['last_name'] == 'Smith'
            assert profile['email'] == 'jane@example.com'
            # Missing fields should be handled gracefully
            assert 'phone' in profile  # May be empty string
        finally:
            os.remove(temp_file.name)

    def test_parse_empty_profile(self):
        """Test parsing empty profile CSV."""
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8')
        temp_file.write("First Name,Last Name,Email Address,Phone,Summary\n")
        temp_file.close()

        try:
            parser = LinkedInParser([temp_file.name])
            data = parser.parse()

            # Should have profile structure even if empty
            assert 'profile' in data
        finally:
            os.remove(temp_file.name)


class TestExperienceParsing:
    """Test experience/positions parsing."""

    def test_parse_multiple_positions(self, mock_positions_csv):
        """Test parsing multiple work positions."""
        parser = LinkedInParser([mock_positions_csv])
        data = parser.parse()

        assert 'positions' in data
        positions = data['positions']
        assert len(positions) >= 2

        # Check first position
        first_pos = positions[0]
        assert first_pos['company'] == 'Tech Corp'
        assert first_pos['title'] == 'Senior Developer'
        assert '2020' in first_pos['duration']

    def test_parse_position_with_description(self, mock_positions_csv):
        """Test that position descriptions are parsed."""
        parser = LinkedInParser([mock_positions_csv])
        data = parser.parse()

        positions = data['positions']
        assert len(positions) > 0
        assert 'description' in positions[0]
        assert positions[0]['description']  # Should not be empty

    def test_parse_current_position(self):
        """Test parsing position with no end date (current role)."""
        # Need 'position' in filename so parser recognizes it
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='_positions.csv', delete=False, encoding='utf-8', prefix='test_')
        temp_file.write("Company Name,Title,Started On,Finished On,Description\n")
        temp_file.write("Current Corp,Senior Engineer,2023-01-01,,Working on amazing projects\n")
        temp_file.close()

        try:
            parser = LinkedInParser([temp_file.name])
            data = parser.parse()

            positions = data['positions']
            assert len(positions) > 0
            # Should indicate current position
            assert 'Présent' in positions[0]['duration'] or 'present' in positions[0]['duration'].lower()
        finally:
            os.remove(temp_file.name)

    def test_parse_empty_experience(self):
        """Test parsing empty experience CSV."""
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8')
        temp_file.write("Company Name,Title,Started On,Finished On,Description\n")
        temp_file.close()

        try:
            parser = LinkedInParser([temp_file.name])
            data = parser.parse()

            assert 'positions' in data
            assert isinstance(data['positions'], list)
        finally:
            os.remove(temp_file.name)


class TestEducationParsing:
    """Test education data parsing."""

    def test_parse_education_entries(self, mock_education_csv):
        """Test parsing education entries."""
        parser = LinkedInParser([mock_education_csv])
        data = parser.parse()

        assert 'education' in data
        education = data['education']
        assert len(education) > 0

        # Check education structure
        edu = education[0]
        assert 'school' in edu
        assert 'degree' in edu
        assert 'start_date' in edu or 'end_date' in edu

    def test_parse_education_dates(self, mock_education_csv):
        """Test that education dates are parsed."""
        parser = LinkedInParser([mock_education_csv])
        data = parser.parse()

        education = data['education']
        assert len(education) > 0
        # Should have date fields
        assert education[0]['start_date'] or education[0]['end_date']

    def test_parse_empty_education(self):
        """Test parsing empty education CSV."""
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8')
        temp_file.write("School Name,Degree Name,Start Date,End Date\n")
        temp_file.close()

        try:
            parser = LinkedInParser([temp_file.name])
            data = parser.parse()

            assert 'education' in data
            assert isinstance(data['education'], list)
        finally:
            os.remove(temp_file.name)


class TestSkillsParsing:
    """Test skills parsing."""

    def test_parse_skills_list(self, mock_skills_csv):
        """Test parsing skills list."""
        parser = LinkedInParser([mock_skills_csv])
        data = parser.parse()

        assert 'skills' in data
        skills = data['skills']
        assert isinstance(skills, list)
        assert len(skills) >= 3
        assert 'Python' in skills
        assert 'JavaScript' in skills

    def test_parse_empty_skills(self):
        """Test parsing empty skills CSV."""
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8')
        temp_file.write("Name\n")
        temp_file.close()

        try:
            parser = LinkedInParser([temp_file.name])
            data = parser.parse()

            assert 'skills' in data
            assert isinstance(data['skills'], list)
        finally:
            os.remove(temp_file.name)


class TestLanguagesParsing:
    """Test languages parsing."""

    def test_parse_languages_with_proficiency(self, mock_languages_csv):
        """Test parsing languages with proficiency levels."""
        parser = LinkedInParser([mock_languages_csv])
        data = parser.parse()

        assert 'languages' in data
        languages = data['languages']
        assert len(languages) >= 2

        # Check structure
        lang = languages[0]
        assert 'name' in lang
        assert 'proficiency' in lang

    def test_parse_language_proficiency_levels(self, mock_languages_csv):
        """Test that proficiency levels are captured."""
        parser = LinkedInParser([mock_languages_csv])
        data = parser.parse()

        languages = data['languages']
        # Should have proficiency info
        assert any('proficiency' in lang and lang['proficiency'] for lang in languages)

    def test_parse_empty_languages(self):
        """Test parsing empty languages CSV."""
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8')
        temp_file.write("Name,Proficiency\n")
        temp_file.close()

        try:
            parser = LinkedInParser([temp_file.name])
            data = parser.parse()

            assert 'languages' in data
            assert isinstance(data['languages'], list)
        finally:
            os.remove(temp_file.name)


class TestCertificationsParsing:
    """Test certifications parsing."""

    def test_parse_certifications(self, mock_certifications_csv):
        """Test parsing certifications."""
        parser = LinkedInParser([mock_certifications_csv])
        data = parser.parse()

        assert 'certifications' in data
        certifications = data['certifications']
        assert len(certifications) > 0

        # Check structure
        cert = certifications[0]
        assert 'name' in cert
        assert 'authority' in cert
        assert 'start_date' in cert or 'end_date' in cert

    def test_parse_certification_authority(self, mock_certifications_csv):
        """Test that certification authority is captured."""
        parser = LinkedInParser([mock_certifications_csv])
        data = parser.parse()

        certifications = data['certifications']
        assert certifications[0]['authority'] == 'Amazon'

    def test_parse_empty_certifications(self):
        """Test parsing empty certifications CSV."""
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8')
        temp_file.write("Name,Authority,Started On,Finished On\n")
        temp_file.close()

        try:
            parser = LinkedInParser([temp_file.name])
            data = parser.parse()

            assert 'certifications' in data
            assert isinstance(data['certifications'], list)
        finally:
            os.remove(temp_file.name)


class TestDateFormatting:
    """Test date formatting functionality."""

    def test_date_range_with_both_dates(self):
        """Test formatting date range with start and end dates."""
        parser = LinkedInParser([])
        formatted = parser._format_date_range('2020-01-01', '2023-12-31')
        assert '2020-01-01' in formatted
        assert '2023-12-31' in formatted
        assert '-' in formatted

    def test_date_range_current_role(self):
        """Test formatting date range for current role (no end date)."""
        parser = LinkedInParser([])
        formatted = parser._format_date_range('2020-01-01', '')
        assert '2020-01-01' in formatted
        assert 'Présent' in formatted or 'present' in formatted.lower()

    def test_date_range_with_none_end_date(self):
        """Test formatting date range with None end date."""
        parser = LinkedInParser([])
        formatted = parser._format_date_range('2020-01-01', None)
        assert '2020-01-01' in formatted


class TestErrorHandling:
    """Test error handling in parser."""

    def test_parse_with_malformed_csv(self):
        """Test parsing malformed CSV file."""
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8')
        temp_file.write("Invalid,CSV,Structure\n")
        temp_file.write("This,is,malformed,with,extra,columns\n")
        temp_file.close()

        try:
            parser = LinkedInParser([temp_file.name])
            data = parser.parse()
            # Should not crash, should return structure
            assert isinstance(data, dict)
        finally:
            os.remove(temp_file.name)

    def test_parse_nonexistent_file(self):
        """Test parsing non-existent file."""
        # Parser handles errors gracefully, should not crash
        try:
            parser = LinkedInParser(['/nonexistent/file.csv'])
            data = parser.parse()
            # Should return empty structure
            assert isinstance(data, dict)
        except FileNotFoundError:
            # This is also acceptable behavior
            pass
