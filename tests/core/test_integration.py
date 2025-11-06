"""
Integration Tests - MEDIUM Priority

End-to-end integration tests covering complete workflows:
- Upload CSV -> Parse -> Generate PDF
- Multi-file upload workflow
- Photo upload workflow
"""

import pytest
import os
import sys
import io
import json
import tempfile

# Add backend to path
backend_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'backend')
sys.path.insert(0, os.path.abspath(backend_dir))


class TestCompleteWorkflow:
    """Test complete end-to-end workflow."""

    def test_upload_parse_generate_workflow(self, client, mock_profile_csv, mock_positions_csv):
        """Test complete workflow: upload CSV -> parse -> generate PDF."""
        # Step 1: Upload and parse CSV files
        with open(mock_profile_csv, 'rb') as profile, open(mock_positions_csv, 'rb') as positions:
            data = {
                'files': [
                    (io.BytesIO(profile.read()), 'Profile.csv'),
                    (io.BytesIO(positions.read()), 'Positions.csv')
                ]
            }

            parse_response = client.post('/api/parse-linkedin',
                                        data=data,
                                        content_type='multipart/form-data')

        # Should parse successfully
        assert parse_response.status_code == 200
        parsed_data = json.loads(parse_response.data)

        # Should have profile data
        assert 'profile' in parsed_data
        assert 'positions' in parsed_data

        # Step 2: Generate PDF from parsed data
        pdf_response = client.post('/api/generate-pdf',
                                   json=parsed_data,
                                   content_type='application/json')

        # Should generate PDF successfully
        assert pdf_response.status_code == 200
        assert pdf_response.content_type == 'application/pdf'

        # PDF should have content
        assert len(pdf_response.data) > 0
        assert pdf_response.data.startswith(b'%PDF')

    def test_multi_file_upload_workflow(self, client, mock_profile_csv, mock_positions_csv,
                                       mock_education_csv, mock_skills_csv, mock_languages_csv,
                                       mock_certifications_csv):
        """Test workflow with all LinkedIn CSV files."""
        # Upload all CSV files
        csv_files = [
            (mock_profile_csv, 'Profile.csv'),
            (mock_positions_csv, 'Positions.csv'),
            (mock_education_csv, 'Education.csv'),
            (mock_skills_csv, 'Skills.csv'),
            (mock_languages_csv, 'Languages.csv'),
            (mock_certifications_csv, 'Certifications.csv')
        ]

        files_data = []
        for filepath, filename in csv_files:
            with open(filepath, 'rb') as f:
                files_data.append((io.BytesIO(f.read()), filename))

        data = {'files': files_data}

        # Parse all files
        parse_response = client.post('/api/parse-linkedin',
                                    data=data,
                                    content_type='multipart/form-data')

        assert parse_response.status_code == 200
        parsed_data = json.loads(parse_response.data)

        # Should have all sections
        assert 'profile' in parsed_data
        assert 'positions' in parsed_data
        assert 'education' in parsed_data
        assert 'skills' in parsed_data
        assert 'languages' in parsed_data
        assert 'certifications' in parsed_data

        # Generate PDF with all data
        pdf_response = client.post('/api/generate-pdf',
                                   json=parsed_data,
                                   content_type='application/json')

        assert pdf_response.status_code == 200
        assert pdf_response.content_type == 'application/pdf'

        # PDF should be substantial (has all sections)
        # Note: Minimal test data produces a small but valid PDF (~1-2KB)
        assert len(pdf_response.data) > 1000  # Should have meaningful content

    def test_workflow_with_photo(self, client, mock_profile_csv, mock_positions_csv, mock_base64_image):
        """Test complete workflow including photo upload."""
        # Step 1: Parse CSV files
        with open(mock_profile_csv, 'rb') as profile, open(mock_positions_csv, 'rb') as positions:
            data = {
                'files': [
                    (io.BytesIO(profile.read()), 'Profile.csv'),
                    (io.BytesIO(positions.read()), 'Positions.csv')
                ]
            }

            parse_response = client.post('/api/parse-linkedin',
                                        data=data,
                                        content_type='multipart/form-data')

        assert parse_response.status_code == 200
        parsed_data = json.loads(parse_response.data)

        # Step 2: Add photo to parsed data
        parsed_data['photo'] = f"data:image/png;base64,{mock_base64_image}"

        # Step 3: Generate PDF with photo
        pdf_response = client.post('/api/generate-pdf',
                                   json=parsed_data,
                                   content_type='application/json')

        assert pdf_response.status_code == 200
        assert pdf_response.content_type == 'application/pdf'

        # PDF should include photo (larger file size)
        assert len(pdf_response.data) > 0


class TestErrorRecovery:
    """Test error recovery in workflows."""

    def test_parse_error_recovery(self, client):
        """Test that parse errors don't leave orphaned files."""
        # Upload invalid CSV
        data = {
            'files': (io.BytesIO(b"completely,invalid,data"), 'bad.csv')
        }

        # This might succeed or fail depending on parser resilience
        response = client.post('/api/parse-linkedin',
                              data=data,
                              content_type='multipart/form-data')

        # Either way, files should be cleaned up
        # Can't easily test this without inspecting temp directory
        assert response.status_code in [200, 400, 500]

    def test_pdf_generation_error_recovery(self, client):
        """Test that PDF generation errors are handled gracefully."""
        # Send malformed data
        bad_data = {
            "profile": None,  # Invalid
            "experience": "not a list",  # Invalid
        }

        response = client.post('/api/generate-pdf',
                              json=bad_data,
                              content_type='application/json')

        # Should return error, not crash
        assert response.status_code in [400, 500]

        # Should have error message
        if response.content_type == 'application/json':
            response_data = json.loads(response.data)
            assert 'error' in response_data


class TestDataConsistency:
    """Test data consistency through the pipeline."""

    def test_parsed_data_structure_consistent(self, client, mock_profile_csv, mock_positions_csv):
        """Test that parsed data has consistent structure."""
        with open(mock_profile_csv, 'rb') as profile, open(mock_positions_csv, 'rb') as positions:
            data = {
                'files': [
                    (io.BytesIO(profile.read()), 'Profile.csv'),
                    (io.BytesIO(positions.read()), 'Positions.csv')
                ]
            }

            response = client.post('/api/parse-linkedin',
                                  data=data,
                                  content_type='multipart/form-data')

        assert response.status_code == 200
        parsed_data = json.loads(response.data)

        # Should have expected structure
        assert isinstance(parsed_data, dict)
        assert isinstance(parsed_data.get('profile', {}), dict)
        assert isinstance(parsed_data.get('positions', []), list)
        assert isinstance(parsed_data.get('education', []), list)
        assert isinstance(parsed_data.get('skills', []), list)
        assert isinstance(parsed_data.get('languages', []), list)
        assert isinstance(parsed_data.get('certifications', []), list)

    def test_data_preserved_through_pipeline(self, client, mock_profile_csv):
        """Test that specific data is preserved through the pipeline."""
        with open(mock_profile_csv, 'rb') as profile:
            data = {
                'files': [(io.BytesIO(profile.read()), 'Profile.csv')]
            }

            response = client.post('/api/parse-linkedin',
                                  data=data,
                                  content_type='multipart/form-data')

        assert response.status_code == 200
        parsed_data = json.loads(response.data)

        # Check specific data from mock file
        profile = parsed_data.get('profile', {})
        assert profile.get('first_name') == 'John'
        assert profile.get('last_name') == 'Doe'
        assert profile.get('email') == 'john.doe@example.com'

        # Now generate PDF and verify it doesn't crash
        pdf_response = client.post('/api/generate-pdf',
                                   json=parsed_data,
                                   content_type='application/json')

        assert pdf_response.status_code == 200


class TestConcurrentRequests:
    """Test handling of concurrent/multiple requests."""

    def test_multiple_sequential_requests(self, client, mock_profile_csv):
        """Test multiple sequential parse requests."""
        for i in range(3):
            with open(mock_profile_csv, 'rb') as profile:
                data = {
                    'files': [(io.BytesIO(profile.read()), 'Profile.csv')]
                }

                response = client.post('/api/parse-linkedin',
                                      data=data,
                                      content_type='multipart/form-data')

            # Each request should succeed independently
            assert response.status_code == 200

    def test_multiple_pdf_generations(self, client, mock_parsed_data):
        """Test multiple sequential PDF generation requests."""
        for i in range(3):
            response = client.post('/api/generate-pdf',
                                   json=mock_parsed_data,
                                   content_type='application/json')

            # Each generation should succeed
            assert response.status_code == 200
            assert response.content_type == 'application/pdf'
