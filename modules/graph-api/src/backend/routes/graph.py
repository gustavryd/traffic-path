from fastapi import APIRouter, HTTPException
from ..models.graph import ShortestPathRequest, ShortestPathResponse
from ..services.shortest_path import ShortestPathService

router = APIRouter(prefix="/graph", tags=["graph"])


@router.post("/shortest-path", response_model=ShortestPathResponse)
async def find_shortest_path(request: ShortestPathRequest) -> ShortestPathResponse:
    """
    Find the shortest path between two vertices in a graph.
    
    Uses Dijkstra's algorithm to compute the shortest path.
    
    - **graph**: The graph containing vertices and edges
    - **start**: The starting vertex id
    - **end**: The ending vertex id
    
    Returns the shortest path with vertex details and total distance.
    """
    try:
        result = ShortestPathService.find_shortest_path(
            graph=request.graph,
            start_id=request.start,
            end_id=request.end
        )
        
        if not result.success:
            raise HTTPException(status_code=404, detail=result.message)
        
        return result
    except HTTPException:
        # Re-raise HTTPExceptions without wrapping them
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error computing shortest path: {str(e)}")
