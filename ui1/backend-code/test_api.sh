#!/bin/bash

# CalmRoute TfL API Test Script
# Usage: ./test_api.sh [base_url]
# Default base_url: http://localhost:8000

BASE_URL="${1:-http://localhost:8000}"

# Helper function to make requests and format output
test_endpoint() {
    local method=$1
    local endpoint=$2
    local data=$3
    
    if [ "$method" == "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL$endpoint" \
            -H "Content-Type: application/json")
    else
        response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data")
    fi
    
    # Extract HTTP code (last line) and body (all lines except last)
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    # Pretty print JSON
    echo "$body" | jq '.' 2>/dev/null || echo "$body"
    echo "Status: $http_code"
}

echo "🧪 Testing CalmRoute TfL API at $BASE_URL"
echo "=========================================="

# Test 1: Health Check
echo ""
echo "📋 Test 1: Health Check"
echo "------------------------"
test_endpoint "GET" "/health" ""

# Test 2: Basic Route Request (Minimal)
echo ""
echo "📋 Test 2: Basic Route Request (No preferences, no time)"
echo "--------------------------------------------------------"
test_endpoint "POST" "/route" '{
    "origin": "Kings Cross Station",
    "destination": "Liverpool Street Station",
    "preferences": {},
    "travel_date": null,
    "start_time": null,
    "arrive_by": false
  }'

# Test 3: Route with User Preferences
echo ""
echo "📋 Test 3: Route with User Preferences"
echo "--------------------------------------"
test_endpoint "POST" "/route" '{
    "origin": "Victoria Station",
    "destination": "Camden Town",
    "preferences": {
      "avoid_crowds": true,
      "avoid_noise": true,
      "avoid_heat": false,
      "prefer_buses": false,
      "minimise_changes": true
    },
    "travel_date": null,
    "start_time": null,
    "arrive_by": false
  }'

# Test 4: Route with Specific Date and Time
echo ""
echo "📋 Test 4: Route with Specific Date and Departure Time"
echo "------------------------------------------------------"
test_endpoint "POST" "/route" '{
    "origin": "Paddington",
    "destination": "London Bridge",
    "preferences": {
      "avoid_crowds": true,
      "avoid_noise": false,
      "avoid_heat": false,
      "prefer_buses": false,
      "minimise_changes": false
    },
    "travel_date": "2026-02-01",
    "start_time": "09:00:00",
    "arrive_by": false
  }'

# Test 5: Route with Arrival Time
echo ""
echo "📋 Test 5: Route with Arrival Time (arrive_by: true)"
echo "----------------------------------------------------"
test_endpoint "POST" "/route" '{
    "origin": "Heathrow Terminal 5",
    "destination": "Waterloo Station",
    "preferences": {
      "avoid_crowds": false,
      "avoid_noise": false,
      "avoid_heat": false,
      "prefer_buses": false,
      "minimise_changes": true
    },
    "travel_date": "2026-02-01",
    "start_time": "18:00:00",
    "arrive_by": true
  }'

# Test 6: Route with Bus Preference
echo ""
echo "📋 Test 6: Route with Bus Preference"
echo "------------------------------------"
test_endpoint "POST" "/route" '{
    "origin": "Oxford Circus",
    "destination": "Piccadilly Circus",
    "preferences": {
      "avoid_crowds": false,
      "avoid_noise": false,
      "avoid_heat": false,
      "prefer_buses": true,
      "minimise_changes": false
    },
    "travel_date": null,
    "start_time": null,
    "arrive_by": false
  }'

# Test 7: All Preferences Enabled
echo ""
echo "📋 Test 7: All Preferences Enabled"
echo "----------------------------------"
test_endpoint "POST" "/route" '{
    "origin": "Stratford",
    "destination": "Westminster",
    "preferences": {
      "avoid_crowds": true,
      "avoid_noise": true,
      "avoid_heat": true,
      "prefer_buses": true,
      "minimise_changes": true
    },
    "travel_date": "2026-02-03",
    "start_time": "08:30:00",
    "arrive_by": false
  }'

echo ""
echo "✅ All tests completed!"
echo ""
echo "Note: Make sure the API server is running with: python3 main.py"
echo "or: uvicorn main:app --reload"
