"""
Example usage of the shortest path service.

This demonstrates how to call the API endpoint with various graph configurations.
"""

import requests
import json

# API endpoint
API_URL = "http://localhost:3030/graph/shortest-path"


def example_simple_graph():
    """
    Example with a simple graph:
    
    A --1--> B --2--> C
    |        |        |
    4        3        1
    |        |        |
    v        v        v
    D --1--> E --2--> F
    """
    request_data = {
        "graph": {
            "vertices": [
                {"id": "A", "name": "City A"},
                {"id": "B", "name": "City B"},
                {"id": "C", "name": "City C"},
                {"id": "D", "name": "City D"},
                {"id": "E", "name": "City E"},
                {"id": "F", "name": "City F"}
            ],
            "edges": [
                {"from": "A", "to": "B", "weight": 1},
                {"from": "B", "to": "C", "weight": 2},
                {"from": "A", "to": "D", "weight": 4},
                {"from": "B", "to": "E", "weight": 3},
                {"from": "C", "to": "F", "weight": 1},
                {"from": "D", "to": "E", "weight": 1},
                {"from": "E", "to": "F", "weight": 2}
            ]
        },
        "start": "A",
        "end": "F"
    }
    
    print("Example 1: Simple Graph (A to F)")
    print("=" * 50)
    response = requests.post(API_URL, json=request_data)
    result = response.json()
    
    print(f"Status: {response.status_code}")
    print(f"Path: {' -> '.join(result['path'])}")
    print(f"Total Distance: {result['total_distance']}")
    print(f"Message: {result['message']}")
    print("\nVertex Details:")
    for vertex in result['vertices']:
        print(f"  - {vertex['id']}: {vertex['name']}")
    print()


def example_disconnected_graph():
    """
    Example with a disconnected graph (no path exists).
    
    A --1--> B       C --1--> D
    """
    request_data = {
        "graph": {
            "vertices": [
                {"id": "A", "name": "Island A"},
                {"id": "B", "name": "Island B"},
                {"id": "C", "name": "Island C"},
                {"id": "D", "name": "Island D"}
            ],
            "edges": [
                {"from": "A", "to": "B", "weight": 1},
                {"from": "C", "to": "D", "weight": 1}
            ]
        },
        "start": "A",
        "end": "D"
    }
    
    print("Example 2: Disconnected Graph (A to D - No Path)")
    print("=" * 50)
    response = requests.post(API_URL, json=request_data)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 404:
        print(f"Error: {response.json()['detail']}")
    print()


def example_complex_graph():
    """
    Example with a more complex graph with multiple possible paths.
    
    Network routing scenario with different connection costs.
    """
    request_data = {
        "graph": {
            "vertices": [
                {"id": "router1", "name": "Main Router"},
                {"id": "router2", "name": "Backup Router"},
                {"id": "router3", "name": "Edge Router"},
                {"id": "server1", "name": "Web Server"},
                {"id": "server2", "name": "API Server"},
                {"id": "db", "name": "Database"}
            ],
            "edges": [
                {"from": "router1", "to": "router2", "weight": 5},
                {"from": "router1", "to": "server1", "weight": 10},
                {"from": "router2", "to": "router3", "weight": 3},
                {"from": "router2", "to": "server1", "weight": 2},
                {"from": "router3", "to": "server2", "weight": 4},
                {"from": "server1", "to": "server2", "weight": 1},
                {"from": "server2", "to": "db", "weight": 2}
            ]
        },
        "start": "router1",
        "end": "db"
    }
    
    print("Example 3: Network Routing (router1 to database)")
    print("=" * 50)
    response = requests.post(API_URL, json=request_data)
    result = response.json()
    
    print(f"Status: {response.status_code}")
    print(f"Optimal Route: {' -> '.join(result['path'])}")
    print(f"Total Latency: {result['total_distance']} ms")
    print(f"Message: {result['message']}")
    print("\nRoute Details:")
    for vertex in result['vertices']:
        print(f"  - {vertex['id']}: {vertex['name']}")
    print()


def main():
    """Run all examples."""
    print("\n" + "=" * 50)
    print("SHORTEST PATH SERVICE EXAMPLES")
    print("=" * 50 + "\n")
    
    try:
        example_simple_graph()
        example_disconnected_graph()
        example_complex_graph()
        
        print("=" * 50)
        print("All examples completed!")
        print("=" * 50)
        
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to the API.")
        print("Make sure the server is running at http://localhost:3030")
    except Exception as e:
        print(f"ERROR: {e}")


if __name__ == "__main__":
    main()
