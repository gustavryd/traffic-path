import heapq
from typing import Dict, List, Optional, Tuple
from ..models.graph import Graph, Vertex, Edge, ShortestPathResponse


class ShortestPathService:
    """Service for computing shortest paths in graphs using Dijkstra's algorithm."""

    @staticmethod
    def find_shortest_path(
        graph: Graph,
        start_id: str,
        end_id: str
    ) -> ShortestPathResponse:
        """
        Find the shortest path between two vertices using Dijkstra's algorithm.
        
        Args:
            graph: The graph containing vertices and edges
            start_id: The id of the starting vertex
            end_id: The id of the ending vertex
            
        Returns:
            ShortestPathResponse containing the path, vertices, and total distance
        """
        # Validate that start and end vertices exist
        vertex_map = {v.id: v for v in graph.vertices}
        
        if start_id not in vertex_map:
            return ShortestPathResponse(
                path=[],
                vertices=[],
                total_distance=float('inf'),
                success=False,
                message=f"Start vertex '{start_id}' not found in graph"
            )
        
        if end_id not in vertex_map:
            return ShortestPathResponse(
                path=[],
                vertices=[],
                total_distance=float('inf'),
                success=False,
                message=f"End vertex '{end_id}' not found in graph"
            )
        
        # Build adjacency list from edges
        adjacency: Dict[str, List[Tuple[str, float]]] = {v.id: [] for v in graph.vertices}
        for edge in graph.edges:
            adjacency[edge.from_vertex].append((edge.to_vertex, edge.weight))
        
        # Dijkstra's algorithm
        distances: Dict[str, float] = {v.id: float('inf') for v in graph.vertices}
        distances[start_id] = 0
        previous: Dict[str, Optional[str]] = {v.id: None for v in graph.vertices}
        
        # Priority queue: (distance, vertex_id)
        pq = [(0, start_id)]
        visited = set()
        
        while pq:
            current_distance, current_vertex = heapq.heappop(pq)
            
            # Skip if we've already processed this vertex
            if current_vertex in visited:
                continue
            
            visited.add(current_vertex)
            
            # If we reached the destination, we can stop
            if current_vertex == end_id:
                break
            
            # Skip if this distance is outdated
            if current_distance > distances[current_vertex]:
                continue
            
            # Check all neighbors
            for neighbor, weight in adjacency[current_vertex]:
                distance = current_distance + weight
                
                # If we found a shorter path, update it
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous[neighbor] = current_vertex
                    heapq.heappush(pq, (distance, neighbor))
        
        # Reconstruct the path
        if distances[end_id] == float('inf'):
            return ShortestPathResponse(
                path=[],
                vertices=[],
                total_distance=float('inf'),
                success=False,
                message=f"No path found between '{start_id}' and '{end_id}'"
            )
        
        # Build the path by following previous pointers
        path = []
        current = end_id
        while current is not None:
            path.append(current)
            current = previous[current]
        path.reverse()
        
        # Get vertex details for the path
        path_vertices = [vertex_map[vertex_id] for vertex_id in path]
        
        return ShortestPathResponse(
            path=path,
            vertices=path_vertices,
            total_distance=distances[end_id],
            success=True,
            message=f"Found shortest path with distance {distances[end_id]}"
        )
