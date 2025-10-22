# Quick Start Guide - Shortest Path Service

The service is **already running** at `http://localhost:3030`. Here are several ways to access it:

## 1. Interactive Web Interface (Easiest)

Open your browser and go to:
```
http://localhost:3030/docs
```

This provides a **Swagger UI** where you can:
- See all endpoints
- Try out the API directly in your browser
- View request/response examples

### How to use the Swagger UI:
1. Click on `POST /graph/shortest-path`
2. Click "Try it out"
3. Edit the example JSON in the request body
4. Click "Execute"
5. See the response below

## 2. Command Line (curl)

### Simple Example
```bash
curl -X POST http://localhost:3030/graph/shortest-path \
  -H "Content-Type: application/json" \
  -d '{
    "graph": {
      "vertices": [
        {"id": "A", "name": "City A"},
        {"id": "B", "name": "City B"},
        {"id": "C", "name": "City C"}
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

### Pretty Print Response (with jq)
```bash
curl -X POST http://localhost:3030/graph/shortest-path \
  -H "Content-Type: application/json" \
  -d '{
    "graph": {
      "vertices": [
        {"id": "A", "name": "City A"},
        {"id": "B", "name": "City B"},
        {"id": "C", "name": "City C"}
      ],
      "edges": [
        {"from": "A", "to": "B", "weight": 1},
        {"from": "B", "to": "C", "weight": 2}
      ]
    },
    "start": "A",
    "end": "C"
  }' | jq
```

## 3. Python Script

### Using the Example Script
```bash
cd modules/graph-api
python3 examples/shortest_path_example.py
```

### Custom Python Code
```python
import requests

# Define your graph
request_data = {
    "graph": {
        "vertices": [
            {"id": "home", "name": "Home"},
            {"id": "work", "name": "Work"},
            {"id": "gym", "name": "Gym"}
        ],
        "edges": [
            {"from": "home", "to": "work", "weight": 5.0},
            {"from": "home", "to": "gym", "weight": 2.0},
            {"from": "gym", "to": "work", "weight": 4.0}
        ]
    },
    "start": "home",
    "end": "work"
}

# Call the API
response = requests.post(
    'http://localhost:3030/graph/shortest-path',
    json=request_data
)

# Print results
result = response.json()
print(f"Path: {' → '.join(result['path'])}")
print(f"Distance: {result['total_distance']}")
print(f"Vertices: {[v['name'] for v in result['vertices']]}")
```

## 4. Using Any HTTP Client

The service accepts standard HTTP POST requests, so you can use:
- **Postman**: Import as POST request to `http://localhost:3030/graph/shortest-path`
- **Insomnia**: Same endpoint
- **HTTPie**: `http POST localhost:3030/graph/shortest-path < request.json`
- Any programming language with HTTP support

## Request Format

```json
{
  "graph": {
    "vertices": [
      {"id": "vertex_id", "name": "Vertex Name"}
    ],
    "edges": [
      {"from": "source_id", "to": "destination_id", "weight": 1.5}
    ]
  },
  "start": "starting_vertex_id",
  "end": "ending_vertex_id"
}
```

## Response Format

### Success (200):
```json
{
  "path": ["A", "B", "C"],
  "vertices": [
    {"id": "A", "name": "City A"},
    {"id": "B", "name": "City B"},
    {"id": "C", "name": "City C"}
  ],
  "total_distance": 3.0,
  "success": true,
  "message": "Found shortest path with distance 3.0"
}
```

### No Path Found (404):
```json
{
  "detail": "No path found between 'A' and 'C'"
}
```

## Test if Service is Running

```bash
curl http://localhost:3030/health
```

Should return: `{"status":"ok"}`

## Other Useful Endpoints

- **API Docs**: http://localhost:3030/docs
- **Alternative Docs**: http://localhost:3030/redoc  
- **Health Check**: http://localhost:3030/health
- **OpenAPI Schema**: http://localhost:3030/openapi.json

## Need Help?

See the full documentation: `modules/graph-api/SHORTEST_PATH_SERVICE.md`
