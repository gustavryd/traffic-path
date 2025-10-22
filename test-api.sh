#!/bin/bash

echo "==================================="
echo "Traffic Data API - Test Suite"
echo "==================================="
echo ""

# Test 1: Health Check
echo "Test 1: Health Check"
echo "--------------------"
curl -s http://localhost:3000/health | jq
echo ""

# Test 2: Get Traffic Statistics
echo "Test 2: Get Traffic Statistics"
echo "------------------------------"
curl -s http://localhost:3000/api/traffic/stats | jq
echo ""

# Test 3: Get Specific Cell Data
echo "Test 3: Get Cell Data (10, 10)"
echo "-------------------------------"
curl -s http://localhost:3000/api/traffic/cell/10/10 | jq
echo ""

# Test 4: Get Configuration
echo "Test 4: Get Configuration"
echo "-------------------------"
curl -s http://localhost:3000/api/config | jq
echo ""

# Test 5: Create Incident
echo "Test 5: Create Traffic Incident at (8, 8)"
echo "------------------------------------------"
curl -s -X POST http://localhost:3000/api/traffic/incident \
  -H "Content-Type: application/json" \
  -d '{"x": 8, "y": 8, "severity": 0.85, "duration": 45000}' | jq
echo ""

# Test 6: Get Current Traffic State (partial)
echo "Test 6: Get Current Traffic State (first 3 rows)"
echo "------------------------------------------------"
curl -s http://localhost:3000/api/traffic/current | jq '.data.grid[0:3]'
echo ""

echo "==================================="
echo "All tests completed!"
echo "==================================="
