#!/bin/bash
# test-reports.sh - Tests para módulo de reportes

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

API_URL="${API_URL:-http://localhost:8000}"
TESTS_PASSED=0
TESTS_FAILED=0

check_test() {
    local name="$1"
    local status="$2"
    local expected="$3"
    
    echo -n "  [TEST] $name... "
    if [ "$status" -eq "$expected" ]; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAIL${NC}"
        ((TESTS_FAILED++))
    fi
}

echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo -e "${GREEN}  Reports Module Tests${NC}"
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo ""

# Test 1: DVDs no devueltos
echo -e "${YELLOW}[1] Unreturned DVDs Report${NC}"
response=$(curl -s -w "\n%{http_code}" "$API_URL/api/reports/unreturned-dvds")
status=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)
check_test "Get unreturned DVDs" "$status" 200

# Verificar estructura
if echo "$body" | grep -q '"count"'; then
    echo -e "    ${GREEN}✓ Has count field${NC}"
fi
if echo "$body" | grep -q '"overdue_count"'; then
    echo -e "    ${GREEN}✓ Has overdue_count field${NC}"
fi
echo ""

# Test 2: Películas más rentadas
echo -e "${YELLOW}[2] Most Rented Films Report${NC}"
response=$(curl -s -w "\n%{http_code}" "$API_URL/api/reports/most-rented?limit=5")
status=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)
check_test "Get most rented (limit 5)" "$status" 200

response=$(curl -s -w "\n%{http_code}" "$API_URL/api/reports/most-rented?limit=20")
status=$(echo "$response" | tail -n1)
check_test "Get most rented (limit 20)" "$status" 200

# Verificar campos importantes
if echo "$body" | grep -q '"total_rentals"'; then
    echo -e "    ${GREEN}✓ Has rental count${NC}"
fi
if echo "$body" | grep -q '"total_revenue"'; then
    echo -e "    ${GREEN}✓ Has revenue data${NC}"
fi
echo ""

# Test 3: Ganancias por staff
echo -e "${YELLOW}[3] Staff Revenue Report${NC}"
response=$(curl -s -w "\n%{http_code}" "$API_URL/api/reports/staff-revenue")
status=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)
check_test "Get all staff revenue" "$status" 200

# Verificar estructura
if echo "$body" | grep -q '"total_revenue_all_staff"'; then
    echo -e "    ${GREEN}✓ Has total revenue${NC}"
fi
echo ""

# Test 4: Ganancias de staff individual
echo -e "${YELLOW}[4] Individual Staff Revenue${NC}"
response=$(curl -s -w "\n%{http_code}" "$API_URL/api/reports/staff-revenue/1")
status=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)
check_test "Get staff 1 revenue" "$status" 200

response=$(curl -s -w "\n%{http_code}" "$API_URL/api/reports/staff-revenue/2")
status=$(echo "$response" | tail -n1)
check_test "Get staff 2 revenue" "$status" 200

# Verificar staff inexistente
response=$(curl -s -w "\n%{http_code}" "$API_URL/api/reports/staff-revenue/9999")
status=$(echo "$response" | tail -n1)
check_test "Reject invalid staff" "$status" 404
echo ""

# Test 5: Reporte de rentas por cliente
echo -e "${YELLOW}[5] Customer Rentals Report${NC}"
response=$(curl -s -w "\n%{http_code}" "$API_URL/api/reports/customer-rentals/1")
status=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)
check_test "Get customer 1 report" "$status" 200

# Verificar campos
if echo "$body" | grep -q '"total_rentals"'; then
    echo -e "    ${GREEN}✓ Has rental count${NC}"
fi
if echo "$body" | grep -q '"active_rentals"'; then
    echo -e "    ${GREEN}✓ Has active rentals${NC}"
fi
if echo "$body" | grep -q '"total_spent"'; then
    echo -e "    ${GREEN}✓ Has spending data${NC}"
fi

# Cliente inexistente
response=$(curl -s -w "\n%{http_code}" "$API_URL/api/reports/customer-rentals/9999")
status=$(echo "$response" | tail -n1)
check_test "Reject invalid customer" "$status" 404
echo ""

# Test 6: Verificar formato JSON
echo -e "${YELLOW}[6] JSON Format Validation${NC}"
response=$(curl -s "$API_URL/api/reports/most-rented?limit=3")
if echo "$response" | python3 -m json.tool > /dev/null 2>&1; then
    echo -e "  ${GREEN}✓ Valid JSON format${NC}"
    ((TESTS_PASSED++))
else
    echo -e "  ${RED}✗ Invalid JSON format${NC}"
    ((TESTS_FAILED++))
fi
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