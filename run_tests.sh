#!/bin/bash

# Script pour exécuter tous les tests du générateur de CV
# Usage: ./run_tests.sh [option]
# Options:
#   all     - Exécuter tous les tests (default)
#   editing - Exécuter seulement les tests d'édition
#   core    - Exécuter seulement les tests core
#   quick   - Exécuter les tests rapides (sans couverture)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  CV Generator - Test Runner${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Parse option
OPTION="${1:-all}"

# Function to print section header
print_section() {
    echo ""
    echo -e "${YELLOW}>>> $1${NC}"
    echo ""
}

# Function to run tests with error handling
run_tests() {
    local test_path=$1
    local test_name=$2

    print_section "Running $test_name"

    if pytest "$test_path" -v --tb=short; then
        echo -e "${GREEN}✅ $test_name PASSED${NC}"
        return 0
    else
        echo -e "${RED}❌ $test_name FAILED${NC}"
        return 1
    fi
}

# Track results
FAILED_TESTS=()

case "$OPTION" in
    editing)
        print_section "Editing Features Tests"
        run_tests "tests/test_api.py" "Editing Features" || FAILED_TESTS+=("Editing Features")
        ;;

    core)
        print_section "Core Tests"
        run_tests "tests/core/" "Core/Security/API" || FAILED_TESTS+=("Core Tests")
        ;;

    quick)
        print_section "Quick Tests (No Coverage)"
        pytest tests/test_api.py tests/core/ -v --tb=short || FAILED_TESTS+=("Quick Tests")
        ;;

    all|*)
        print_section "1/3 - Editing Features Tests"
        run_tests "tests/test_api.py" "Editing Features" || FAILED_TESTS+=("Editing Features")

        print_section "2/3 - Core/Technical Tests"
        run_tests "tests/core/" "Core/Security/API" || FAILED_TESTS+=("Core Tests")

        print_section "3/3 - Business Logic Tests"
        run_tests "tests/business/" "Business Logic" || FAILED_TESTS+=("Business Logic")
        ;;
esac

# Summary
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Test Summary${NC}"
echo -e "${BLUE}========================================${NC}"

if [ ${#FAILED_TESTS[@]} -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "  1. Review coverage report: firefox htmlcov/index.html"
    echo "  2. Test frontend: firefox tests/test_frontend.html"
    echo "  3. Commit your changes"
    exit 0
else
    echo -e "${RED}❌ Some tests failed:${NC}"
    for test in "${FAILED_TESTS[@]}"; do
        echo -e "${RED}   - $test${NC}"
    done
    echo ""
    echo -e "${YELLOW}To debug:${NC}"
    echo "  pytest tests/test_api.py -v -s  # Show detailed output"
    exit 1
fi
