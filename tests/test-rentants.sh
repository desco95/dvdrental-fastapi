#!/bin/bash
# test-rentants.sh - Tests específicos para el módulo de rentas

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

API_URL="${API_URL:-http://localhost:8000}"
TESTS_PASSED=0
TESTS_FAILED=0

# check_test "name" <status> "<expected list>"
# expected list examples: "200" or "201 307"
check_test() {
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

echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo -e "${GREEN}  Rental Module Tests${NC}"
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo ""

# Helper: POST JSON and capture body + status (no follow redirects)
post_json() {
    local url="$1"
    local json="$2"
    curl -s -w "\n%{http_code}" \
        -X POST "$url" \
        -H "Content-Type: application/json" \
        -d "$json"
}

# Helper: POST JSON following redirects (-L) to get final response body/status
post_json_follow() {
    local url="$1"
    local json="$2"
    curl -s -L -w "\n%{http_code}" \
        -X POST "$url" \
        -H "Content-Type: application/json" \
        -d "$json"
}

# Test 1: Crear renta válida
echo -e "${YELLOW}[1] Testing rental creation${NC}"
response=$(post_json "$API_URL/api/rentals" '{"customer_id":1,"film_id":2,"staff_id":1}')
status=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)

# Accept 201 or 307 (FastAPI redirect)
check_test "Create valid rental" "$status" "201 307"

# If redirect, re-run following redirects to get actual body with rental_id
if [ "$status" -eq 307 ]; then
    response=$(post_json_follow "$API_URL/api/rentals" '{"customer_id":1,"film_id":2,"staff_id":1}')
    status=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
fi

if [ "$status" -eq 201 ]; then
    RENTAL_ID=$(echo "$body" | grep -o '"rental_id":[0-9]*' | grep -o '[0-9]*' | head -1)
    if [ -n "$RENTAL_ID" ]; then
        echo -e "    ${GREEN}Created rental ID: $RENTAL_ID${NC}"
    fi
fi
echo ""

# Test 2: Crear renta con customer inexistente
echo -e "${YELLOW}[2] Testing invalid customer${NC}"
response=$(post_json "$API_URL/api/rentals" '{"customer_id":9999,"film_id":1,"staff_id":1}')
status=$(echo "$response" | tail -n1)
check_test "Reject invalid customer" "$status" "404"
echo ""

# Test 3: Crear renta con película inexistente
echo -e "${YELLOW}[3] Testing invalid film${NC}"
response=$(post_json "$API_URL/api/rentals" '{"customer_id":1,"film_id":9999,"staff_id":1}')
status=$(echo "$response" | tail -n1)
check_test "Reject invalid film" "$status" "404"
echo ""

# Test 4: Devolver renta
if [ -n "${RENTAL_ID:-}" ]; then
    echo -e "${YELLOW}[4] Testing rental return${NC}"
    response=$(curl -s -w "\n%{http_code}" -X PUT "$API_URL/api/rentals/$RENTAL_ID/return")
    status=$(echo "$response" | tail -n1)
    check_test "Return rental" "$status" "200"
    echo ""

    # Test 5: Intentar devolver renta ya devuelta
    echo -e "${YELLOW}[5] Testing double return${NC}"
    response=$(curl -s -w "\n%{http_code}" -X PUT "$API_URL/api/rentals/$RENTAL_ID/return")
    status=$(echo "$response" | tail -n1)
    check_test "Reject double return" "$status" "400"
    echo ""
else
    echo -e "${YELLOW}[4-5] Skipped return tests (no RENTAL_ID captured)${NC}"
    echo ""
fi

# Test 6: Obtener rentas de cliente
echo -e "${YELLOW}[6] Testing customer rentals${NC}"
response=$(curl -s -w "\n%{http_code}" "$API_URL/api/rentals/customer/1")
status=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)
check_test "Get customer rentals" "$status" "200"

# Verificar que tiene al menos una renta
rental_count=$(echo "$body" | grep -o '"total_rentals":[0-9]*' | grep -o '[0-9]*' | head -1)
if [ -n "$rental_count" ] && [ "$rental_count" -gt 0 ]; then
    echo -e "    ${GREEN}Found $rental_count rentals${NC}"
fi
echo ""

# Test 7: Crear nueva renta para cancelar
echo -e "${YELLOW}[7] Testing rental cancellation${NC}"
response=$(post_json "$API_URL/api/rentals" '{"customer_id":2,"film_id":3,"staff_id":1}')
status=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)

check_test "Create rental to cancel" "$status" "201 307"

if [ "$status" -eq 307 ]; then
    response=$(post_json_follow "$API_URL/api/rentals" '{"customer_id":2,"film_id":3,"staff_id":1}')
    status=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
fi

if [ "$status" -eq 201 ]; then
    CANCEL_ID=$(echo "$body" | grep -o '"rental_id":[0-9]*' | grep -o '[0-9]*' | head -1)
    if [ -n "$CANCEL_ID" ]; then
        echo -e "    ${GREEN}Created rental to cancel: $CANCEL_ID${NC}"

        # Cancelar la renta
        response=$(curl -s -w "\n%{http_code}" -X DELETE "$API_URL/api/rentals/$CANCEL_ID")
        status=$(echo "$response" | tail -n1)
        check_test "Cancel active rental" "$status" "200"
    fi
fi
echo ""

# Test 8: Listar rentas con paginación
echo -e "${YELLOW}[8] Testing pagination${NC}"
response=$(curl -s -w "\n%{http_code}" "$API_URL/api/rentals?limit=10&offset=0")
status=$(echo "$response" | tail -n1)
check_test "Paginated list (page 1)" "$status" "200"

response=$(curl -s -w "\n%{http_code}" "$API_URL/api/rentals?limit=10&offset=10")
status=$(echo "$response" | tail -n1)
check_test "Paginated list (page 2)" "$status" "200"
echo ""

# Resumen
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
