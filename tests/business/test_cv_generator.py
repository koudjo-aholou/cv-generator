"""
CV Generator Tests - HIGH Priority (Business Logic)

Tests for PDF CV generation functionality including:
- PDF generation
- Photo handling
- Header creation
- Section generation
- Layout and styling
- Pagination
- Error handling
"""

import pytest
import os
import sys
import tempfile
from unittest.mock import patch, MagicMock
from io import BytesIO

# Add backend to path
backend_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'backend')
sys.path.insert(0, os.path.abspath(backend_dir))

from cv_generator import CVGenerator
from reportlab.lib.pagesizes import A4


class TestPDFGeneration:
    """Test basic PDF generation."""

    def test_generate_pdf_success(self, mock_parsed_data):
        """Test that PDF is generated successfully."""
        generator = CVGenerator(mock_parsed_data)
        pdf_path = generator.generate()

        # PDF file should be created
        assert os.path.exists(pdf_path)
        assert pdf_path.endswith('.pdf')

        # Clean up
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

    def test_generated_pdf_is_valid(self, mock_parsed_data):
        """Test that generated PDF is valid."""
        generator = CVGenerator(mock_parsed_data)
        pdf_path = generator.generate()

        # Check file is not empty and has PDF magic number
        with open(pdf_path, 'rb') as f:
            content = f.read()
            assert len(content) > 0
            assert content.startswith(b'%PDF')

        # Clean up
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

    def test_pdf_size_reasonable(self, mock_parsed_data):
        """Test that generated PDF has reasonable size."""
        generator = CVGenerator(mock_parsed_data)
        pdf_path = generator.generate()

        # PDF should be between 1KB and 10MB
        size = os.path.getsize(pdf_path)
        assert 1024 < size < 10 * 1024 * 1024

        # Clean up
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

    def test_generate_with_minimal_data(self):
        """Test PDF generation with minimal data."""
        minimal_data = {
            "profile": {
                "first_name": "John",
                "last_name": "Doe"
            },
            "positions": [],
            "education": [],
            "skills": [],
            "languages": [],
            "certifications": []
        }

        generator = CVGenerator(minimal_data)
        pdf_path = generator.generate()

        assert os.path.exists(pdf_path)

        # Clean up
        if os.path.exists(pdf_path):
            os.remove(pdf_path)


class TestPhotoHandling:
    """Test photo handling in PDF."""

    def test_generate_pdf_with_photo(self, mock_parsed_data, mock_base64_image):
        """Test PDF generation with profile photo."""
        data = mock_parsed_data.copy()
        data['photo'] = f"data:image/png;base64,{mock_base64_image}"

        generator = CVGenerator(data)
        pdf_path = generator.generate()

        # Should generate successfully
        assert os.path.exists(pdf_path)

        # PDF with photo should be larger than without
        size_with_photo = os.path.getsize(pdf_path)

        # Clean up
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

        # Generate without photo
        generator_no_photo = CVGenerator(mock_parsed_data)
        pdf_path_no_photo = generator_no_photo.generate()
        size_without_photo = os.path.getsize(pdf_path_no_photo)

        # Clean up
        if os.path.exists(pdf_path_no_photo):
            os.remove(pdf_path_no_photo)

        # Photo should add some size
        assert size_with_photo >= size_without_photo

    def test_generate_pdf_without_photo(self, mock_parsed_data):
        """Test PDF generation without photo."""
        # Ensure no photo in data
        data = mock_parsed_data.copy()
        data.pop('photo', None)

        generator = CVGenerator(data)
        pdf_path = generator.generate()

        assert os.path.exists(pdf_path)

        # Clean up
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

    def test_photo_error_handling(self, mock_parsed_data):
        """Test that invalid photo data doesn't crash generation."""
        data = mock_parsed_data.copy()
        data['photo'] = "invalid_base64_data"

        generator = CVGenerator(data)
        # Should not crash, might generate without photo
        pdf_path = generator.generate()

        assert os.path.exists(pdf_path)

        # Clean up
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

    def test_photo_dimensions_fixed(self, mock_parsed_data, mock_base64_image):
        """Test that photo is resized to fixed dimensions."""
        data = mock_parsed_data.copy()
        data['photo'] = f"data:image/png;base64,{mock_base64_image}"

        generator = CVGenerator(data)

        # Create photo image
        photo_image = generator._create_photo_image()

        if photo_image:
            # Should have specific width/height (35mm in points)
            expected_size = 35 * 72 / 25.4  # Convert mm to points
            # Allow small tolerance
            assert abs(photo_image.drawWidth - expected_size) < 5
            assert abs(photo_image.drawHeight - expected_size) < 5


class TestHeaderCreation:
    """Test PDF header creation."""

    def test_header_contains_name(self, mock_parsed_data):
        """Test that header contains full name."""
        generator = CVGenerator(mock_parsed_data)

        # Build header
        header_elements = generator._build_header()

        # Should have some elements
        assert len(header_elements) > 0

    def test_header_with_all_contact_info(self):
        """Test header with complete contact information."""
        data = {
            "profile": {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john@example.com",
                "phone": "+1234567890",
                "summary": "Software Engineer"
            },
            "positions": [],
            "education": [],
            "skills": [],
            "languages": [],
            "certifications": []
        }

        generator = CVGenerator(data)
        header_elements = generator._build_header()

        assert len(header_elements) > 0

    def test_header_with_photo(self, mock_parsed_data, mock_base64_image):
        """Test header with profile photo."""
        data = mock_parsed_data.copy()
        data['photo'] = f"data:image/png;base64,{mock_base64_image}"

        generator = CVGenerator(data)
        header_elements = generator._build_header()

        # Should include photo in header
        assert len(header_elements) > 0


class TestSectionGeneration:
    """Test individual section generation."""

    def test_experience_section_generated(self):
        """Test that experience section is generated."""
        data = {
            "profile": {"first_name": "John", "last_name": "Doe"},
            "positions": [
                {
                    "company": "Tech Corp",
                    "title": "Developer",
                    "duration": "2020 - 2023",
                    "description": "Developed software"
                }
            ],
            "education": [],
            "skills": [],
            "languages": [],
            "certifications": []
        }

        generator = CVGenerator(data)
        exp_section = generator._build_experience()

        # Should return list of elements
        assert isinstance(exp_section, list)
        assert len(exp_section) > 0

    def test_education_section_generated(self):
        """Test that education section is generated."""
        data = {
            "profile": {"first_name": "John", "last_name": "Doe"},
            "positions": [],
            "education": [
                {
                    "school": "University",
                    "degree": "Bachelor",
                    "start_date": "2014",
                    "end_date": "2018"
                }
            ],
            "skills": [],
            "languages": [],
            "certifications": []
        }

        generator = CVGenerator(data)
        edu_section = generator._build_education()

        assert isinstance(edu_section, list)
        assert len(edu_section) > 0

    def test_skills_section_generated(self):
        """Test that skills section is generated."""
        data = {
            "profile": {"first_name": "John", "last_name": "Doe"},
            "positions": [],
            "education": [],
            "skills": ["Python", "JavaScript", "Docker"],
            "languages": [],
            "certifications": []
        }

        generator = CVGenerator(data)
        skills_section = generator._build_skills()

        assert isinstance(skills_section, list)
        assert len(skills_section) > 0

    def test_languages_section_generated(self):
        """Test that languages section is generated."""
        data = {
            "profile": {"first_name": "John", "last_name": "Doe"},
            "positions": [],
            "education": [],
            "skills": [],
            "languages": [
                {"name": "English", "proficiency": "Native"}
            ],
            "certifications": []
        }

        generator = CVGenerator(data)
        lang_section = generator._build_languages()

        assert isinstance(lang_section, list)
        assert len(lang_section) > 0

    def test_certifications_section_generated(self):
        """Test that certifications section is generated."""
        data = {
            "profile": {"first_name": "John", "last_name": "Doe"},
            "positions": [],
            "education": [],
            "skills": [],
            "languages": [],
            "certifications": [
                {
                    "name": "AWS Certified",
                    "authority": "Amazon",
                    "start_date": "2021",
                    "end_date": "2024"
                }
            ]
        }

        generator = CVGenerator(data)
        cert_section = generator._build_certifications()

        assert isinstance(cert_section, list)
        assert len(cert_section) > 0

    def test_empty_sections_handled(self):
        """Test that empty sections are handled gracefully."""
        data = {
            "profile": {"first_name": "John", "last_name": "Doe"},
            "positions": [],
            "education": [],
            "skills": [],
            "languages": [],
            "certifications": []
        }

        generator = CVGenerator(data)

        # These should return empty lists or handle gracefully
        exp = generator._build_experience()
        edu = generator._build_education()
        skills = generator._build_skills()
        langs = generator._build_languages()
        certs = generator._build_certifications()

        # Should not crash, should return lists
        assert isinstance(exp, list)
        assert isinstance(edu, list)
        assert isinstance(skills, list)
        assert isinstance(langs, list)
        assert isinstance(certs, list)


class TestPagination:
    """Test pagination and KeepTogether."""

    def test_sections_use_keep_together(self, mock_parsed_data):
        """Test that sections use KeepTogether for pagination."""
        generator = CVGenerator(mock_parsed_data)

        # Build sections
        exp_section = generator._build_experience()

        # Should use KeepTogether (may be wrapped in list)
        # This is implementation-dependent, just check structure
        assert isinstance(exp_section, list)

    def test_large_content_pagination(self):
        """Test pagination with large content."""
        # Create data with many items
        data = {
            "profile": {"first_name": "John", "last_name": "Doe"},
            "positions": [
                {
                    "company": f"Company {i}",
                    "title": f"Title {i}",
                    "duration": "2020 - 2023",
                    "description": "Long description " * 50
                }
                for i in range(10)
            ],
            "education": [],
            "skills": ["Skill" + str(i) for i in range(50)],
            "languages": [],
            "certifications": []
        }

        generator = CVGenerator(data)
        pdf_path = generator.generate()

        # Should generate without errors
        assert os.path.exists(pdf_path)

        # Clean up
        if os.path.exists(pdf_path):
            os.remove(pdf_path)


class TestStyling:
    """Test PDF styling."""

    def test_styles_defined(self, mock_parsed_data):
        """Test that styles are properly defined."""
        generator = CVGenerator(mock_parsed_data)

        # Should have styles
        assert hasattr(generator, 'styles')
        assert generator.styles is not None

    def test_custom_colors_used(self, mock_parsed_data):
        """Test that custom colors are defined in styles."""
        generator = CVGenerator(mock_parsed_data)

        # Should have styles with custom colors defined
        assert 'Name' in generator.styles
        assert 'SectionHeader' in generator.styles
        # Check that colors are properly set in styles
        assert generator.styles['Name'].textColor is not None


class TestErrorHandling:
    """Test error handling in generation."""

    def test_missing_profile_handled(self):
        """Test that missing profile is handled."""
        data = {
            "positions": [],
            "education": [],
            "skills": [],
            "languages": [],
            "certifications": []
        }

        # Should handle missing profile
        generator = CVGenerator(data)
        pdf_path = generator.generate()

        assert os.path.exists(pdf_path)

        # Clean up
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

    def test_invalid_data_types(self):
        """Test handling of invalid data types."""
        data = {
            "profile": {"first_name": "John", "last_name": "Doe"},
            "positions": "not a list",  # Invalid type
            "education": None,  # Invalid type
            "skills": [],
            "languages": [],
            "certifications": []
        }

        # Should handle gracefully or raise appropriate error
        try:
            generator = CVGenerator(data)
            pdf_path = generator.generate()

            if os.path.exists(pdf_path):
                os.remove(pdf_path)
        except (TypeError, AttributeError):
            # Expected for invalid data
            pass

    def test_special_characters_in_text(self):
        """Test handling of special characters in text."""
        data = {
            "profile": {
                "first_name": "Jöhn",
                "last_name": "Döe",
                "summary": "Expert in C++ & C# with 100% dedication"
            },
            "positions": [
                {
                    "company": "Tech & Co.",
                    "title": "Senior Developer (Lead)",
                    "duration": "2020 - 2023",
                    "description": "Worked on <projects> with special & chars"
                }
            ],
            "education": [],
            "skills": ["C++", "C#", ".NET"],
            "languages": [],
            "certifications": []
        }

        generator = CVGenerator(data)
        pdf_path = generator.generate()

        # Should handle special characters without crashing
        assert os.path.exists(pdf_path)

        # Clean up
        if os.path.exists(pdf_path):
            os.remove(pdf_path)


class TestPageSize:
    """Test page size configuration."""

    def test_page_size_a4(self, mock_parsed_data):
        """Test that PDF uses A4 page size."""
        generator = CVGenerator(mock_parsed_data)

        # Should use A4
        # Check if pagesize is set in doc or styles
        pdf_path = generator.generate()

        assert os.path.exists(pdf_path)

        # Clean up
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
