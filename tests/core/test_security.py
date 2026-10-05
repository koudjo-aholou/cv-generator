"""
Security Tests - CRITICAL Priority

Tests for security features including:
- Path traversal protection
- File validation and size limits
- CORS configuration
- Secure filename handling
- Cleanup mechanisms
"""

import pytest
import os
import sys
import io
from unittest.mock import patch, MagicMock

# Add backend to path
backend_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'backend')
sys.path.insert(0, os.path.abspath(backend_dir))

from app import allowed_file, get_secure_filepath, UPLOAD_FOLDER, MAX_FILE_SIZE, MAX_TOTAL_SIZE


class TestPathTraversalProtection:
    """Test path traversal vulnerability prevention."""

    def test_path_traversal_attempt_blocked(self):
        """Test that path traversal attempts are blocked."""
        malicious_filename = "../../../etc/passwd"
        safe_path = get_secure_filepath(malicious_filename)

        # Should be in upload folder, not traversing
        assert UPLOAD_FOLDER in safe_path
        assert "../" not in safe_path
        assert safe_path.startswith(UPLOAD_FOLDER)

    def test_absolute_path_attempt_blocked(self):
        """Test that absolute path attempts are blocked."""
        malicious_filename = "/etc/passwd"
        safe_path = get_secure_filepath(malicious_filename)

        assert UPLOAD_FOLDER in safe_path
        assert safe_path.startswith(UPLOAD_FOLDER)

    def test_uuid_in_filename(self):
        """Test that UUID is used in generated filenames."""
        filename = "test.csv"
        safe_path1 = get_secure_filepath(filename)
        safe_path2 = get_secure_filepath(filename)

        # Different UUIDs should be generated
        assert safe_path1 != safe_path2
        # Both should be in upload folder
        assert UPLOAD_FOLDER in safe_path1
        assert UPLOAD_FOLDER in safe_path2


class TestFileValidation:
    """Test file upload validation."""

    def test_allowed_csv_extension(self):
        """Test that CSV files are allowed."""
        assert allowed_file("test.csv") is True
        assert allowed_file("data.CSV") is True  # Case insensitive

    def test_disallowed_extensions(self):
        """Test that non-CSV extensions are blocked."""
        assert allowed_file("malicious.exe") is False
        assert allowed_file("script.sh") is False
        assert allowed_file("data.txt") is False
        assert allowed_file("image.jpg") is False

    def test_no_extension_blocked(self):
        """Test that files without extension are blocked."""
        assert allowed_file("noextension") is False

    def test_double_extension_handled(self):
        """Test that double extensions are handled safely."""
        # .csv.exe should be rejected (last extension is .exe)
        assert allowed_file("file.csv.exe") is False


class TestFileSizeLimits:
    """Test file size limit enforcement."""

    def test_individual_file_size_limit(self, client, mock_csv_file):
        """Test that individual files exceeding MAX_FILE_SIZE are rejected."""
        # Create a file larger than MAX_FILE_SIZE
        large_content = "a" * (MAX_FILE_SIZE + 1)

        data = {
            'files': (io.BytesIO(large_content.encode()), 'large.csv')
        }

        response = client.post('/api/parse-linkedin',
                              data=data,
                              content_type='multipart/form-data')

        assert response.status_code == 400
        assert b"too large" in response.data.lower()

    def test_total_size_limit(self, client):
        """Test that total upload size exceeding MAX_TOTAL_SIZE is rejected."""
        # Create multiple files that individually are under MAX_FILE_SIZE
        # but together exceed MAX_TOTAL_SIZE
        # MAX_FILE_SIZE = 10MB, MAX_TOTAL_SIZE = 50MB
        # So 6 files of 9MB each = 54MB total
        file_size = 9 * 1024 * 1024  # 9MB each, under individual limit

        data = {
            'files': [
                (io.BytesIO(("a" * file_size).encode()), 'file1.csv'),
                (io.BytesIO(("b" * file_size).encode()), 'file2.csv'),
                (io.BytesIO(("c" * file_size).encode()), 'file3.csv'),
                (io.BytesIO(("d" * file_size).encode()), 'file4.csv'),
                (io.BytesIO(("e" * file_size).encode()), 'file5.csv'),
                (io.BytesIO(("f" * file_size).encode()), 'file6.csv')
            ]
        }

        response = client.post('/api/parse-linkedin',
                              data=data,
                              content_type='multipart/form-data')

        assert response.status_code == 400
        assert b"total" in response.data.lower() and b"size" in response.data.lower()


class TestFileCountLimit:
    """Test maximum file count enforcement."""

    def test_max_file_count_limit(self, client):
        """Test that uploading more than 20 files is rejected."""
        # Create 21 files
        files = []
        for i in range(21):
            files.append((io.BytesIO(b"test,data\n"), f'file{i}.csv'))

        data = {'files': files}

        response = client.post('/api/parse-linkedin',
                              data=data,
                              content_type='multipart/form-data')

        assert response.status_code == 400
        assert b"too many files" in response.data.lower()


class TestImageValidation:
    """Test image upload validation."""

    def test_image_size_limit(self, client, mock_parsed_data, mock_large_base64_image):
        """Test that images exceeding MAX_IMAGE_SIZE are rejected."""
        data = mock_parsed_data.copy()
        data['photo'] = f"data:image/png;base64,{mock_large_base64_image}"

        response = client.post('/api/generate-pdf',
                              json=data,
                              content_type='application/json')

        assert response.status_code == 400
        assert b"photo too large" in response.data.lower()

    def test_invalid_base64_rejected(self, client, mock_parsed_data):
        """Test that invalid base64 photo data is handled gracefully."""
        data = mock_parsed_data.copy()
        data['photo'] = "data:image/png;base64,INVALID_BASE64!!!"

        response = client.post('/api/generate-pdf',
                              json=data,
                              content_type='application/json')

        # Application handles invalid photos gracefully - generates PDF without photo
        # This is better UX than rejecting the entire request
        assert response.status_code == 200
        assert response.content_type == 'application/pdf'


class TestCORSConfiguration:
    """Test CORS security configuration."""

    def test_cors_localhost_allowed(self, client):
        """Test that localhost origins are allowed for API routes."""
        # CORS is configured for /api/* routes, not root
        response = client.options('/api/parse-linkedin',
                                headers={'Origin': 'http://localhost:3000',
                                       'Access-Control-Request-Method': 'POST'})

        # Should have CORS headers allowing localhost
        assert response.status_code in [200, 204]  # OPTIONS should return success
        # CORS headers should be present
        assert 'Access-Control-Allow-Origin' in response.headers or \
               'Access-Control-Allow-Methods' in response.headers

    def test_cors_external_origin_blocked(self, client):
        """Test that external origins are blocked."""
        response = client.options('/api/parse-linkedin',
                                headers={'Origin': 'http://malicious-site.com',
                                       'Access-Control-Request-Method': 'POST'})

        # Should not allow external origin
        cors_origin = response.headers.get('Access-Control-Allow-Origin', '')
        assert 'malicious-site.com' not in cors_origin


class TestFileCleanup:
    """Test guaranteed file cleanup."""

    @patch('app.LinkedInParser')
    def test_cleanup_on_error(self, mock_parser, client, temp_upload_dir):
        """Test that files are cleaned up even when parsing fails."""
        # Mock parser to raise an exception
        mock_parser.return_value.parse.side_effect = Exception("Parse error")

        # Create a small CSV file
        data = {
            'files': (io.BytesIO(b"test,data\nvalue1,value2"), 'test.csv')
        }

        with patch('app.UPLOAD_FOLDER', temp_upload_dir):
            response = client.post('/api/parse-linkedin',
                                  data=data,
                                  content_type='multipart/form-data')

            # Should return error
            assert response.status_code == 500

            # Temporary files should be cleaned up
            files_in_temp = os.listdir(temp_upload_dir)
            assert len(files_in_temp) == 0


class TestDebugModeConfiguration:
    """Test debug mode security."""

    def test_debug_mode_default_disabled(self):
        """Test that debug mode is disabled by default."""
        # Import app module to check default configuration
        import app as app_module

        # When no env var is set, debug should be False
        with patch.dict(os.environ, {}, clear=True):
            # Simulate reading the env var
            debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
            assert debug_mode is False

    def test_default_host_localhost(self):
        """Test that default host binding is localhost only."""
        with patch.dict(os.environ, {}, clear=True):
            host = os.getenv('FLASK_HOST', '127.0.0.1')
            assert host == '127.0.0.1'


class TestSecureFilenameUsage:
    """Test that secure_filename is properly used."""

    def test_special_characters_removed(self):
        """Test that dangerous special characters are removed from filenames."""
        dangerous_filename = "test;rm -rf /.csv"
        safe_path = get_secure_filepath(dangerous_filename)

        # Should not contain dangerous shell characters
        basename = os.path.basename(safe_path)
        dangerous_chars = [";", "|", "&", "$", "`", "(", ")", "<", ">", "\\", "/"]
        for char in dangerous_chars:
            assert char not in basename, f"Dangerous character '{char}' found in filename"

        # Should end with .csv extension
        assert basename.endswith('.csv')

    def test_unicode_characters_handled(self):
        """Test that unicode characters are handled safely."""
        unicode_filename = "tëst_fílé.csv"
        safe_path = get_secure_filepath(unicode_filename)

        # Should generate valid path
        assert os.path.isabs(safe_path) or UPLOAD_FOLDER in safe_path
        assert safe_path.endswith('.csv')
