#!/bin/bash
# test-api.sh - Suite completa de pruebas para DVD Rental API

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuración
API_URL="${API_URL:-http://localhost:8000}"
TESTS_PASSED=0
TESTS_FAILED=0

# Función para verificar respuesta
check_response() {
    local test_name="$1"
    local response="$2"
    local expected_status="$3"
    local actual_status="$4"
    
    echo -n "  [TEST] $test_name... "
    
    if [ "$actual_status" -eq "$expected_status" ]; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC}"
        echo "    Expected: $expected_status, Got: $actual_status"
        ((TESTS_FAILED++))
        return 1
    fi
}

# Banner
echo ""
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo -e "${GREEN}  DVD Rental API - Test Suite${NC}"
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo -e "${YELLOW}  Target: $API_URL${NC}"
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo ""

# Esperar a que la API esté lista
echo -e "${YELLOW}⏳ Esperando a que la API esté lista...${NC}"
max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if curl -sf "$API_URL/health" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ API está lista${NC}"
        break
    fi
    ((attempt++))
    echo -n "."
    sleep 2
done
echo ""

if [ $attempt -eq $max_attempts ]; then
    echo -e "${RED}✗ La API no respondió después de $max_attempts intentos${NC}"
    exit 1
fi

# === CATEGORÍA: HEALTH & INFO ===
echo -e "${BLUE}[1/7] Health & Info${NC}"
response=$(curl -s -w "\n%{http_code}" "$API_URL/health")
status=$(echo "$response" | tail -n1)
check_response "Health Check" "" 200 "$status"

response=$(curl -s -w "\n%{http_code}" "$API_URL/")
status=$(echo "$response" | tail -n1)
check_response "Root Endpoint" "" 200 "$status"
echo ""

# === CATEGORÍA: FILMS ===
echo -e "${BLUE}[2/7] Films Endpoints${NC}"
response=$(curl -s -w "\n%{http_code}" "$API_URL/api/films?limit=5")
status=$(echo "$response" | tail -n1)
check_response "List Films" "" 200 "$status"

response=$(curl -s -w "\n%{http_code}" "$API_URL/api/films/1")
status=$(echo "$response" | tail -n1)
check_response "Get Film by ID" "" 200 "$status"

response=$(curl -s -w "\n%{http_code}" "$API_URL/api/films/search?title=academy")
status=$(echo "$response" | tail -n1)
check_response "Search Films" "" 200 "$status"

response=$(curl -s -w "\n%{http_code}" "$API_URL/api/films/category/Action")
status=$(echo "$response" | tail -n1)
check_response "Films by Category" "" 200 "$status"
echo ""

# === CATEGORÍA: CUSTOMERS ===
echo -e "${BLUE}[3/7] Customers Endpoints${NC}"
response=$(curl -s -w "\n%{http_code}" "$API_URL/api/customers?limit=5")
status=$(echo "$response" | tail -n1)
check_response "List Customers" "" 200 "$status"

response=$(curl -s -w "\n%{http_code}" "$API_URL/api/customers/1")
status=$(echo "$response" | tail -n1)
check_response "Get Customer by ID" "" 200 "$status"
echo ""

# === CATEGORÍA: STAFF ===
echo -e "${BLUE}[4/7] Staff Endpoints${NC}"
response=$(curl -s -w "\n%{http_code}" "$API_URL/api/staff")
status=$(echo "$response" | tail -n1)
check_response "List Staff" "" 200 "$status"

response=$(curl -s -w "\n%{http_code}" "$API_URL/api/staff/1")
status=$(echo "$response" | tail -n1)
check_response "Get Staff by ID" "" 200 "$status"
echo ""

# === CATEGORÍA: RENTALS ===
echo -e "${BLUE}[5/7] Rentals Endpoints${NC}"
response=$(curl -s -w "\n%{http_code}" "$API_URL/api/rentals?limit=5")
status=$(echo "$response" | tail -n1)
check_response "List Rentals" "" 200 "$status"

# Crear renta
echo -e "${YELLOW}  Creating test rental...${NC}"
response=$(curl -s -w "\n%{http_code}" \
    -X POST "$API_URL/api/rentals" \
    -H "Content-Type: application/json" \
    -d '{"customer_id":1,"film_id":1,"staff_id":1}')
status=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)
check_response "Create Rental" "" 201 "$status"

if [ $? -eq 0 ]; then
    RENTAL_ID=$(echo "$body" | grep -o '"rental_id":[0-9]*' | grep -o '[0-9]*' | head -1)
    echo -e "${GREEN}  ✓ Created rental ID: $RENTAL_ID${NC}"
    
    # Devolver renta
    if [ -n "$RENTAL_ID" ]; then
        response=$(curl -s -w "\n%{http_code}" \
            -X PUT "$API_URL/api/rentals/$RENTAL_ID/return")
        status=$(echo "$response" | tail -n1)
        check_response "Return Rental" "" 200 "$status"
    fi
fi

response=$(curl -s -w "\n%{http_code}" "$API_URL/api/rentals/customer/1")
status=$(echo "$response" | tail -n1)
check_response "Customer Rentals" "" 200 "$status"
echo ""

# === CATEGORÍA: REPORTS ===
echo -e "${BLUE}[6/7] Reports Endpoints${NC}"
response=$(curl -s -w "\n%{http_code}" "$API_URL/api/reports/unreturned-dvds")
status=$(echo "$response" | tail -n1)
check_response "Unreturned DVDs Report" "" 200 "$status"

response=$(curl -s -w "\n%{http_code}" "$API_URL/api/reports/most-rented?limit=10")
status=$(echo "$response" | tail -n1)
check_response "Most Rented Films Report" "" 200 "$status"

response=$(curl -s -w "\n%{http_code}" "$API_URL/api/reports/staff-revenue")
status=$(echo "$response" | tail -n1)
check_response "Staff Revenue Report" "" 200 "$status"

response=$(curl -s -w "\n%{http_code}" "$API_URL/api/reports/staff-revenue/1")
status=$(echo "$response" | tail -n1)
check_response "Staff Revenue by ID" "" 200 "$status"

response=$(curl -s -w "\n%{http_code}" "$API_URL/api/reports/customer-rentals/1")
status=$(echo "$response" | tail -n1)
check_response "Customer Rentals Report" "" 200 "$status"
echo ""

# === CATEGORÍA: PERFORMANCE ===
echo -e "${BLUE}[7/7] Performance Tests${NC}"
start_time=$(date +%s%3N)
curl -s "$API_URL/api/films?limit=100" > /dev/null
end_time=$(date +%s%3N)
duration=$((end_time - start_time))
echo -e "  [PERF] List 100 films: ${duration}ms"

if [ $duration -lt 1000 ]; then
    echo -e "${GREEN}  ✓ Performance: Excellent (<1s)${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${YELLOW}  ⚠ Performance: Acceptable (>1s)${NC}"
fi
echo ""

# === RESUMEN ===
TOTAL=$((TESTS_PASSED + TESTS_FAILED))
PASS_RATE=$((TESTS_PASSED * 100 / TOTAL))

echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo -e "${GREEN}  Test Results${NC}"
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo -e "  Total Tests:  $TOTAL"
echo -e "  ${GREEN}Passed:       $TESTS_PASSED${NC}"
echo -e "  ${RED}Failed:       $TESTS_FAILED${NC}"
echo -e "  Pass Rate:    $PASS_RATE%"
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed successfully!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some tests failed!${NC}"
    exit 1
fi