#!/bin/bash
# test-api.sh - Basic API checks (robust for redirects)

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

API_URL="${API_URL:-http://localhost:8000}"

TESTS_PASSED=0
TESTS_FAILED=0

check_any() {
  # check_any "Name" "<status>" "200 307 308"
  local name="$1"
  local status="$2"
  local expected_list="$3"

  echo -n "  [TEST] $name... "
  for exp in $expected_list; do
    if [ "$status" -eq "$exp" ]; then
      echo -e "${GREEN}✓ PASS${NC}"
      ((TESTS_PASSED++))
      return 0
    fi
  done
  echo -e "${RED}✗ FAIL (Expected: $expected_list, Got: $status)${NC}"
  ((TESTS_FAILED++))
  return 0
}

get_status() {
  # follows redirects and returns status code
  curl -s -L -o /dev/null -w "%{http_code}" "$1"
}

get_body_and_status() {
  # returns "BODY\nSTATUS"
  curl -s -L -w "\n%{http_code}" "$1"
}

echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo -e "${GREEN}  DVD Rental API - Test Suite${NC}"
echo -e "${BLUE}  Target: ${API_URL}${NC}"
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo ""

echo -e "${YELLOW}⏳ Esperando a que la API esté lista...${NC}"
for i in {1..30}; do
  if curl -s "${API_URL}/health" | grep -Eiq "healthy|ok"; then
    echo -e "${GREEN}✓ API está lista${NC}"
    break
  fi
  sleep 2
done
echo ""

echo -e "${YELLOW}[1/7] Health & Info${NC}"

# 1) Health endpoint (must be OK/healthy)
resp=$(curl -s -w "\n%{http_code}" "${API_URL}/health")
status=$(echo "$resp" | tail -n1)
body=$(echo "$resp" | head -n-1)
check_any "Health Check" "$status" "200"
echo "$body" | grep -Eiq "healthy|ok" || { echo -e "${RED}  Health body not OK${NC}"; ((TESTS_FAILED++)); }

# 2) Root endpoint (often exists, allow 200 or redirect)
status=$(get_status "${API_URL}/")
check_any "Root /" "$status" "200 307 308 404"

# 3) OpenAPI json (FastAPI usually provides it)
status=$(get_status "${API_URL}/openapi.json")
check_any "OpenAPI /openapi.json" "$status" "200 307 308"

# 4) Docs (FastAPI usually provides it)
status=$(get_status "${API_URL}/docs")
check_any "Docs /docs" "$status" "200 307 308"

echo ""

# OPTIONAL: if your API is mounted under /api, check /api/health too,
# but allow 404 if project doesn't use that prefix.
echo -e "${YELLOW}[2/7] API Prefix (optional)${NC}"
status=$(get_status "${API_URL}/api/health")
check_any "Optional /api/health" "$status" "200 307 308 404"
echo ""

# Summary
TOTAL=$((TESTS_PASSED + TESTS_FAILED))
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo -e "${GREEN}  Results${NC}"
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo -e "  Total:  $TOTAL"
echo -e "  ${GREEN}Passed: $TESTS_PASSED${NC}"
echo -e "  ${RED}Failed: $TESTS_FAILED${NC}"
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo ""

[ $TESTS_FAILED -eq 0 ] && exit 0 || exit 1
