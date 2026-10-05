# CV Generator Test Suite

Comprehensive test suite with 103 tests covering security, API, business logic, integration, compatibility, and editing features.

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures and pytest configuration
├── test_api.py              # Editing features tests (15 tests) - CRITICAL
├── test_frontend.html       # Frontend editing tests (24 tests) - HIGH
├── core/                    # Core/Technical tests (44 tests)
│   ├── test_security.py     # Security tests (10 tests) - CRITICAL
│   ├── test_app.py          # Flask API tests (27 tests) - CRITICAL
│   ├── test_integration.py  # Integration tests (3 tests) - MEDIUM
│   └── test_compatibility.py # Compatibility tests (4 tests) - OPTIONAL
└── business/                # Business Logic tests (44 tests)
    ├── test_linkedin_parser.py  # LinkedIn parser (19 tests) - HIGH
    └── test_cv_generator.py     # CV generator (25 tests) - HIGH
```

## Test Categories

### Editing Features Tests (15 tests - CRITICAL)

**Backend Tests (`test_api.py`)**

Tests for all editing functionalities:
- Profile editing (summary, email, phone, address)
- Experience editing (title, company, description, dates)
- Education editing (degree, school, field, dates)
- Skills selection (individual selection, ex: 10 out of 30)
- Languages editing (name, proficiency)
- Certifications editing (name, authority, dates, URL)
- Multiline descriptions (line breaks support)
- Configuration (visibility filters, colors, section order)
- Complete editing workflow

**Running Editing Tests:**
```bash
# Run all editing tests
pytest tests/test_api.py -v

# Run specific editing test
pytest tests/test_api.py::test_generate_pdf_with_selected_skills -v

# Run with coverage
pytest tests/test_api.py --cov=backend --cov-report=html
```

**Frontend Tests (`test_frontend.html`)**

Interactive browser-based tests covering 24 test cases:
- Data structure validation (4 tests)
- Profile editing (3 tests)
- Experience editing (3 tests)
- Education editing (3 tests)
- Skills selection (3 tests)
- Languages editing (2 tests)
- Certifications editing (2 tests)
- Configuration (3 tests)
- Search functionality (1 test)

**Running Frontend Tests:**
```bash
# Open in browser
firefox tests/test_frontend.html
# or
google-chrome tests/test_frontend.html
```

### Core/Technical Tests (44 tests)

**Security Tests (10 tests - CRITICAL)**
- Path traversal protection
- File upload validation
- Size limits enforcement
- CORS configuration
- Secure filename handling
- Cleanup mechanisms

**API Tests (27 tests - CRITICAL)**
- Endpoint validation
- Request/response handling
- Error handling
- File cleanup
- Logging

**Integration Tests (3 tests - MEDIUM)**
- End-to-end workflows
- Multi-file processing
- Photo upload workflow

**Compatibility Tests (4 tests - OPTIONAL)**
- UTF-8 encoding
- Special characters
- CSV format variations
- Date format handling

### Business Logic Tests (44 tests)

**LinkedIn Parser Tests (19 tests - HIGH)**
- Profile parsing
- Experience/positions parsing
- Education parsing
- Skills parsing
- Languages parsing
- Certifications parsing
- Date formatting

**CV Generator Tests (25 tests - HIGH)**
- PDF generation
- Photo handling
- Header creation
- Section generation
- Layout and styling
- Pagination
- Error handling

## Running Tests

### Install Dependencies

```bash
cd /home/user/cv-generator
pip install -r backend/requirements.txt
```

### Run All Tests

```bash
# Run all tests with coverage
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=backend --cov-report=html
```

### Run Specific Test Categories

```bash
# Run security tests only
pytest tests/core/test_security.py

# Run API tests only
pytest tests/core/test_app.py

# Run business logic tests only
pytest tests/business/

# Run critical tests only
pytest tests/core/test_security.py tests/core/test_app.py
```

### Run Tests by Priority

```bash
# Phase 1: Critical (Security + API)
pytest tests/core/test_security.py tests/core/test_app.py

# Phase 2: Business Logic (Parser + Generator)
pytest tests/business/

# Phase 3: Integration
pytest tests/core/test_integration.py

# Phase 4: Compatibility
pytest tests/core/test_compatibility.py
```

### Run Tests by Marker

```bash
# Run security tests
pytest -m security

# Run API tests
pytest -m api

# Run integration tests
pytest -m integration
```

### Run Specific Tests

```bash
# Run specific test class
pytest tests/core/test_security.py::TestPathTraversalProtection

# Run specific test function
pytest tests/core/test_security.py::TestPathTraversalProtection::test_path_traversal_attempt_blocked
```

## Coverage Reports

After running tests with coverage, view the HTML report:

```bash
# Generate coverage report
pytest --cov=backend --cov-report=html

# Open coverage report (Linux)
xdg-open htmlcov/index.html

# Open coverage report (Mac)
open htmlcov/index.html
```

## Test Execution Phases

### Phase 1: Core Critical (37 tests)
**Priority: CRITICAL**
- Security: 10 tests
- API Flask: 27 tests

```bash
pytest tests/core/test_security.py tests/core/test_app.py
```

### Phase 2: Business Logic (44 tests)
**Priority: HIGH**
- LinkedIn Parser: 19 tests
- CV Generator: 25 tests

```bash
pytest tests/business/
```

### Phase 3: Integration (3 tests)
**Priority: MEDIUM**
- End-to-end workflows

```bash
pytest tests/core/test_integration.py
```

### Phase 4: Compatibility (4 tests)
**Priority: OPTIONAL**
- Encoding and format compatibility

```bash
pytest tests/core/test_compatibility.py
```

## Test Fixtures

Shared fixtures are defined in `conftest.py`:

- `app`: Flask app instance
- `client`: Flask test client
- `temp_upload_dir`: Temporary directory for file uploads
- `mock_csv_file`: Generic mock CSV file
- `mock_profile_csv`: Mock Profile.csv
- `mock_positions_csv`: Mock Positions.csv
- `mock_education_csv`: Mock Education.csv
- `mock_skills_csv`: Mock Skills.csv
- `mock_languages_csv`: Mock Languages.csv
- `mock_certifications_csv`: Mock Certifications.csv
- `mock_parsed_data`: Complete mock parsed data
- `mock_base64_image`: Small test image
- `mock_large_base64_image`: Large test image for size validation

## Continuous Integration

To integrate with CI/CD:

```yaml
# Example for GitHub Actions
- name: Run tests
  run: |
    pip install -r backend/requirements.txt
    pytest --cov=backend --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
```

## Expected Coverage

Target coverage: **>85%**

- Security functions: 100%
- API endpoints: >95%
- Parser logic: >90%
- Generator logic: >90%
- Error handling: >80%

## Test Maintenance

- Add tests for new features
- Update fixtures when data structure changes
- Keep test data realistic
- Document edge cases
- Review and update security tests regularly

## Troubleshooting

### Import Errors

If you get import errors:
```bash
export PYTHONPATH="${PYTHONPATH}:/home/user/cv-generator/backend"
```

### Cleanup Issues

If tests leave temporary files:
```bash
rm -rf /tmp/cv_uploads/*
```

### Coverage Not Working

Install coverage separately:
```bash
pip install coverage pytest-cov
```

## Contributing

When adding new tests:
1. Follow existing naming conventions
2. Use appropriate fixtures from conftest.py
3. Add docstrings explaining what is tested
4. Group related tests in classes
5. Mark tests with appropriate priority
6. Ensure tests are isolated and don't depend on each other

## Test Statistics

- **Total Tests**: 103 (88 backend + 15 editing)
- **Critical Priority**: 52 tests (Security + API + Editing)
- **High Priority**: 44 tests (Business Logic)
- **Medium Priority**: 3 tests (Integration)
- **Optional Priority**: 4 tests (Compatibility)

- **Editing Features**: 15 backend tests + 24 frontend tests
- **Core/Technical**: 44 tests
- **Business Logic**: 44 tests

### New Editing Tests Results

Last run: **15/15 tests passed** ✅

Key coverage:
- Profile editing: 100%
- Experience editing: 100%
- Education editing: 100%
- Skills selection: 100%
- Languages editing: 100%
- Certifications editing: 100%
- Configuration: 100%
- Multiline support: 100%

## Contact

For questions about tests, see the main project README or SECURITY.md.
