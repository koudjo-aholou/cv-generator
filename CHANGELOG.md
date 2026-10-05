# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.1.0] - 2024-11-06

### 🔒 Security - CRITICAL FIXES

#### Fixed
- **Path Traversal Vulnerability** - Prevented malicious file uploads with path traversal attempts
  - Now using `secure_filename()` and UUID generation
  - Files stored with random names to prevent collisions and attacks

- **Debug Mode Exposure** - Disabled debug mode by default
  - Controlled via `FLASK_DEBUG` environment variable
  - Warning logged if debug mode is enabled
  - Changed default binding from `0.0.0.0` to `127.0.0.1` (localhost only)

- **CORS Misconfiguration** - Restricted CORS to localhost origins only
  - Previously: Any origin could access the API
  - Now: Only localhost and file:// origins allowed

- **File Upload Validation** - Added comprehensive upload security
  - File type validation (CSV only)
  - File size limits (10MB per file, 50MB total)
  - Maximum file count (20 files)
  - Extension whitelist enforcement

- **Image Upload Validation** - Added photo size and format checks
  - Maximum 5MB for profile photos
  - Base64 size validation before decoding
  - Prevents DoS through huge image uploads

#### Added
- **Comprehensive Logging** - Production-grade logging system
  - All file operations logged
  - Error tracking with stack traces (server-side only)
  - Security events logged

- **Guaranteed Cleanup** - Files always deleted after processing
  - `finally` blocks ensure cleanup on errors
  - Logging of cleanup failures

- **Environment Configuration** - Production-safe configuration
  - `.env.example` file with documentation
  - `FLASK_DEBUG`, `FLASK_HOST`, `FLASK_PORT` variables
  - Sensible defaults for security

- **Security Documentation** - Complete security guide
  - `SECURITY.md` file added
  - Threat model documentation
  - Production deployment guidelines
  - Security best practices

### 🐛 Bug Fixes

#### Fixed
- **Photo Mode Detection Bug** - Fixed PNG transparency handling
  - Proper conversion of P and LA modes to RGBA
  - Correct alpha mask application
  - Better error handling for image modes

- **Photo Error Handling Bug** - Fixed layout breaking on photo errors
  - Returns `None` instead of empty Paragraph
  - Graceful fallback to no-photo layout
  - Added proper logging for photo errors

- **Function Naming Bug** - Renamed misleading function
  - `_calculate_duration()` → `_format_date_range()`
  - Function only formats, doesn't calculate
  - Updated docstring for clarity
  - Changed bare `except:` to `except Exception:`

### 📝 Documentation

#### Added
- Section on security in README.md
- SECURITY.md with comprehensive security documentation
- CHANGELOG.md (this file)
- .env.example with configuration examples

#### Changed
- Updated README with security warnings
- Added security features to feature list

### 🔧 Technical Improvements

#### Changed
- Refactored `app.py` with security-first approach
- Added helper functions for file validation
- Improved error messages (descriptive without exposing internals)
- Better structured code with clear separation of concerns

### 📦 Dependencies

No new dependencies required. All security features use existing libraries:
- `werkzeug.utils.secure_filename` (already included with Flask)
- `uuid` (Python standard library)
- `logging` (Python standard library)

## [1.0.0] - 2024-11-05

### 🎉 Initial Release

#### Added
- LinkedIn CSV parsing
- PDF CV generation with ReportLab
- Modern responsive web interface
- Profile photo support
- Mock data for testing (Muhammad Avdol)
- Multiple sections: Experience, Education, Skills, Languages, Certifications
- French language support
- Start scripts for Linux/Mac and Windows

#### Features
- No database - privacy-focused design
- In-memory processing only
- Automatic temporary file cleanup
- Drag & drop file upload
- Photo crop and resize to square
- Multiple CV sections with KeepTogether pagination

---

## Migration Guide

### Upgrading to 1.1.0

No breaking changes. The application works the same way for users, but with added security.

#### For Developers

If you were running with custom configurations:

1. **Environment Variables**: Create a `.env` file (optional):
   ```bash
   FLASK_DEBUG=False
   FLASK_HOST=127.0.0.1
   FLASK_PORT=5000
   ```

2. **Host Binding**: If you need to bind to `0.0.0.0`:
   ```bash
   FLASK_HOST=0.0.0.0 python app.py
   ```
   ⚠️ Only use this on trusted networks

3. **Debug Mode**: Only enable for development:
   ```bash
   FLASK_DEBUG=True python app.py
   ```

#### For Users

No changes required. The application works exactly the same way, just more securely.

---

## Security Advisories

### [CVE-2024-XXXX] - Path Traversal (Fixed in 1.1.0)

**Severity**: Critical
**Status**: Fixed

**Description**: Previous versions allowed arbitrary file uploads with path traversal, potentially allowing attackers to overwrite system files.

**Affected Versions**: 1.0.0
**Fixed in**: 1.1.0

**Mitigation**: Upgrade to 1.1.0 immediately if running older versions.

---

## Contributors

- Initial development and security hardening

## Links

- [Repository](https://github.com/yourusername/cv-generator)
- [Security Policy](SECURITY.md)
- [README](README.md)
