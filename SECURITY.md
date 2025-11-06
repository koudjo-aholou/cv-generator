# Security Documentation

## Overview

This document describes the security measures implemented in the CV Generator application.

## Security Features

### 1. Path Traversal Prevention

**Issue**: Attackers could upload files with malicious names like `../../../etc/passwd` to access/overwrite system files.

**Solution**:
- Use `werkzeug.utils.secure_filename()` to sanitize filenames
- Generate unique UUIDs for each file to prevent collisions
- Store files only in designated temporary directory

**Implementation**:
```python
def get_secure_filepath(original_filename):
    secured_name = secure_filename(original_filename)
    unique_id = uuid.uuid4().hex
    extension = secured_name.rsplit('.', 1)[1].lower()
    safe_filename = f"{unique_id}.{extension}"
    return os.path.join(UPLOAD_FOLDER, safe_filename)
```

### 2. File Upload Validation

**Protections**:
- File type validation (CSV only)
- Individual file size limit: 10MB
- Total upload size limit: 50MB
- Maximum number of files: 20
- Extension whitelist: `.csv`

**Why**: Prevents DoS attacks through massive file uploads and ensures only valid data is processed.

### 3. Image Upload Validation

**Protections**:
- Image size limit: 5MB
- Base64 size validation before decoding
- Format validation (JPEG, PNG)
- Automatic cleanup of processed images

### 4. Debug Mode Configuration

**Security Risk**: Running Flask with `debug=True` in production exposes:
- Detailed error messages with stack traces
- Interactive debugger accessible remotely
- Source code paths

**Solution**:
- Debug mode disabled by default
- Controlled via environment variable `FLASK_DEBUG`
- Warning logged if debug mode is enabled

### 5. Network Binding

**Issue**: Binding to `0.0.0.0` exposes the service to all network interfaces.

**Solution**:
- Default binding to `127.0.0.1` (localhost only)
- Configurable via `FLASK_HOST` environment variable
- Documented in `.env.example`

### 6. CORS Configuration

**Issue**: Unrestricted CORS allows any origin to access the API.

**Solution**:
```python
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:*", "http://127.0.0.1:*", "file://*"],
        "methods": ["GET", "POST"],
        "allow_headers": ["Content-Type"]
    }
})
```

- Restricted to localhost origins only
- Limited HTTP methods
- Specific header allowlist

### 7. Temporary File Cleanup

**Protection**:
- `finally` blocks ensure cleanup even on errors
- Files deleted immediately after processing
- Logging of cleanup failures for monitoring

**Implementation**:
```python
try:
    # Process files
    pass
finally:
    # Always clean up
    for filepath in saved_files:
        if os.path.exists(filepath):
            os.remove(filepath)
```

### 8. Input Validation

**Protections**:
- JSON structure validation
- Data type checking
- Size limits enforced before processing
- Descriptive error messages (not exposing internals)

### 9. Logging

**Security Logging**:
- All uploads logged with filenames
- Errors logged with stack traces (server-side only)
- No sensitive data in client-facing error messages
- Separate logging levels for development/production

## Configuration

### Environment Variables

Create a `.env` file (never commit this):

```bash
FLASK_DEBUG=False
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
```

### Production Deployment

For production deployment:

1. **Never enable debug mode**:
   ```bash
   FLASK_DEBUG=False
   ```

2. **Use a production WSGI server** (not Flask development server):
   ```bash
   gunicorn -w 4 -b 127.0.0.1:5000 app:app
   ```

3. **Use reverse proxy** (nginx, Apache):
   - Handles SSL/TLS
   - Rate limiting
   - DDoS protection

4. **Set up firewall rules**:
   - Block external access to application port
   - Allow only reverse proxy access

5. **Regular updates**:
   - Keep dependencies updated
   - Monitor security advisories

## Threat Model

### Threats Mitigated

| Threat | Mitigation | Status |
|--------|------------|--------|
| Path Traversal | Secure filename + UUID | ✅ Fixed |
| Large File DoS | Size limits | ✅ Fixed |
| Arbitrary File Upload | Extension whitelist | ✅ Fixed |
| Memory Exhaustion | Size validation | ✅ Fixed |
| Information Disclosure | Debug mode off | ✅ Fixed |
| CORS Abuse | Origin restrictions | ✅ Fixed |
| Temp File Accumulation | Guaranteed cleanup | ✅ Fixed |

### Remaining Considerations

1. **CSV Injection**: Not currently validated (low risk for local use)
2. **Rate Limiting**: Not implemented (consider for public deployment)
3. **Authentication**: None (appropriate for local use only)
4. **HTTPS**: Not configured (use reverse proxy in production)

## Security Best Practices

### For Users

1. **Run locally only** - Do not expose to public internet
2. **Keep dependencies updated**: `pip install --upgrade -r requirements.txt`
3. **Review uploaded files** - Only upload your own LinkedIn exports
4. **Clear browser cache** - After processing sensitive data

### For Developers

1. **Never commit** `.env` files
2. **Validate all inputs** from users
3. **Log security events** appropriately
4. **Review dependencies** for known vulnerabilities
5. **Test with malicious inputs** during development

## Reporting Security Issues

If you discover a security vulnerability:

1. **Do NOT** open a public issue
2. Report via email to maintainers
3. Provide detailed description
4. Allow time for fix before disclosure

## Changelog

- **2024-11-06**: Initial security hardening
  - Fixed path traversal vulnerability
  - Added file validation
  - Secured Flask configuration
  - Implemented CORS restrictions
  - Added comprehensive logging

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Flask Security Best Practices](https://flask.palletsprojects.com/en/latest/security/)
- [Werkzeug Security Utilities](https://werkzeug.palletsprojects.com/en/latest/utils/#module-werkzeug.security)
