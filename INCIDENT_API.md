# Traffic Incident API Documentation

This document describes the enhanced incident creation functionality for the traffic generator system.

## Overview

The system now provides a comprehensive API for creating, managing, and monitoring traffic incidents on road edges. Each incident affects traffic flow on the specified edge and propagates to connected roads.

## Enhanced Features

### 1. Create Traffic Incident
Create a traffic incident on a chosen edge with validation and detailed feedback.

**Endpoint:** `POST /api/traffic/incident`

**Request Body:**
```json
{
  "edgeId": "edge_5",           // Required: ID of the edge (road)
  "severity": 0.7,              // Optional: 0.0-1.0, default: 0.5
  "duration": 120000,           // Optional: milliseconds (10s-1hr), default: 60000
  "type": "accident"            // Optional: incident type, default: random
}
```

**Incident Types:**
- `accident` - Vehicle accident causing delays
- `construction` - Road construction work
- `roadblock` - Road closure or blockage
- `weather` - Weather-related conditions
- `event` - Special event causing congestion

**Response (Success):**
```json
{
  "success": true,
  "message": "Incident created successfully",
  "data": {
    "id": "incident_1729593234567_abc123xyz",
    "edgeId": "edge_5",
    "from": "node_3",
    "to": "node_7",
    "severity": 0.7,
    "startTime": 1729593234567,
    "endTime": 1729593354567,
    "type": "accident",
    "description": "Severe vehicle accident causing delays"
  }
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": "Edge edge_99 already has an active incident"
}
```

**Validation Rules:**
- `edgeId` must exist in the graph
- Edge must not already have an active incident
- `severity` is clamped between 0.0 and 1.0
- `duration` is clamped between 10,000ms (10s) and 3,600,000ms (1 hour)

**Example Usage:**
```bash
# Create a severe accident with 2-minute duration
curl -X POST http://localhost:3000/api/traffic/incident \
  -H "Content-Type: application/json" \
  -d '{
    "edgeId": "edge_5",
    "severity": 0.8,
    "duration": 120000,
    "type": "accident"
  }'
```

---

### 2. Get All Edges
Retrieve all edges in the graph with their current status.

**Endpoint:** `GET /api/traffic/edges`

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "edge_0",
      "from": "node_0",
      "to": "node_1",
      "distance": 45,
      "currentWeight": 0.32,
      "hasIncident": false
    },
    {
      "id": "edge_5",
      "from": "node_3",
      "to": "node_7",
      "distance": 58,
      "currentWeight": 0.85,
      "hasIncident": true
    }
  ]
}
```

---

### 3. Get Available Edges
Get only edges that don't currently have incidents (useful for creating new incidents).

**Endpoint:** `GET /api/traffic/edges/available`

**Response:**
```json
{
  "success": true,
  "count": 47,
  "data": [
    {
      "id": "edge_0",
      "from": "node_0",
      "to": "node_1",
      "distance": 45,
      "currentTraffic": 0.32
    }
  ]
}
```

---

### 4. Get Active Incidents
Retrieve all currently active incidents with remaining time.

**Endpoint:** `GET /api/traffic/incidents`

**Response:**
```json
{
  "success": true,
  "count": 2,
  "data": [
    {
      "id": "incident_1729593234567_abc123xyz",
      "edgeId": "edge_5",
      "from": "node_3",
      "to": "node_7",
      "severity": 0.7,
      "startTime": 1729593234567,
      "endTime": 1729593354567,
      "type": "accident",
      "description": "Severe vehicle accident causing delays",
      "remainingTime": 45230
    }
  ]
}
```

---

### 5. Clear Incident
Manually clear an active incident before its scheduled end time.

**Endpoint:** `DELETE /api/traffic/incident/:incidentId`

**Response:**
```json
{
  "success": true,
  "message": "Incident cleared successfully",
  "data": {
    "id": "incident_1729593234567_abc123xyz",
    "edgeId": "edge_5",
    "from": "node_3",
    "to": "node_7"
  }
}
```

---

## Incident Effects

When an incident is created:

1. **Direct Impact:** The incident increases traffic weight on the affected edge by up to 80% of the severity value
2. **Propagation:** Connected roads experience increased traffic (up to 50% of the severity value)
3. **Speed Reduction:** Vehicle speeds decrease proportionally to increased traffic
4. **Vehicle Count:** More vehicles accumulate on affected roads

**Severity Levels:**
- `0.0 - 0.4`: Minor incident - minimal impact
- `0.4 - 0.7`: Moderate incident - noticeable delays
- `0.7 - 1.0`: Severe incident - major traffic disruption

---

## Usage Workflow

### Creating an Incident on a Specific Edge

1. **List available edges:**
   ```bash
   curl http://localhost:3000/api/traffic/edges/available
   ```

2. **Choose an edge and create incident:**
   ```bash
   curl -X POST http://localhost:3000/api/traffic/incident \
     -H "Content-Type: application/json" \
     -d '{
       "edgeId": "edge_12",
       "severity": 0.6,
       "duration": 180000,
       "type": "construction"
     }'
   ```

3. **Monitor active incidents:**
   ```bash
   curl http://localhost:3000/api/traffic/incidents
   ```

4. **Clear incident early (optional):**
   ```bash
   curl -X DELETE http://localhost:3000/api/traffic/incident/incident_1729593234567_abc123xyz
   ```

---

## JavaScript/Node.js Example

```javascript
const axios = require('axios');

const API_URL = 'http://localhost:3000';

async function createTrafficIncident() {
  try {
    // Get available edges
    const edgesResponse = await axios.get(`${API_URL}/api/traffic/edges/available`);
    const availableEdges = edgesResponse.data.data;
    
    if (availableEdges.length === 0) {
      console.log('No available edges for incidents');
      return;
    }
    
    // Choose a random edge
    const randomEdge = availableEdges[Math.floor(Math.random() * availableEdges.length)];
    
    // Create incident
    const incidentResponse = await axios.post(`${API_URL}/api/traffic/incident`, {
      edgeId: randomEdge.id,
      severity: 0.75,
      duration: 120000,
      type: 'accident'
    });
    
    console.log('Incident created:', incidentResponse.data);
    
    // Monitor for 30 seconds
    setTimeout(async () => {
      const incidents = await axios.get(`${API_URL}/api/traffic/incidents`);
      console.log('Active incidents:', incidents.data);
    }, 30000);
    
  } catch (error) {
    console.error('Error:', error.response?.data || error.message);
  }
}

createTrafficIncident();
```

---

## Events

The TrafficGenerator now emits additional events:

```javascript
trafficGenerator.on('incidentCreated', (incident) => {
  console.log('New incident:', incident);
});

trafficGenerator.on('incidentCleared', (incident) => {
  console.log('Incident cleared:', incident);
});
```

---

## Error Handling

Common errors and solutions:

| Error | Cause | Solution |
|-------|-------|----------|
| `Edge not found: edge_99` | Invalid edge ID | Use `/api/traffic/edges` to get valid IDs |
| `Edge already has an active incident` | Duplicate incident | Choose different edge or clear existing incident |
| `edgeId is required` | Missing parameter | Include edgeId in request body |
| `Incident not found` | Invalid incident ID | Use `/api/traffic/incidents` to get valid IDs |

---

## Testing

Test the incident functionality with curl:

```bash
# 1. Get available edges
curl http://localhost:3000/api/traffic/edges/available | jq

# 2. Create a test incident
curl -X POST http://localhost:3000/api/traffic/incident \
  -H "Content-Type: application/json" \
  -d '{"edgeId": "edge_0", "severity": 0.8, "duration": 60000, "type": "accident"}'

# 3. Check active incidents
curl http://localhost:3000/api/traffic/incidents | jq

# 4. View traffic state
curl http://localhost:3000/api/traffic/current | jq '.data.edges[] | select(.isIncident == true)'

# 5. Wait for incident to clear or manually clear it
# (Wait 60 seconds or use DELETE endpoint)
