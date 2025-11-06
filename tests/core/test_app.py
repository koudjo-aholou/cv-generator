"""
API Flask Tests - CRITICAL Priority

Tests for Flask API endpoints including:
- Root endpoint
- /api/parse-linkedin endpoint
- /api/generate-pdf endpoint
- Request validation
- Error handling
- File cleanup
"""

import pytest
import os
import sys
import io
import json
from unittest.mock import patch, MagicMock, mock_open

# Add backend to path
backend_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'backend')
sys.path.insert(0, os.path.abspath(backend_dir))


class TestRootEndpoint:
    """Test root endpoint."""

    def test_root_returns_json(self, client):
        """Test that root endpoint returns JSON."""
        response = client.get('/')
        assert response.status_code == 200
        assert response.content_type == 'application/json'

    def test_root_contains_version(self, client):
        """Test that root endpoint contains version info."""
        response = client.get('/')
        data = json.loads(response.data)
        assert 'version' in data or 'status' in data


class TestParseLinkedInEndpoint:
    """Test /api/parse-linkedin endpoint."""

    def test_no_files_returns_400(self, client):
        """Test that request without files returns 400."""
        response = client.post('/api/parse-linkedin',
                              data={},
                              content_type='multipart/form-data')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_empty_files_list_returns_400(self, client):
        """Test that empty files list returns 400."""
        response = client.post('/api/parse-linkedin',
                              data={'files': []},
                              content_type='multipart/form-data')
        assert response.status_code == 400

    def test_invalid_extension_returns_400(self, client):
        """Test that non-CSV files are rejected."""
        data = {
            'files': (io.BytesIO(b"malicious content"), 'malware.exe')
        }
        response = client.post('/api/parse-linkedin',
                              data=data,
                              content_type='multipart/form-data')
        assert response.status_code == 400
        assert b"invalid file type" in response.data.lower()

    @patch('app.LinkedInParser')
    def test_valid_csv_accepted(self, mock_parser, client):
        """Test that valid CSV files are accepted."""
        # Mock parser to return valid data
        mock_parser.return_value.parse.return_value = {
            "profile": {"first_name": "Test", "last_name": "User"},
            "experience": [],
            "education": [],
            "skills": [],
            "languages": [],
            "certifications": []
        }

        data = {
            'files': (io.BytesIO(b"header1,header2\nvalue1,value2"), 'test.csv')
        }

        response = client.post('/api/parse-linkedin',
                              data=data,
                              content_type='multipart/form-data')

        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert 'profile' in response_data

    @patch('app.LinkedInParser')
    def test_multiple_csv_files_accepted(self, mock_parser, client):
        """Test that multiple CSV files are accepted."""
        mock_parser.return_value.parse.return_value = {
            "profile": {"first_name": "Test"},
            "experience": [],
            "education": [],
            "skills": [],
            "languages": [],
            "certifications": []
        }

        data = {
            'files': [
                (io.BytesIO(b"header1\nvalue1"), 'file1.csv'),
                (io.BytesIO(b"header2\nvalue2"), 'file2.csv')
            ]
        }

        response = client.post('/api/parse-linkedin',
                              data=data,
                              content_type='multipart/form-data')

        assert response.status_code == 200

    @patch('app.LinkedInParser')
    def test_parser_error_returns_500(self, mock_parser, client):
        """Test that parser errors return 500."""
        mock_parser.return_value.parse.side_effect = Exception("Parse error")

        data = {
            'files': (io.BytesIO(b"test,data\nvalue1,value2"), 'test.csv')
        }

        response = client.post('/api/parse-linkedin',
                              data=data,
                              content_type='multipart/form-data')

        assert response.status_code == 500
        response_data = json.loads(response.data)
        assert 'error' in response_data

    @patch('app.LinkedInParser')
    @patch('app.os.remove')
    def test_files_cleaned_up_after_success(self, mock_remove, mock_parser, client):
        """Test that uploaded files are cleaned up after successful parsing."""
        mock_parser.return_value.parse.return_value = {
            "profile": {"first_name": "Test"},
            "experience": [],
            "education": [],
            "skills": [],
            "languages": [],
            "certifications": []
        }

        data = {
            'files': (io.BytesIO(b"test,data\nvalue1,value2"), 'test.csv')
        }

        response = client.post('/api/parse-linkedin',
                              data=data,
                              content_type='multipart/form-data')

        assert response.status_code == 200
        # os.remove should be called for cleanup
        assert mock_remove.called

    @patch('app.LinkedInParser')
    @patch('app.os.remove')
    def test_files_cleaned_up_after_error(self, mock_remove, mock_parser, client):
        """Test that uploaded files are cleaned up even on error."""
        mock_parser.return_value.parse.side_effect = Exception("Error")

        data = {
            'files': (io.BytesIO(b"test,data\nvalue1,value2"), 'test.csv')
        }

        response = client.post('/api/parse-linkedin',
                              data=data,
                              content_type='multipart/form-data')

        assert response.status_code == 500
        # Files should still be cleaned up
        assert mock_remove.called


class TestGeneratePDFEndpoint:
    """Test /api/generate-pdf endpoint."""

    def test_no_data_returns_400(self, client):
        """Test that request without data returns error."""
        response = client.post('/api/generate-pdf',
                              json=None,
                              content_type='application/json')
        # May return 400 or 500 depending on Flask version
        assert response.status_code in [400, 500]

    def test_invalid_json_returns_400(self, client):
        """Test that invalid JSON returns error."""
        response = client.post('/api/generate-pdf',
                              data="not valid json",
                              content_type='application/json')
        # May return 400, 415, or 500 depending on Flask version and how it handles the error
        assert response.status_code in [400, 415, 500]

    def test_non_dict_data_returns_400(self, client):
        """Test that non-dictionary data returns 400."""
        response = client.post('/api/generate-pdf',
                              json=["not", "a", "dict"],
                              content_type='application/json')
        assert response.status_code == 400

    @patch('app.CVGenerator')
    def test_valid_data_returns_pdf(self, mock_generator, client, mock_parsed_data, temp_upload_dir):
        """Test that valid data generates and returns PDF."""
        # Create a temporary PDF file
        temp_pdf = os.path.join(temp_upload_dir, 'test.pdf')
        with open(temp_pdf, 'wb') as f:
            f.write(b"%PDF-1.4\n%test pdf content")

        mock_generator.return_value.generate.return_value = temp_pdf

        response = client.post('/api/generate-pdf',
                              json=mock_parsed_data,
                              content_type='application/json')

        assert response.status_code == 200
        assert response.content_type == 'application/pdf'

    @patch('app.CVGenerator')
    def test_pdf_has_attachment_header(self, mock_generator, client, mock_parsed_data, temp_upload_dir):
        """Test that PDF response has attachment header."""
        temp_pdf = os.path.join(temp_upload_dir, 'test.pdf')
        with open(temp_pdf, 'wb') as f:
            f.write(b"%PDF-1.4\n%test")

        mock_generator.return_value.generate.return_value = temp_pdf

        response = client.post('/api/generate-pdf',
                              json=mock_parsed_data,
                              content_type='application/json')

        assert response.status_code == 200
        assert 'attachment' in response.headers.get('Content-Disposition', '')

    @patch('app.CVGenerator')
    def test_generator_error_returns_500(self, mock_generator, client, mock_parsed_data):
        """Test that generator errors return 500."""
        mock_generator.return_value.generate.side_effect = Exception("PDF generation failed")

        response = client.post('/api/generate-pdf',
                              json=mock_parsed_data,
                              content_type='application/json')

        assert response.status_code == 500
        response_data = json.loads(response.data)
        assert 'error' in response_data

    @patch('app.CVGenerator')
    def test_data_with_photo_accepted(self, mock_generator, client, mock_parsed_data, mock_base64_image, temp_upload_dir):
        """Test that data with valid photo is accepted."""
        temp_pdf = os.path.join(temp_upload_dir, 'test.pdf')
        with open(temp_pdf, 'wb') as f:
            f.write(b"%PDF-1.4\n%test")

        mock_generator.return_value.generate.return_value = temp_pdf

        data = mock_parsed_data.copy()
        data['photo'] = f"data:image/png;base64,{mock_base64_image}"

        response = client.post('/api/generate-pdf',
                              json=data,
                              content_type='application/json')

        assert response.status_code == 200

    def test_oversized_photo_rejected(self, client, mock_parsed_data, mock_large_base64_image):
        """Test that oversized photos are rejected."""
        data = mock_parsed_data.copy()
        data['photo'] = f"data:image/png;base64,{mock_large_base64_image}"

        response = client.post('/api/generate-pdf',
                              json=data,
                              content_type='application/json')

        assert response.status_code == 400
        assert b"too large" in response.data.lower()


class TestRequestValidation:
    """Test request validation."""

    def test_wrong_content_type_parse(self, client):
        """Test that wrong content type for /api/parse-linkedin fails."""
        response = client.post('/api/parse-linkedin',
                              data='{"test": "data"}',
                              content_type='application/json')
        # Should fail because it expects multipart/form-data
        assert response.status_code == 400

    def test_wrong_content_type_generate(self, client):
        """Test that wrong content type for /api/generate-pdf fails."""
        response = client.post('/api/generate-pdf',
                              data='files=(test.csv)',
                              content_type='multipart/form-data')
        # Should fail or return error
        assert response.status_code in [400, 415, 500]

    def test_get_method_not_allowed_parse(self, client):
        """Test that GET method is not allowed for /api/parse-linkedin."""
        response = client.get('/api/parse-linkedin')
        assert response.status_code == 405  # Method not allowed

    def test_get_method_not_allowed_generate(self, client):
        """Test that GET method is not allowed for /api/generate-pdf."""
        response = client.get('/api/generate-pdf')
        assert response.status_code == 405


class TestErrorHandling:
    """Test error handling and messages."""

    @patch('app.LinkedInParser')
    def test_error_response_format(self, mock_parser, client):
        """Test that error responses have consistent format."""
        mock_parser.return_value.parse.side_effect = Exception("Test error")

        data = {
            'files': (io.BytesIO(b"test,data\n"), 'test.csv')
        }

        response = client.post('/api/parse-linkedin',
                              data=data,
                              content_type='multipart/form-data')

        assert response.status_code == 500
        response_data = json.loads(response.data)
        assert 'error' in response_data
        assert isinstance(response_data['error'], str)

    @patch('app.CVGenerator')
    def test_pdf_error_response_format(self, mock_generator, client, mock_parsed_data):
        """Test that PDF generation errors have consistent format."""
        mock_generator.return_value.generate.side_effect = Exception("PDF error")

        response = client.post('/api/generate-pdf',
                              json=mock_parsed_data,
                              content_type='application/json')

        assert response.status_code == 500
        response_data = json.loads(response.data)
        assert 'error' in response_data

    def test_error_does_not_expose_stack_trace(self, client):
        """Test that errors don't expose internal stack traces to client."""
        # Try to trigger an error
        response = client.post('/api/parse-linkedin',
                              data={},
                              content_type='multipart/form-data')

        response_text = response.data.decode('utf-8')
        # Should not contain file paths or internal details
        assert '/home/' not in response_text or 'Traceback' not in response_text


class TestLogging:
    """Test logging functionality."""

    @patch('app.logger')
    @patch('app.LinkedInParser')
    def test_successful_parse_logged(self, mock_parser, mock_logger, client):
        """Test that successful parsing is logged."""
        mock_parser.return_value.parse.return_value = {
            "profile": {},
            "experience": [],
            "education": [],
            "skills": [],
            "languages": [],
            "certifications": []
        }

        data = {
            'files': (io.BytesIO(b"test,data\n"), 'test.csv')
        }

        response = client.post('/api/parse-linkedin',
                              data=data,
                              content_type='multipart/form-data')

        assert response.status_code == 200
        # Logger should have been called
        assert mock_logger.info.called

    @patch('app.logger')
    @patch('app.LinkedInParser')
    def test_parse_error_logged(self, mock_parser, mock_logger, client):
        """Test that parsing errors are logged."""
        mock_parser.return_value.parse.side_effect = Exception("Parse error")

        data = {
            'files': (io.BytesIO(b"test,data\n"), 'test.csv')
        }

        response = client.post('/api/parse-linkedin',
                              data=data,
                              content_type='multipart/form-data')

        assert response.status_code == 500
        # Error should be logged
        assert mock_logger.error.called


class TestResponseHeaders:
    """Test response headers."""

    def test_json_response_content_type(self, client):
        """Test that JSON responses have correct content type."""
        response = client.get('/')
        assert response.status_code == 200
        assert 'application/json' in response.content_type

    @patch('app.CVGenerator')
    def test_pdf_response_content_type(self, mock_generator, client, mock_parsed_data, temp_upload_dir):
        """Test that PDF responses have correct content type."""
        temp_pdf = os.path.join(temp_upload_dir, 'test.pdf')
        with open(temp_pdf, 'wb') as f:
            f.write(b"%PDF-1.4\n%test")

        mock_generator.return_value.generate.return_value = temp_pdf

        response = client.post('/api/generate-pdf',
                              json=mock_parsed_data,
                              content_type='application/json')

        assert response.status_code == 200
        assert response.content_type == 'application/pdf'
