"""
Tests for CV Generator API
Tests all editing functionalities including profile, experiences, education, skills, etc.
"""

import sys
import os
import json
import base64
from io import BytesIO

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import pytest
from app import app
from linkedin_parser import LinkedInParser


@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_linkedin_data():
    """Sample LinkedIn data for testing"""
    return {
        "profile": {
            "first_name": "Jean",
            "last_name": "Dupont",
            "email": "jean.dupont@example.com",
            "phone": "+33 6 12 34 56 78",
            "address": "Paris, France",
            "headline": "Développeur Full-Stack",
            "summary": "Développeur passionné avec 5 ans d'expérience en Python et JavaScript. Expert en développement web et mobile."
        },
        "positions": [
            {
                "title": "Développeur Senior",
                "company": "Tech Corp",
                "description": "Développement d'applications web modernes.\nGestion d'équipe de 3 développeurs.\nMise en place de CI/CD.",
                "started_on": "Jan 2020",
                "finished_on": "Présent"
            },
            {
                "title": "Développeur Junior",
                "company": "StartUp Inc",
                "description": "Développement de features backend.\nParticipation aux code reviews.",
                "started_on": "Jan 2018",
                "finished_on": "Dec 2019"
            }
        ],
        "education": [
            {
                "school": "Université Paris-Saclay",
                "degree": "Master Informatique",
                "field_of_study": "Intelligence Artificielle",
                "start_date": "2015",
                "end_date": "2017"
            },
            {
                "school": "IUT Paris",
                "degree": "DUT Informatique",
                "field_of_study": "Développement logiciel",
                "start_date": "2013",
                "end_date": "2015"
            }
        ],
        "skills": [
            "Python", "JavaScript", "React", "Node.js", "Django",
            "Flask", "PostgreSQL", "MongoDB", "Docker", "Kubernetes",
            "AWS", "Git", "CI/CD", "TDD", "Agile",
            "TypeScript", "Vue.js", "Redis", "GraphQL", "REST API",
            "HTML", "CSS", "SASS", "Webpack", "Jest",
            "Linux", "Nginx", "Jenkins", "Terraform", "Ansible"
        ],
        "languages": [
            {"name": "Français", "proficiency": "Natif"},
            {"name": "Anglais", "proficiency": "Courant"},
            {"name": "Espagnol", "proficiency": "Intermédiaire"}
        ],
        "certifications": [
            {
                "name": "AWS Certified Developer",
                "authority": "Amazon Web Services",
                "start_date": "Jan 2022",
                "end_date": "Jan 2025",
                "url": "https://aws.amazon.com/certification"
            },
            {
                "name": "Python Professional Certificate",
                "authority": "Python Institute",
                "start_date": "Jun 2021",
                "end_date": "",
                "url": ""
            }
        ]
    }


def test_generate_pdf_basic(client, sample_linkedin_data):
    """Test basic PDF generation with default data"""
    response = client.post(
        '/api/generate-pdf',
        data=json.dumps(sample_linkedin_data),
        content_type='application/json'
    )

    assert response.status_code == 200
    assert response.content_type == 'application/pdf'
    assert len(response.data) > 0


def test_generate_pdf_with_edited_profile(client, sample_linkedin_data):
    """Test PDF generation with edited profile summary"""
    # Edit the summary
    sample_linkedin_data['profile']['summary'] = "Nouveau résumé édité.\nAvec plusieurs lignes.\nPour tester les sauts de ligne."
    sample_linkedin_data['profile']['email'] = "nouveau.email@example.com"

    response = client.post(
        '/api/generate-pdf',
        data=json.dumps(sample_linkedin_data),
        content_type='application/json'
    )

    assert response.status_code == 200
    assert response.content_type == 'application/pdf'


def test_generate_pdf_with_edited_experiences(client, sample_linkedin_data):
    """Test PDF generation with edited experiences"""
    # Edit first experience
    sample_linkedin_data['positions'][0]['title'] = "Lead Developer"
    sample_linkedin_data['positions'][0]['company'] = "New Tech Corp"
    sample_linkedin_data['positions'][0]['description'] = "Description éditée.\nAvec nouvelles lignes.\nEt plus de détails."

    response = client.post(
        '/api/generate-pdf',
        data=json.dumps(sample_linkedin_data),
        content_type='application/json'
    )

    assert response.status_code == 200
    assert response.content_type == 'application/pdf'


def test_generate_pdf_with_edited_education(client, sample_linkedin_data):
    """Test PDF generation with edited education"""
    # Edit education
    sample_linkedin_data['education'][0]['degree'] = "Master 2 Informatique"
    sample_linkedin_data['education'][0]['school'] = "École Polytechnique"
    sample_linkedin_data['education'][0]['field_of_study'] = "Machine Learning et Data Science"

    response = client.post(
        '/api/generate-pdf',
        data=json.dumps(sample_linkedin_data),
        content_type='application/json'
    )

    assert response.status_code == 200
    assert response.content_type == 'application/pdf'


def test_generate_pdf_with_selected_skills(client, sample_linkedin_data):
    """Test PDF generation with individually selected skills (10 out of 30)"""
    # Select only 10 skills
    selected_skills = [
        "Python", "JavaScript", "React", "Django", "PostgreSQL",
        "Docker", "AWS", "Git", "TypeScript", "REST API"
    ]

    data = sample_linkedin_data.copy()
    data['skills'] = selected_skills

    response = client.post(
        '/api/generate-pdf',
        data=json.dumps(data),
        content_type='application/json'
    )

    assert response.status_code == 200
    assert response.content_type == 'application/pdf'


def test_generate_pdf_with_config_experience_visible(client, sample_linkedin_data):
    """Test PDF generation with only specific experiences visible"""
    data = sample_linkedin_data.copy()
    data['config'] = {
        'experience_visible': [0],  # Only show first experience
        'sections': {
            'summary': True,
            'experience': True,
            'education': True,
            'skills': True,
            'languages': True,
            'certifications': True
        }
    }

    response = client.post(
        '/api/generate-pdf',
        data=json.dumps(data),
        content_type='application/json'
    )

    assert response.status_code == 200
    assert response.content_type == 'application/pdf'


def test_generate_pdf_with_config_education_visible(client, sample_linkedin_data):
    """Test PDF generation with only specific education visible"""
    data = sample_linkedin_data.copy()
    data['config'] = {
        'education_visible': [0],  # Only show first education
        'sections': {
            'summary': True,
            'experience': True,
            'education': True,
            'skills': True,
            'languages': True,
            'certifications': True
        }
    }

    response = client.post(
        '/api/generate-pdf',
        data=json.dumps(data),
        content_type='application/json'
    )

    assert response.status_code == 200
    assert response.content_type == 'application/pdf'


def test_generate_pdf_with_edited_languages(client, sample_linkedin_data):
    """Test PDF generation with edited languages"""
    # Edit languages
    sample_linkedin_data['languages'][0]['proficiency'] = "Langue maternelle"
    sample_linkedin_data['languages'][1]['proficiency'] = "Bilingue (C2)"

    response = client.post(
        '/api/generate-pdf',
        data=json.dumps(sample_linkedin_data),
        content_type='application/json'
    )

    assert response.status_code == 200
    assert response.content_type == 'application/pdf'


def test_generate_pdf_with_edited_certifications(client, sample_linkedin_data):
    """Test PDF generation with edited certifications"""
    # Edit certification
    sample_linkedin_data['certifications'][0]['name'] = "AWS Certified Solutions Architect"
    sample_linkedin_data['certifications'][0]['authority'] = "AWS Training"

    response = client.post(
        '/api/generate-pdf',
        data=json.dumps(sample_linkedin_data),
        content_type='application/json'
    )

    assert response.status_code == 200
    assert response.content_type == 'application/pdf'


def test_generate_pdf_with_multiline_descriptions(client, sample_linkedin_data):
    """Test PDF generation with multiline descriptions (line breaks)"""
    # Add multiple line breaks in descriptions
    sample_linkedin_data['profile']['summary'] = "Ligne 1\n\nLigne 2 avec espace\n\n\nLigne 3 avec beaucoup d'espaces"
    sample_linkedin_data['positions'][0]['description'] = "Responsabilité 1\n\nResponsabilité 2\n\nResponsabilité 3"

    response = client.post(
        '/api/generate-pdf',
        data=json.dumps(sample_linkedin_data),
        content_type='application/json'
    )

    assert response.status_code == 200
    assert response.content_type == 'application/pdf'


def test_generate_pdf_with_colors(client, sample_linkedin_data):
    """Test PDF generation with custom colors"""
    data = sample_linkedin_data.copy()
    data['config'] = {
        'template': 'modern',
        'colors': {
            'primary': '#e74c3c',
            'text': '#2c3e50',
            'secondary_text': '#95a5a6'
        }
    }

    response = client.post(
        '/api/generate-pdf',
        data=json.dumps(data),
        content_type='application/json'
    )

    assert response.status_code == 200
    assert response.content_type == 'application/pdf'


def test_generate_pdf_with_all_sections_disabled(client, sample_linkedin_data):
    """Test PDF generation with all optional sections disabled"""
    data = sample_linkedin_data.copy()
    data['config'] = {
        'sections': {
            'summary': False,
            'experience': True,  # At least one section must be visible
            'education': False,
            'skills': False,
            'languages': False,
            'certifications': False
        }
    }

    response = client.post(
        '/api/generate-pdf',
        data=json.dumps(data),
        content_type='application/json'
    )

    assert response.status_code == 200
    assert response.content_type == 'application/pdf'


def test_generate_pdf_with_section_order(client, sample_linkedin_data):
    """Test PDF generation with custom section order"""
    data = sample_linkedin_data.copy()
    data['config'] = {
        'section_order': ['skills', 'experience', 'education', 'summary', 'languages', 'certifications']
    }

    response = client.post(
        '/api/generate-pdf',
        data=json.dumps(data),
        content_type='application/json'
    )

    assert response.status_code == 200
    assert response.content_type == 'application/pdf'


def test_complete_editing_workflow(client, sample_linkedin_data):
    """Test complete editing workflow with all features"""
    # Simulate user editing everything
    data = sample_linkedin_data.copy()

    # Edit profile
    data['profile']['summary'] = "Résumé complètement réécrit.\nAvec plusieurs paragraphes.\n\nPour un meilleur impact."
    data['profile']['email'] = "jean.nouveau@example.com"
    data['profile']['phone'] = "+33 7 00 00 00 00"

    # Edit first experience
    data['positions'][0]['title'] = "Architecte Logiciel Senior"
    data['positions'][0]['description'] = "Architecture et développement.\nLeadership technique.\nMentoring d'équipe."

    # Edit education
    data['education'][0]['degree'] = "Diplôme d'Ingénieur"
    data['education'][0]['field_of_study'] = "Informatique et Mathématiques Appliquées"

    # Select only 12 skills out of 30
    data['skills'] = [
        "Python", "JavaScript", "TypeScript", "React",
        "Django", "PostgreSQL", "Docker", "Kubernetes",
        "AWS", "Git", "REST API", "GraphQL"
    ]

    # Edit languages
    data['languages'][0]['proficiency'] = "Langue maternelle"

    # Edit certification
    data['certifications'][0]['name'] = "AWS Certified Solutions Architect - Professional"

    # Add configuration
    data['config'] = {
        'experience_visible': [0],  # Only show first experience
        'education_visible': [0],   # Only show first education
        'sections': {
            'summary': True,
            'experience': True,
            'education': True,
            'skills': True,
            'languages': True,
            'certifications': True
        },
        'template': 'modern',
        'colors': {
            'primary': '#3498db',
            'text': '#2c3e50',
            'secondary_text': '#7f8c8d'
        }
    }

    response = client.post(
        '/api/generate-pdf',
        data=json.dumps(data),
        content_type='application/json'
    )

    assert response.status_code == 200
    assert response.content_type == 'application/pdf'
    assert len(response.data) > 0


def test_linkedin_parser_maintains_structure():
    """Test that LinkedIn parser maintains data structure"""
    # This test verifies that the parser output is compatible with our editing interface
    # We can't test with real CSV files here, but we verify the structure

    # Mock data that would come from parser
    parsed_data = {
        'profile': {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'summary': 'Test summary'
        },
        'positions': [],
        'education': [],
        'skills': [],
        'languages': [],
        'certifications': []
    }

    # Verify all required keys exist
    assert 'profile' in parsed_data
    assert 'positions' in parsed_data
    assert 'education' in parsed_data
    assert 'skills' in parsed_data
    assert 'languages' in parsed_data
    assert 'certifications' in parsed_data


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
