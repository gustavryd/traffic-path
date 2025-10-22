# Traffic Data API - Graph-Based

Real-time traffic data generation API with graph structure (vertices and edges) for network/road visualization.

## Features

- **Graph-Based Model**: Vertices (intersections) connected by edges (roads)
- **Real-time Updates**: WebSocket connection for live traffic data streaming
- **REST API**: Full REST endpoints for querying and controlling traffic data
- **Dynamic Traffic Patterns**: Realistic traffic simulation with:
  - Rush hour patterns (morning and evening peaks)
  - Traffic flow propagation through connected roads
  - Random incidents (accidents, construction, etc.)
  - Vehicle counting and speed calculation
- **Traffic Statistics**: Real-time metrics and analytics
- **Incident Management**: Create and track traffic incidents on roads

## Data Format

The API returns traffic data in the following format:

```json
{
  "vertices": [
    {
      "id": "node_0",
      "name": "Intersection 1",
      "x": 283.0,
      "y": 54.3
    }
  ],
  "edges": [
    {
      "id": "edge_0",
      "from": "node_0",
      "to": "node_9",
      "weight": 0.65,
      "distance": 12,
      "speed": 24,
      "vehicleCount": 63,
      "isIncident": false,
      "incidentSeverity": 0,
      "bidirectional": true
    }
  ]
}
```

## Installation

```bash
npm install
```

## Usage

### Start the Server

```bash
npm start
```

For development with auto-restart:

```bash
npm run dev
```

The API will start on port 3000 by default.

## API Endpoints

### REST API

#### Get Graph Structure
```
GET /api/traffic/graph
```

Returns the traffic graph with vertices and edges in the specified format.

**Response:**
```json
{
  "success": true,
  "data": {
    "vertices": [
      {"id": "node_0", "name": "Intersection 1"}
    ],
    "edges": [
      {"from": "node_0", "to": "node_1", "weight": 0.45}
    ]
  }
}
```

#### Get Current Traffic State
```
GET /api/traffic/current
```

Returns complete state including graph, incidents, and configuration.

**Response:**
```json
{
  "success": true,
  "data": {
    "vertices": [...],
    "edges": [...],
    "incidents": [...],
    "config": {...},
    "updateCount": 42,
    "timestamp": 1698765432123
  }
}
```

#### Get Specific Vertex Data
```
GET /api/traffic/vertex/:id
```

Returns data for a specific vertex (intersection).

**Example:** `GET /api/traffic/vertex/node_5`

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "node_5",
    "name": "Intersection 6",
    "x": 450.2,
    "y": 320.8
  }
}
```

#### Get Specific Edge Data
```
GET /api/traffic/edge/:id
```

Returns traffic data for a specific edge (road).

**Example:** `GET /api/traffic/edge/edge_10`

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "edge_10",
    "from": "node_3",
    "to": "node_7",
    "weight": 0.72,
    "distance": 15,
    "speed": 20,
    "vehicleCount": 68,
    "isIncident": false,
    "incidentSeverity": 0,
    "bidirectional": true
  }
}
```

#### Get Traffic Statistics
```
GET /api/traffic/stats
```

Returns aggregate statistics about the traffic network.

**Response:**
```json
{
  "success": true,
  "data": {
    "totalVertices": 20,
    "totalEdges": 32,
    "averageTrafficLevel": "0.423",
    "totalVehicles": 2145,
    "averageSpeed": 35,
    "activeIncidents": 2,
    "updateCount": 156,
    "uptime": 156234
  }
}
```

#### Get Configuration
```
GET /api/config
```

Returns current API configuration.

#### Update Configuration
```
POST /api/config
Content-Type: application/json

{
  "nodeCount": 30,
  "roadDensity": 0.4,
  "updateInterval": 500,
  "baseTrafficLevel": 0.4,
  "trafficVariability": 0.3,
  "incidentProbability": 0.002
}
```

Updates the API configuration. Note: Changing node count or road density will reinitialize the graph.

#### Create Traffic Incident
```
POST /api/traffic/incident
Content-Type: application/json

{
  "edgeId": "edge_5",
  "severity": 0.8,
  "duration": 60000
}
```

Creates a traffic incident on a specific road/edge.

**Parameters:**
- `edgeId`: Edge ID where incident occurs
- `severity`: Incident severity (0-1)
- `duration`: Duration in milliseconds

#### Health Check
```
GET /health
```

Returns server health status.

### WebSocket API

Connect to: `ws://localhost:3000`

#### Initial Connection

Upon connection, the server sends the initial traffic state:

```json
{
  "type": "initial",
  "data": {
    "vertices": [...],
    "edges": [...],
    "incidents": [...],
    "config": {...}
  }
}
```

#### Real-time Updates

The server broadcasts traffic updates every second (configurable):

```json
{
  "type": "update",
  "data": {
    "vertices": [...],
    "edges": [...],
    "incidents": [...],
    "config": {...},
    "updateCount": 42,
    "timestamp": 1698765432123
  },
  "timestamp": 1698765432123
}
```

#### Client Messages

**Subscribe to Updates:**
```json
{
  "type": "subscribe"
}
```

**Update Configuration:**
```json
{
  "type": "configure",
  "config": {
    "baseTrafficLevel": 0.5
  }
}
```

## Data Structure

### Vertex (Node/Intersection)

Each vertex in the graph represents an intersection or node:

```json
{
  "id": "node_5",
  "name": "Intersection 6",
  "x": 450.2,
  "y": 320.8
}
```

### Edge (Road)

Each edge represents a road connecting two vertices:

```json
{
  "id": "edge_10",
  "from": "node_3",
  "to": "node_7",
  "weight": 0.72,              // Traffic level (0-1, 0=no traffic, 1=gridlock)
  "distance": 15,              // Road length in arbitrary units
  "speed": 20,                 // Average speed in mph
  "vehicleCount": 68,          // Number of vehicles on this road
  "isIncident": false,         // Whether there's an incident
  "incidentSeverity": 0,       // 0-1 severity level
  "bidirectional": true        // Whether traffic flows both ways
}
```

### Incident

```json
{
  "id": 1698765432123.456,
  "edgeId": "edge_5",
  "from": "node_3",
  "to": "node_7",
  "severity": 0.8,
  "startTime": 1698765432123,
  "endTime": 1698765492123,
  "type": "accident"
}
```

**Incident Types:**
- `accident`
- `construction`
- `roadblock`
- `weather`
- `event`

## Traffic Simulation Features

### Time-Based Patterns

The system simulates realistic traffic patterns:
- **Morning Rush** (7-9 AM): 1.5x traffic multiplier
- **Evening Rush** (5-7 PM): 1.6x traffic multiplier
- **Night Time** (11 PM - 5 AM): 0.4x traffic multiplier

### Connected Road Flow

Traffic levels in each road are influenced by connected roads, creating realistic traffic flow patterns through the network.

### Random Incidents

Incidents occur randomly based on the configured probability and affect the road and connected roads.

## Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `nodeCount` | 20 | Number of vertices (intersections) in the graph |
| `roadDensity` | 0.3 | Connection probability between nodes |
| `updateInterval` | 1000 | Update interval in milliseconds |
| `baseTrafficLevel` | 0.3 | Base traffic level (0-1) |
| `trafficVariability` | 0.2 | Traffic variability factor |
| `incidentProbability` | 0.001 | Probability of incident per edge per update |

## Visualization

### Graph Client

Open `graph-client.html` in your browser to see an interactive visualization of the traffic network:

- **Blue dots**: Intersections/vertices
- **Colored lines**: Roads/edges (color indicates traffic level)
- **Red markers**: Active incidents
- Click on nodes or roads to see detailed information
- Real-time updates as traffic conditions change

## Example Usage

### Using curl

```bash
# Get the graph structure
curl http://localhost:3000/api/traffic/graph

# Get statistics
curl http://localhost:3000/api/traffic/stats

# Create an incident
curl -X POST http://localhost:3000/api/traffic/incident \
  -H "Content-Type: application/json" \
  -d '{"edgeId": "edge_5", "severity": 0.9, "duration": 60000}'
```

### Using JavaScript/WebSocket

```javascript
const ws = new WebSocket('ws://localhost:3000');

ws.onopen = () => {
  ws.send(JSON.stringify({ type: 'subscribe' }));
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  if (message.type === 'update') {
    console.log('Graph update:', message.data);
    // message.data.vertices - array of nodes
    // message.data.edges - array of roads with traffic data
  }
};
```

## License

ISC
