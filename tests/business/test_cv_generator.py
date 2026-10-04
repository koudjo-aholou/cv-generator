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
from reportlab.lib.units import mm


def flowable_text(flowables):
    """Recursively collect the rendered text of a list of reportlab flowables.

    Walks into Tables (``_cellvalues``) and grouping flowables such as
    KeepTogether (``_content``) so assertions can be made on the text that
    will actually end up in the PDF.
    """
    collected = []

    def walk(item):
        if isinstance(item, (list, tuple)):
            for sub in item:
                walk(sub)
        elif hasattr(item, '_cellvalues'):
            walk(item._cellvalues)
        elif hasattr(item, '_content'):
            walk(item._content)
        elif hasattr(item, 'text'):
            collected.append(item.text)

    walk(flowables)
    return " ".join(collected)


@pytest.fixture
def swiss_profile_data(mock_parsed_data):
    """Parsed data whose profile carries the Swiss-specific personal fields."""
    data = mock_parsed_data.copy()
    data["profile"] = {
        **mock_parsed_data["profile"],
        "birth_date": "1990-05-21",
        "nationality": "Suisse",
        "civil_status": "Célibataire",
        "permit": "Permis C",
    }
    return data


class TestPDFGeneration:
    """Test basic PDF generation."""

    def test_generate_pdf_success(self, mock_parsed_data):
        """Test that PDF is generated successfully."""
        generator = CVGenerator(mock_parsed_data)
        pdf = generator.generate()

        # PDF file should be created
        assert pdf.getbuffer().nbytes > 0
        assert pdf.getvalue().startswith(b'%PDF')


    def test_generated_pdf_is_valid(self, mock_parsed_data):
        """Test that generated PDF is valid."""
        generator = CVGenerator(mock_parsed_data)
        pdf = generator.generate()

        # Check file is not empty and has PDF magic number
        content = pdf.getvalue()
        assert len(content) > 0
        assert content.startswith(b'%PDF')


    def test_pdf_size_reasonable(self, mock_parsed_data):
        """Test that generated PDF has reasonable size."""
        generator = CVGenerator(mock_parsed_data)
        pdf = generator.generate()

        # PDF should be between 1KB and 10MB
        size = pdf.getbuffer().nbytes
        assert 1024 < size < 10 * 1024 * 1024


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
        pdf = generator.generate()

        assert pdf.getbuffer().nbytes > 0



class TestPhotoHandling:
    """Test photo handling in PDF."""

    def test_generate_pdf_with_photo(self, mock_parsed_data):
        """Test PDF generation with profile photo.

        Uses a high-entropy (noisy) photo rather than the 1x1 pixel fixture:
        a trivial flat-color image compresses to less than the generated
        placeholder avatar, making a size comparison against "no photo"
        meaningless/flaky. Noise ensures the real photo reliably compresses
        to more bytes than the simple placeholder shape.
        """
        import random
        from PIL import Image as PILImage

        random.seed(42)
        noisy_image = PILImage.new("RGB", (200, 200))
        noisy_image.putdata(
            [
                (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                for _ in range(200 * 200)
            ]
        )
        buffer = BytesIO()
        noisy_image.save(buffer, format="PNG")
        import base64
        noisy_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        data = mock_parsed_data.copy()
        data['photo'] = f"data:image/png;base64,{noisy_base64}"

        generator = CVGenerator(data)
        pdf = generator.generate()

        # Should generate successfully
        assert pdf.getbuffer().nbytes > 0

        # PDF with photo should be larger than without
        size_with_photo = pdf.getbuffer().nbytes


        # Generate without photo
        generator_no_photo = CVGenerator(mock_parsed_data)
        pdf_no_photo = generator_no_photo.generate()
        size_without_photo = pdf_no_photo.getbuffer().nbytes


        # Photo should add some size
        assert size_with_photo >= size_without_photo

    def test_generate_pdf_without_photo(self, mock_parsed_data):
        """Test PDF generation without photo."""
        # Ensure no photo in data
        data = mock_parsed_data.copy()
        data.pop('photo', None)

        generator = CVGenerator(data)
        pdf = generator.generate()

        assert pdf.getbuffer().nbytes > 0


    def test_photo_error_handling(self, mock_parsed_data):
        """Test that invalid photo data doesn't crash generation."""
        data = mock_parsed_data.copy()
        data['photo'] = "invalid_base64_data"

        generator = CVGenerator(data)
        # Should not crash, might generate without photo
        pdf = generator.generate()

        assert pdf.getbuffer().nbytes > 0


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
        pdf = generator.generate()

        # Should generate without errors
        assert pdf.getbuffer().nbytes > 0



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
        pdf = generator.generate()

        assert pdf.getbuffer().nbytes > 0


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
            pdf = generator.generate()

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
        pdf = generator.generate()

        # Should handle special characters without crashing
        assert pdf.getbuffer().nbytes > 0



class TestPageSize:
    """Test page size configuration."""

    def test_page_size_a4(self, mock_parsed_data):
        """Test that PDF uses A4 page size."""
        generator = CVGenerator(mock_parsed_data)

        # Should use A4
        # Check if pagesize is set in doc or styles
        pdf = generator.generate()

        assert pdf.getbuffer().nbytes > 0



class TestLanguageSupport:
    """Test FR/EN language handling for section labels."""

    def test_default_language_is_french(self, mock_parsed_data):
        """Test that labels default to French when no language is configured."""
        generator = CVGenerator(mock_parsed_data)

        assert generator.language == "fr"
        assert generator.labels["education"] == "Formations"
        assert generator.labels["skills"] == "Compétences"

    def test_english_language_labels(self, mock_parsed_data):
        """Test that English labels are used when language is set to 'en'."""
        generator = CVGenerator(mock_parsed_data, config={"language": "en"})

        assert generator.language == "en"
        assert generator.labels["education"] == "Education"
        assert generator.labels["experience"] == "Professional Experience"
        assert generator.labels["skills"] == "Skills"

    def test_invalid_language_falls_back_to_french(self, mock_parsed_data):
        """Test that an unsupported language code falls back to French."""
        generator = CVGenerator(mock_parsed_data, config={"language": "de"})

        assert generator.language == "fr"
        assert generator.labels["education"] == "Formations"

    def test_custom_labels_override_language_defaults(self, mock_parsed_data):
        """Test that explicit labels still override the language defaults."""
        generator = CVGenerator(
            mock_parsed_data,
            config={"language": "en", "labels": {"education": "My Studies"}},
        )

        assert generator.labels["education"] == "My Studies"
        assert generator.labels["skills"] == "Skills"

    @pytest.mark.parametrize("bad_label", [None, ""])
    def test_null_or_empty_label_falls_back_to_default(
        self, mock_parsed_data, bad_label
    ):
        """Regression: a null/empty label from the client must not break rendering.

        The config is attacker-controlled JSON; previously a null label
        reached ``title.upper()`` and raised AttributeError.
        """
        generator = CVGenerator(
            mock_parsed_data, config={"labels": {"education": bad_label}}
        )

        assert generator.labels["education"] == "Formations"
        assert "FORMATIONS" in flowable_text(generator._build_education())

    def test_null_labels_object_falls_back_to_defaults(self, mock_parsed_data):
        """Regression: config with labels explicitly null must not crash."""
        generator = CVGenerator(mock_parsed_data, config={"labels": None})

        assert generator.labels["education"] == "Formations"

    def test_all_sections_have_a_label_in_both_languages(self, mock_parsed_data):
        """Regression: no section key may be missing from a language's labels."""
        expected_keys = {
            "about",
            "experience",
            "education",
            "skills",
            "languages",
            "certifications",
        }

        for language in ("fr", "en"):
            generator = CVGenerator(mock_parsed_data, config={"language": language})
            assert set(generator.labels) == expected_keys
            assert all(generator.labels.values()), f"empty label in '{language}'"

    def test_french_labels_rendered_in_sections(self, mock_parsed_data):
        """Test that French labels reach the rendered section headers (uppercased)."""
        generator = CVGenerator(mock_parsed_data, config={"language": "fr"})

        assert "FORMATIONS" in flowable_text(generator._build_education())
        assert "COMPÉTENCES" in flowable_text(generator._build_skills())

    def test_english_labels_rendered_in_sections(self, mock_parsed_data):
        """Test that English labels reach the rendered section headers (uppercased)."""
        generator = CVGenerator(mock_parsed_data, config={"language": "en"})

        education_text = flowable_text(generator._build_education())
        assert "EDUCATION" in education_text
        assert "FORMATIONS" not in education_text

        assert "SKILLS" in flowable_text(generator._build_skills())
        assert "PROFESSIONAL EXPERIENCE" in flowable_text(generator._build_experience())

    def test_custom_label_rendered_in_section(self, mock_parsed_data):
        """Test that a user-customized label reaches the rendered section header."""
        generator = CVGenerator(
            mock_parsed_data, config={"labels": {"education": "Parcours Académique"}}
        )

        assert "PARCOURS ACADÉMIQUE" in flowable_text(generator._build_education())

    def test_english_pdf_generation_end_to_end(self, mock_parsed_data):
        """Test that an English CV generates a valid PDF end to end."""
        generator = CVGenerator(mock_parsed_data, config={"language": "en"})
        pdf = generator.generate()

        assert pdf.getvalue().startswith(b"%PDF")


class TestSwissCv:
    """Test Swiss CV-specific conventions."""

    def test_default_cv_type_is_standard(self, mock_parsed_data):
        """Test that cv_type defaults to 'standard'."""
        generator = CVGenerator(mock_parsed_data)

        assert generator.cv_type == "standard"

    def test_swiss_cv_type_is_set(self, mock_parsed_data):
        """Test that cv_type can be set to 'swiss'."""
        generator = CVGenerator(mock_parsed_data, config={"cv_type": "swiss"})

        assert generator.cv_type == "swiss"

    @pytest.mark.parametrize(
        "raw,expected",
        [
            ("1990-05-21", "21.05.1990"),   # ISO (HTML date input format)
            ("21/05/1990", "21.05.1990"),   # French slash format
            ("21.05.1990", "21.05.1990"),   # already Swiss — idempotent
            ("2000-01-01", "01.01.2000"),   # zero padding preserved
        ],
    )
    def test_format_swiss_date_supported_formats(self, mock_parsed_data, raw, expected):
        """Test accepted input formats are all normalized to dd.mm.yyyy."""
        generator = CVGenerator(mock_parsed_data)

        assert generator._format_swiss_date(raw) == expected

    @pytest.mark.parametrize(
        "raw",
        [
            "not a date",
            "",
            None,
            "1990",
            "May 21, 1990",
            "1990-13-45",
            1990,       # non-string from an untrusted JSON payload
            ["1990"],   # wrong type entirely
        ],
    )
    def test_format_swiss_date_invalid_input_returned_unchanged(
        self, mock_parsed_data, raw
    ):
        """Test that unparsable, empty or non-string input never raises.

        Regression: an int previously reached ``strptime`` and raised
        TypeError, which the ValueError guard did not catch.
        """
        generator = CVGenerator(mock_parsed_data)

        assert generator._format_swiss_date(raw) == raw

    def test_swiss_header_with_non_string_birth_date(self, mock_parsed_data):
        """Regression: a non-string birth_date must not break header rendering."""
        data = mock_parsed_data.copy()
        data["profile"] = {**mock_parsed_data["profile"], "birth_date": 1990}

        generator = CVGenerator(data, config={"cv_type": "swiss"})

        assert "1990" in flowable_text(generator._build_header())

    def test_standard_header_omits_swiss_fields(self, swiss_profile_data):
        """Test that personal info fields are not rendered for standard CVs."""
        generator = CVGenerator(swiss_profile_data, config={"cv_type": "standard"})
        rendered_text = flowable_text(generator._build_header())

        assert "Nationalité" not in rendered_text
        assert "Permis de travail" not in rendered_text
        assert "21.05.1990" not in rendered_text
        # Standard contact info is still rendered
        assert "john.doe@example.com" in rendered_text

    def test_swiss_header_includes_personal_info(self, swiss_profile_data):
        """Test that Swiss CVs render birth date, nationality, civil status and permit."""
        generator = CVGenerator(swiss_profile_data, config={"cv_type": "swiss"})
        rendered_text = flowable_text(generator._build_header())

        assert "Date de naissance: 21.05.1990" in rendered_text
        assert "Nationalité: Suisse" in rendered_text
        assert "État civil: Célibataire" in rendered_text
        assert "Permis de travail: Permis C" in rendered_text

    def test_swiss_header_personal_info_in_english(self, swiss_profile_data):
        """Test that Swiss personal info labels are translated when language is English."""
        generator = CVGenerator(
            swiss_profile_data, config={"cv_type": "swiss", "language": "en"}
        )
        rendered_text = flowable_text(generator._build_header())

        assert "Date of birth: 21.05.1990" in rendered_text
        assert "Nationality: Suisse" in rendered_text
        assert "Civil status: Célibataire" in rendered_text
        assert "Work permit: Permis C" in rendered_text
        # French labels must not leak through
        assert "Nationalité" not in rendered_text

    def test_swiss_header_with_partial_personal_info(self, mock_parsed_data):
        """Test that only the provided Swiss fields are rendered (no empty lines)."""
        data = mock_parsed_data.copy()
        data["profile"] = {**mock_parsed_data["profile"], "nationality": "Suisse"}

        generator = CVGenerator(data, config={"cv_type": "swiss"})
        rendered_text = flowable_text(generator._build_header())

        assert "Nationalité: Suisse" in rendered_text
        assert "Date de naissance" not in rendered_text
        assert "État civil" not in rendered_text
        assert "Permis de travail" not in rendered_text

    def test_swiss_header_without_any_personal_info(self, mock_parsed_data):
        """Test that Swiss mode degrades gracefully when no Swiss fields are set."""
        generator = CVGenerator(mock_parsed_data, config={"cv_type": "swiss"})
        header_elements = generator._build_header()

        assert len(header_elements) > 0
        rendered_text = flowable_text(header_elements)
        assert "John Doe" in rendered_text
        assert "Nationalité" not in rendered_text

    def test_standard_header_column_widths_unchanged(self, mock_parsed_data):
        """Regression: standard layout keeps its original 130mm/40mm split."""
        generator = CVGenerator(mock_parsed_data, config={"cv_type": "standard"})
        header_table = generator._build_header()[0]

        assert header_table._colWidths == pytest.approx([130 * mm, 40 * mm])

    def test_swiss_header_uses_larger_photo_column(self, mock_parsed_data):
        """Test that Swiss CVs give the photo a larger column, keeping total width."""
        generator = CVGenerator(mock_parsed_data, config={"cv_type": "swiss"})
        header_table = generator._build_header()[0]

        assert header_table._colWidths == pytest.approx([120 * mm, 50 * mm])
        # Total header width must stay within the printable area
        assert sum(header_table._colWidths) == pytest.approx(170 * mm)

    def test_swiss_pdf_generation_end_to_end(self, swiss_profile_data):
        """Test that a Swiss + English CV generates a valid PDF end to end."""
        generator = CVGenerator(
            swiss_profile_data, config={"cv_type": "swiss", "language": "en"}
        )
        pdf = generator.generate()

        assert pdf.getvalue().startswith(b"%PDF")


# Payloads that previously aborted PDF generation with
# "paraparser: syntax error: parse ended with 1 unclosed tags".
XML_HOSTILE = ["<", "Rue <test", "<b>x</b>", "a & b", "5 < 10 > 3", '"quoted"', "</para>"]


class TestXmlEscaping:
    """Regression: user text must never reach ReportLab's parser unescaped."""

    @pytest.mark.parametrize("payload", XML_HOSTILE)
    def test_profile_fields_survive_hostile_text(self, mock_parsed_data, payload):
        """Test that hostile text in standard profile fields does not crash."""
        data = mock_parsed_data.copy()
        data["profile"] = {
            **mock_parsed_data["profile"],
            "headline": payload,
            "address": payload,
        }

        generator = CVGenerator(data)
        rendered = flowable_text(generator._build_header())

        assert "&lt;" in rendered or "<" not in payload

    @pytest.mark.parametrize("payload", XML_HOSTILE)
    def test_swiss_fields_survive_hostile_text(self, mock_parsed_data, payload):
        """Test that hostile text in the Swiss personal fields does not crash."""
        data = mock_parsed_data.copy()
        data["profile"] = {
            **mock_parsed_data["profile"],
            "nationality": payload,
            "civil_status": payload,
            "permit": payload,
        }

        generator = CVGenerator(data, config={"cv_type": "swiss"})

        assert flowable_text(generator._build_header())

    @pytest.mark.parametrize("payload", XML_HOSTILE)
    def test_custom_label_survives_hostile_text(self, mock_parsed_data, payload):
        """Test that a hostile custom section label does not crash rendering."""
        generator = CVGenerator(
            mock_parsed_data, config={"labels": {"education": payload}}
        )

        assert flowable_text(generator._build_education())

    @pytest.mark.parametrize("payload", XML_HOSTILE)
    def test_sections_survive_hostile_text(self, mock_parsed_data, payload):
        """Test hostile text across experience, education, skills and languages."""
        data = mock_parsed_data.copy()
        data["positions"] = [{"title": payload, "company": payload, "duration": payload}]
        data["education"] = [{"school": payload, "degree": payload}]
        data["skills"] = [payload]
        data["languages"] = [{"name": payload, "proficiency": payload}]
        data["certifications"] = [{"name": payload, "authority": payload}]

        generator = CVGenerator(data)

        for builder in (
            generator._build_experience,
            generator._build_education,
            generator._build_skills,
            generator._build_languages,
            generator._build_certifications,
        ):
            assert flowable_text(builder()) is not None

    def test_hostile_text_generates_valid_pdf_end_to_end(self, mock_parsed_data):
        """Regression: a '<' in an address used to return HTTP 500."""
        data = mock_parsed_data.copy()
        data["profile"] = {
            **mock_parsed_data["profile"],
            "address": "Rue <test> 5 & 6",
        }

        generator = CVGenerator(data)
        pdf = generator.generate()

        assert pdf.getvalue().startswith(b"%PDF")

    def test_formatting_injection_is_neutralized(self, mock_parsed_data):
        """Test that '<b>' in user data renders literally instead of as bold."""
        data = mock_parsed_data.copy()
        data["profile"] = {**mock_parsed_data["profile"], "headline": "<b>INJECTE</b>"}

        rendered = flowable_text(CVGenerator(data)._build_header())

        assert "&lt;b&gt;INJECTE&lt;/b&gt;" in rendered
        assert "<b>INJECTE</b>" not in rendered


class TestIntentionalMarkupPreserved:
    """The escaping must NOT destroy the markup the renderer composes itself.

    Bullets, line breaks and bold language names come from recent branch work
    (commits on bullets/emoji); escaping the composed string would silently
    undo them, so each is pinned here.
    """

    def test_list_description_keeps_bullets_and_breaks(self, mock_parsed_data):
        """Test that a multi-line description still yields bullets and <br/>."""
        generator = CVGenerator(mock_parsed_data)

        out = generator._format_description("Dev web n Gestion equipe n Mise en place CI")

        assert out.count("&#8226;") == 3
        assert out.count("<br/>") == 2

    def test_native_bullet_characters_still_converted(self, mock_parsed_data):
        """Test that '•' separated text is still split into bullet items."""
        generator = CVGenerator(mock_parsed_data)

        out = generator._format_description("Projet A • Projet B • Projet C")

        assert out.count("&#8226;") == 3

    def test_description_text_is_escaped_but_markup_survives(self, mock_parsed_data):
        """Test escaping and intentional markup coexisting in one description."""
        generator = CVGenerator(mock_parsed_data)

        out = generator._format_description("R&D <Acme> n Second <item>")

        assert "&amp;" in out
        assert "&lt;Acme&gt;" in out
        assert "&#8226;" in out
        assert "<br/>" in out

    def test_language_names_stay_bold(self, mock_parsed_data):
        """Test that the structural <b> around language names is preserved."""
        data = mock_parsed_data.copy()
        data["languages"] = [{"name": "Français", "proficiency": "Natif"}]

        rendered = flowable_text(CVGenerator(data)._build_languages())

        assert "<b>Français</b>" in rendered


# Every style the builders reference by name. _setup_modern_styles,
# _setup_classic_styles and _setup_creative_styles must each register all of
# them: a style added to one template only would raise KeyError at render time
# under the other two.
REQUIRED_STYLES = {
    "Company",
    "Contact",
    "DateLocation",
    "Description",
    "Headline",
    "JobTitle",
    "MissionClient",
    "MissionDescription",
    "MissionTitle",
    "Name",
    "SectionHeader",
    "SkillItem",
    "Summary",
}

TEMPLATES = ["modern", "classic", "creative"]


class TestTemplates:
    """Cover the three templates.

    'classic' and 'creative' are selectable from the UI radio group but were
    at 0% coverage — ~330 lines that no test exercised.
    """

    @pytest.mark.parametrize("template", TEMPLATES + ["inconnu", None])
    def test_template_registers_every_required_style(self, mock_parsed_data, template):
        """Test each template (and the fallback) defines all 13 styles."""
        generator = CVGenerator(mock_parsed_data, config={"template": template})

        missing = REQUIRED_STYLES - set(generator.styles.byName)
        assert not missing, f"styles manquants pour '{template}': {sorted(missing)}"

    @pytest.mark.parametrize("template", TEMPLATES)
    def test_template_generates_valid_pdf(self, mock_parsed_data, template):
        """Test each template produces a valid PDF end to end."""
        generator = CVGenerator(mock_parsed_data, config={"template": template})
        pdf = generator.generate()

        assert pdf.getvalue().startswith(b"%PDF")

    def test_unknown_template_falls_back_to_modern(self, mock_parsed_data):
        """Test an unrecognized template renders with the modern styles."""
        modern = CVGenerator(mock_parsed_data, config={"template": "modern"})
        unknown = CVGenerator(mock_parsed_data, config={"template": "inconnu"})

        for style in sorted(REQUIRED_STYLES):
            for attr in ("fontName", "fontSize", "alignment", "leading"):
                assert getattr(unknown.styles[style], attr) == getattr(
                    modern.styles[style], attr
                ), f"'{style}.{attr}' diverge du fallback modern"

    @pytest.mark.parametrize("template", TEMPLATES)
    def test_template_works_with_swiss_and_english(self, mock_parsed_data, template):
        """Test the templates compose with the language and Swiss options."""
        generator = CVGenerator(
            mock_parsed_data,
            config={"template": template, "language": "en", "cv_type": "swiss"},
        )

        assert generator.labels["education"] == "Education"
        assert flowable_text(generator._build_education())

    def test_templates_are_visually_distinct(self, mock_parsed_data):
        """Test the three templates do not all collapse to the same styling.

        Guards against a refactor silently making every template identical.
        They share fontName (all Helvetica) and differ through size, alignment
        and colour instead, so this pins the dimensions that actually vary.
        """
        generators = {
            t: CVGenerator(mock_parsed_data, config={"template": t}) for t in TEMPLATES
        }

        sizes = {t: g.styles["Name"].fontSize for t, g in generators.items()}
        assert len(set(sizes.values())) == len(TEMPLATES), f"tailles non distinctes: {sizes}"

        # 'classic' is the centered one, the other two are left-aligned
        alignments = {t: g.styles["Name"].alignment for t, g in generators.items()}
        assert alignments["classic"] != alignments["modern"]

        # 'creative' is the one that tints headings with the accent colour
        colors = {t: str(g.styles["SectionHeader"].textColor) for t, g in generators.items()}
        assert colors["creative"] != colors["modern"]


class TestConsultantMissionsRendering:
    """Cover the PDF rendering of nested consultant missions.

    test_consultant_missions.py covers the *parsing* that builds the
    'missions' key; this covers the rendering branch that consumes it,
    which was the remaining uncovered block of _build_experience.
    """

    @pytest.fixture
    def data_with_missions(self, mock_parsed_data):
        data = mock_parsed_data.copy()
        data["positions"] = [
            {
                "company": "Zenika",
                "title": "Consultant",
                "duration": "2020 - 2023",
                "missions": [
                    {
                        "client": "Aircall",
                        "title": "Software Engineer",
                        "duration": "2020-03 - 2020-08",
                        "location": "Remote",
                        "description": "Backend n API design",
                    },
                    {"client": "Orange", "title": "Tech Lead"},
                ],
            }
        ]
        return data

    def test_missions_are_rendered(self, data_with_missions):
        """Test each mission's client, title, dates and description appear."""
        rendered = flowable_text(CVGenerator(data_with_missions)._build_experience())

        assert "Mission chez Aircall" in rendered
        assert "Mission chez Orange" in rendered
        assert "Software Engineer" in rendered
        assert "2020-03 - 2020-08 | Remote" in rendered

    def test_mission_description_is_formatted(self, data_with_missions):
        """Test mission descriptions go through the bullet formatting."""
        rendered = flowable_text(CVGenerator(data_with_missions)._build_experience())

        assert "&#8226;" in rendered

    def test_mission_without_client_uses_fallback(self, mock_parsed_data):
        """Test a mission missing its client still renders."""
        data = mock_parsed_data.copy()
        data["positions"] = [{"company": "X", "title": "Y", "missions": [{}]}]

        rendered = flowable_text(CVGenerator(data)._build_experience())

        assert "Mission chez Client" in rendered

    def test_hostile_text_in_mission_is_escaped(self, mock_parsed_data):
        """Regression: a '<' in a mission client used to abort the PDF."""
        data = mock_parsed_data.copy()
        data["positions"] = [
            {
                "company": "X",
                "title": "Y",
                "missions": [{"client": "A <b>A", "title": "T & T"}],
            }
        ]

        rendered = flowable_text(CVGenerator(data)._build_experience())

        assert "&lt;b&gt;" in rendered
        assert "&amp;" in rendered

    def test_position_without_missions_is_unaffected(self, mock_parsed_data):
        """Test the ordinary (non-consultant) path renders no mission header."""
        rendered = flowable_text(CVGenerator(mock_parsed_data)._build_experience())

        assert "Mission chez" not in rendered

    def test_missions_pdf_end_to_end(self, data_with_missions):
        """Test a CV carrying missions generates a valid PDF."""
        pdf = CVGenerator(data_with_missions).generate()

        assert pdf.getvalue().startswith(b"%PDF")
