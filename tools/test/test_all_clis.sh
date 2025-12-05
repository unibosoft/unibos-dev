#!/bin/bash
# Test script for all 5 UNIBOS CLIs
# Tests the complete 5-tier architecture

set -e

echo "=========================================="
echo "UNIBOS 5-Tier CLI Architecture Test"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Test function
test_cli() {
    local cli_name=$1
    local test_description=$2
    local command=$3

    echo -e "${CYAN}Testing: ${test_description}${NC}"
    echo "Command: $command"

    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASS${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}✗ FAIL${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
    echo ""
}

# Test help output
test_help() {
    local cli_name=$1

    echo -e "${CYAN}Testing: ${cli_name} --help${NC}"
    echo "Command: $cli_name --help"

    if $cli_name --help > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASS${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}✗ FAIL${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
    echo ""
}

# Test version output
test_version() {
    local cli_name=$1

    echo -e "${CYAN}Testing: ${cli_name} --version${NC}"
    echo "Command: $cli_name --version"

    if $cli_name --version > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASS${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}✗ FAIL${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
    echo ""
}

echo "=========================================="
echo "1. Testing unibos-dev (Development)"
echo "=========================================="
echo ""

test_help "unibos-dev"
test_version "unibos-dev"
test_cli "unibos-dev" "unibos-dev status" "unibos-dev status"
test_cli "unibos-dev" "unibos-dev git status" "unibos-dev git status"

echo "=========================================="
echo "2. Testing unibos-manager (Manager)"
echo "=========================================="
echo ""

test_help "unibos-manager"
test_version "unibos-manager"

echo "=========================================="
echo "3. Testing unibos-hub (Hub)"
echo "=========================================="
echo ""

test_help "unibos-hub"
test_version "unibos-hub"
test_cli "unibos-hub" "unibos-hub start (dry-run)" "unibos-hub start"
test_cli "unibos-hub" "unibos-hub stop (dry-run)" "unibos-hub stop"
test_cli "unibos-hub" "unibos-hub restart (dry-run)" "unibos-hub restart"
test_cli "unibos-hub" "unibos-hub logs (dry-run)" "unibos-hub logs"
test_cli "unibos-hub" "unibos-hub status (dry-run)" "unibos-hub status"
test_cli "unibos-hub" "unibos-hub backup (dry-run)" "unibos-hub backup"

echo "=========================================="
echo "4. Testing unibos-worker (Worker)"
echo "=========================================="
echo ""

test_help "unibos-worker"
test_version "unibos-worker"
test_cli "unibos-worker" "unibos-worker status" "unibos-worker status"

echo "=========================================="
echo "5. Testing unibos (Node)"
echo "=========================================="
echo ""

test_help "unibos"
test_version "unibos"
test_cli "unibos" "unibos status" "unibos status"
test_cli "unibos" "unibos launch (no args)" "unibos launch"
test_cli "unibos" "unibos update" "unibos update"
test_cli "unibos" "unibos backup" "unibos backup"
test_cli "unibos" "unibos settings" "unibos settings"

echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo ""
echo -e "Total tests: $((TESTS_PASSED + TESTS_FAILED))"
echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Failed: $TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    echo ""
    echo "=========================================="
    echo "5-Tier Architecture Verified"
    echo "=========================================="
    echo ""
    echo "Available CLIs:"
    echo "  1. unibos-dev       - Development environment"
    echo "  2. unibos-manager   - Remote management"
    echo "  3. unibos-hub       - Hub server (rocksteady + bebop)"
    echo "  4. unibos-worker    - Background task processing"
    echo "  5. unibos           - Node / end user"
    echo ""
    echo "TUI Mode (no arguments):"
    echo "  unibos-dev"
    echo "  unibos-manager"
    echo "  unibos-hub"
    echo "  unibos-worker"
    echo "  unibos"
    echo ""
    echo "CLI Mode (with arguments):"
    echo "  unibos-dev status"
    echo "  unibos-manager --help"
    echo "  unibos-hub start"
    echo "  unibos-worker start --type ocr"
    echo "  unibos launch recaria"
    echo ""
    exit 0
else
    echo -e "${RED}✗ Some tests failed${NC}"
    echo ""
    echo "Please check the failed tests above."
    exit 1
fi
