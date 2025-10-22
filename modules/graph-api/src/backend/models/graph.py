from pydantic import BaseModel, Field
from typing import Dict, List, Optional


class Vertex(BaseModel):
    """Represents a vertex in the graph with an id and name."""
    id: str = Field(..., description="Unique identifier for the vertex")
    name: str = Field(..., description="Human-readable name for the vertex")


class Edge(BaseModel):
    """Represents a weighted edge connecting two vertices."""
    from_vertex: str = Field(..., alias="from", description="Source vertex id")
    to_vertex: str = Field(..., alias="to", description="Destination vertex id")
    weight: float = Field(..., gt=0, description="Weight of the edge (must be positive)")

    class Config:
        populate_by_name = True


class Graph(BaseModel):
    """Represents a complete graph with vertices and edges."""
    vertices: List[Vertex] = Field(..., description="List of all vertices in the graph")
    edges: List[Edge] = Field(..., description="List of all edges in the graph")


class ShortestPathRequest(BaseModel):
    """Request model for finding the shortest path between two vertices."""
    graph: Graph = Field(..., description="The graph to search")
    start: str = Field(..., description="Starting vertex id")
    end: str = Field(..., description="Ending vertex id")


class ShortestPathResponse(BaseModel):
    """Response model containing the shortest path result."""
    path: List[str] = Field(..., description="Ordered list of vertex ids in the shortest path")
    vertices: List[Vertex] = Field(..., description="Vertex details for each vertex in the path")
    total_distance: float = Field(..., description="Total distance/weight of the path")
    success: bool = Field(..., description="Whether a path was found")
    message: Optional[str] = Field(None, description="Additional information or error message")
