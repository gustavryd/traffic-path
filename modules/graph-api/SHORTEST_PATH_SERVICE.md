# Shortest Path Service

A REST API service for finding the shortest path between two vertices in a weighted directed graph using Dijkstra's algorithm.

## Overview

This service provides an efficient implementation of Dijkstra's shortest path algorithm, designed to find the optimal path between any two vertices in a graph where:
- Vertices have unique string IDs and human-readable names
- Edges are directed and have positive weights
- The graph may be disconnected (no path exists between some vertices)

## API Endpoint

### POST `/graph/shortest-path`

Finds the shortest path between two vertices in a provided graph.

**Request Body:**
```json
{
  "graph": {
    "vertices": [
      {"id": "A", "name": "City A"},
      {"id": "B", "name": "City B"},
      {"id": "C", "name": "City C"}
    ],
    "edges": [
      {"from": "A", "to": "B", "weight": 1.5},
      {"from": "B", "to": "C", "weight": 2.0}
    ]
  },
  "start": "A",
  "end": "C"
}
```

**Response (Success - 200):**
```json
{
  "path": ["A", "B", "C"],
  "vertices": [
    {"id": "A", "name": "City A"},
    {"id": "B", "name": "City B"},
    {"id": "C", "name": "City C"}
  ],
  "total_distance": 3.5,
  "success": true,
  "message": "Found shortest path with distance 3.5"
}
```

**Response (No Path - 404):**
```json
{
  "detail": "No path found between 'A' and 'C'"
}
```

**Response (Invalid Input - 404):**
```json
{
  "detail": "Start vertex 'X' not found in graph"
}
```

## Data Models

### Vertex
```python
{
  "id": str,      # Unique identifier
  "name": str     # Human-readable name
}
```

### Edge
```python
{
  "from": str,    # Source vertex ID
  "to": str,      # Destination vertex ID
  "weight": float # Positive weight (distance, cost, etc.)
}
```

### Graph
```python
{
  "vertices": List[Vertex],
  "edges": List[Edge]
}
```

## Algorithm

The service uses **Dijkstra's algorithm** for finding the shortest path:

1. **Initialization**: Set distance to start vertex as 0, all others as infinity
2. **Priority Queue**: Process vertices in order of their current shortest distance
3. **Relaxation**: For each vertex, update distances to neighbors if a shorter path is found
4. **Path Reconstruction**: Trace back from end to start using predecessor pointers
5. **Optimization**: Early termination when destination is reached

**Time Complexity**: O((V + E) log V) where V = vertices, E = edges
**Space Complexity**: O(V + E)

## Features

✅ **Efficient pathfinding** using Dijkstra's algorithm with priority queue
✅ **Complete path details** including vertex information and total distance
✅ **Error handling** for invalid vertices and disconnected graphs
✅ **Directed graphs** support
✅ **Weighted edges** with positive weights
✅ **Hot reload** during development for instant updates

## Usage Examples

### Example 1: Simple Path
```bash
curl -X POST http://localhost:3030/graph/shortest-path \
  -H "Content-Type: application/json" \
  -d '{
    "graph": {
      "vertices": [
        {"id": "A", "name": "Start"},
        {"id": "B", "name": "Middle"},
        {"id": "C", "name": "End"}
      ],
      "edges": [
        {"from": "A", "to": "B", "weight": 1},
        {"from": "B", "to": "C", "weight": 2}
      ]
    },
    "start": "A",
    "end": "C"
  }'
```

### Example 2: Multiple Paths (Finds Shortest)
```bash
curl -X POST http://localhost:3030/graph/shortest-path \
  -H "Content-Type: application/json" \
  -d '{
    "graph": {
      "vertices": [
        {"id": "A", "name": "Start"},
        {"id": "B", "name": "Route 1"},
        {"id": "C", "name": "Route 2"},
        {"id": "D", "name": "End"}
      ],
      "edges": [
        {"from": "A", "to": "B", "weight": 1},
        {"from": "B", "to": "D", "weight": 5},
        {"from": "A", "to": "C", "weight": 2},
        {"from": "C", "to": "D", "weight": 1}
      ]
    },
    "start": "A",
    "end": "D"
  }'
```
Result: Path A → C → D (distance: 3) instead of A → B → D (distance: 6)

### Example 3: Python Client
```python
import requests

response = requests.post('http://localhost:3030/graph/shortest-path', json={
    "graph": {
        "vertices": [
            {"id": "home", "name": "Home"},
            {"id": "work", "name": "Work"},
            {"id": "store", "name": "Store"}
        ],
        "edges": [
            {"from": "home", "to": "work", "weight": 5.2},
            {"from": "work", "to": "store", "weight": 3.1}
        ]
    },
    "start": "home",
    "end": "store"
})

result = response.json()
print(f"Path: {' → '.join(result['path'])}")
print(f"Total distance: {result['total_distance']}")
```

## Testing

Run the included example script:
```bash
cd modules/graph-api
python examples/shortest_path_example.py
```

This runs three test scenarios:
1. Simple graph with direct path
2. Disconnected graph (no path exists)
3. Complex network routing scenario

## Interactive API Documentation

Visit the auto-generated API documentation at:
- Swagger UI: http://localhost:3030/docs
- ReDoc: http://localhost:3030/redoc

These provide interactive testing and detailed schema documentation.

## Use Cases

- **Route Planning**: Find shortest routes between locations
- **Network Routing**: Optimize data packet paths through networks
- **Supply Chain**: Minimize transportation costs
- **Game Pathfinding**: Calculate optimal movement paths
- **Social Networks**: Find shortest connection paths between users
- **Logistics**: Optimize delivery routes

## Architecture

```
modules/graph-api/
├── src/backend/
│   ├── models/
│   │   └── graph.py           # Data models (Vertex, Edge, Graph)
│   ├── services/
│   │   └── shortest_path.py   # Dijkstra's algorithm implementation
│   ├── routes/
│   │   └── graph.py           # API endpoints
│   └── main.py                # FastAPI app with route registration
└── examples/
    └── shortest_path_example.py  # Usage examples
```

## Limitations

- **Edge weights must be positive** (Dijkstra's algorithm requirement)
- **Directed graphs only** (edges are one-way)
- **In-memory processing** (graph is sent with each request)
- For very large graphs (>10,000 vertices), consider using specialized graph databases

## Development

The service runs with hot reload enabled. After making changes to any Python file, check the logs:

```bash
# Using Polytope MCP tools
__polytope__get_container_logs(container: graph-api, limit: 50)
```

Look for successful reload messages or any errors.

## API Server Information

- **Port**: 3030
- **Host**: localhost
- **Framework**: FastAPI
- **Hot Reload**: Enabled in development
- **Container**: graph-api

## Support

For issues or questions, check:
1. Container logs for errors
2. API documentation at `/docs`
3. Example scripts in `examples/`
