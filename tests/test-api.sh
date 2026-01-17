#!/usr/bin/env bash
# test-api.sh - Basic API checks (robust + no phantom fails)

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
  # check_any "Name" <status> "200 307 308"
  local name="$1"
  local status="$2"
  local expected_list="$3"

  echo -n "  [TEST] $name... "
  for exp in $expected_list; do
    if [ "$status" -eq "$exp" ]; then
      echo -e "${GREEN}✓ PASS${NC}"
      TESTS_PASSED=$((TESTS_PASSED + 1))
      return 0
    fi
  done

  echo -e "${RED}✗ FAIL (Expected: $expected_list, Got: $status)${NC}"
  TESTS_FAILED=$((TESTS_FAILED + 1))
  return 0
}

get_status() {
  curl -s -L -o /dev/null -w "%{http_code}" "$1"
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

echo -e "${YELLOW}[1/2] Health & Info${NC}"
resp=$(curl -s -w "\n%{http_code}" "${API_URL}/health")
status=$(echo "$resp" | tail -n1)
body=$(echo "$resp" | head -n-1)
check_any "Health Check" "$status" "200"

if echo "$body" | grep -Eiq "healthy|ok"; then
  echo -e "  ${GREEN}✓ PASS${NC} (Health body OK)"
  TESTS_PASSED=$((TESTS_PASSED + 1))
else
  echo -e "  ${RED}✗ FAIL${NC} (Health body not OK)"
  TESTS_FAILED=$((TESTS_FAILED + 1))
fi

check_any "Root /" "$(get_status "${API_URL}/")" "200 307 308 404"
check_any "OpenAPI /openapi.json" "$(get_status "${API_URL}/openapi.json")" "200 307 308"
check_any "Docs /docs" "$(get_status "${API_URL}/docs")" "200 307 308"
echo ""

echo -e "${YELLOW}[2/2] Quick API endpoints presence${NC}"
# Estos endpoints existen en tu openapi.json (los probamos con status aceptable)
check_any "GET /api/films/" "$(get_status "${API_URL}/api/films/")" "200"
check_any "GET /api/customers/" "$(get_status "${API_URL}/api/customers/")" "200"
check_any "GET /api/staff/" "$(get_status "${API_URL}/api/staff/")" "200"
echo ""

TOTAL=$((TESTS_PASSED + TESTS_FAILED))
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo -e "${GREEN}  Results${NC}"
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo -e "  Total:  $TOTAL"
echo -e "  ${GREEN}Passed: $TESTS_PASSED${NC}"
echo -e "  ${RED}Failed: $TESTS_FAILED${NC}"
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo ""

[ "$TESTS_FAILED" -eq 0 ] && exit 0 || exit 1
