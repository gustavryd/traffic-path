from typing import Optional
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel, Field

from ..utils import log

logger = log.get_logger(__name__)
router = APIRouter(prefix="/api/traffic", tags=["traffic"])


class IncidentCreateRequest(BaseModel):
    edgeId: str = Field(..., description="The edge ID where the incident should occur")
    severity: Optional[float] = Field(0.5, ge=0.0, le=1.0, description="Incident severity (0-1)")
    duration: Optional[float] = Field(60000, ge=10000, le=3600000, description="Duration in milliseconds")
    type: Optional[str] = Field(None, description="Incident type (accident, construction, roadblock, weather, event)")


class ConfigUpdateRequest(BaseModel):
    node_count: Optional[int] = Field(None, ge=1, le=100)
    update_interval: Optional[int] = Field(None, ge=1000, le=300000)
    base_traffic_level: Optional[float] = Field(None, ge=0.0, le=1.0)
    traffic_variability: Optional[float] = Field(None, ge=0.0, le=1.0)
    incident_probability: Optional[float] = Field(None, ge=0.0, le=1.0)
    road_density: Optional[float] = Field(None, ge=0.0, le=1.0)


@router.get("/current")
async def get_current_traffic(request: Request):
    """Get current traffic state (graph structure)."""
    try:
        traffic_generator = request.app.state.traffic_generator
        state = traffic_generator.get_current_state()
        return {"success": True, "data": state}
    except Exception as e:
        logger.error(f"Error getting current traffic: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/graph")
async def get_graph_data(request: Request):
    """Get graph data in specific format."""
    try:
        traffic_generator = request.app.state.traffic_generator
        state = traffic_generator.get_current_state()
        return {
            "success": True,
            "data": {
                "vertices": state["vertices"],
                "edges": state["edges"]
            }
        }
    except Exception as e:
        logger.error(f"Error getting graph data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/vertex/{vertex_id}")
async def get_vertex_data(request: Request, vertex_id: str):
    """Get specific vertex data."""
    try:
        traffic_generator = request.app.state.traffic_generator
        vertex_data = traffic_generator.get_vertex_data(vertex_id)
        
        if vertex_data:
            return {"success": True, "data": vertex_data}
        else:
            raise HTTPException(status_code=404, detail="Vertex not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting vertex data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/edge/{edge_id}")
async def get_edge_data(request: Request, edge_id: str):
    """Get specific edge data."""
    try:
        traffic_generator = request.app.state.traffic_generator
        edge_data = traffic_generator.get_edge_data(edge_id)
        
        if edge_data:
            return {"success": True, "data": edge_data}
        else:
            raise HTTPException(status_code=404, detail="Edge not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting edge data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/edges")
async def get_all_edges(request: Request):
    """Get all edges (roads)."""
    try:
        traffic_generator = request.app.state.traffic_generator
        edges = traffic_generator.get_all_edges()
        return {"success": True, "data": edges}
    except Exception as e:
        logger.error(f"Error getting edges: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/edges/available")
async def get_available_edges(request: Request):
    """Get available edges for incident creation (edges without active incidents)."""
    try:
        traffic_generator = request.app.state.traffic_generator
        available_edges = traffic_generator.get_available_edges_for_incident()
        return {
            "success": True,
            "data": available_edges,
            "count": len(available_edges)
        }
    except Exception as e:
        logger.error(f"Error getting available edges: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/incidents")
async def get_active_incidents(request: Request):
    """Get all active incidents."""
    try:
        traffic_generator = request.app.state.traffic_generator
        incidents = traffic_generator.get_active_incidents()
        return {
            "success": True,
            "data": incidents,
            "count": len(incidents)
        }
    except Exception as e:
        logger.error(f"Error getting active incidents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/incident")
async def create_incident(request: Request, incident_request: IncidentCreateRequest):
    """Create traffic incident on an edge (road)."""
    try:
        traffic_generator = request.app.state.traffic_generator
        
        incident = traffic_generator.create_incident(
            incident_request.edgeId,
            incident_request.severity,
            incident_request.duration,
            incident_request.type
        )
        
        return {
            "success": True,
            "message": "Incident created successfully",
            "data": incident
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating incident: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/incident/{incident_id}")
async def clear_incident(request: Request, incident_id: str):
    """Clear a specific incident manually."""
    try:
        traffic_generator = request.app.state.traffic_generator
        cleared_incident = traffic_generator.clear_incident(incident_id)
        
        return {
            "success": True,
            "message": "Incident cleared successfully",
            "data": cleared_incident
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error clearing incident: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_traffic_stats(request: Request):
    """Get traffic statistics."""
    try:
        traffic_generator = request.app.state.traffic_generator
        stats = traffic_generator.get_stats()
        return {"success": True, "data": stats}
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config")
async def get_config(request: Request):
    """Get configuration."""
    try:
        traffic_generator = request.app.state.traffic_generator
        config = traffic_generator.get_config()
        return {"success": True, "data": config}
    except Exception as e:
        logger.error(f"Error getting config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/config")
async def update_config(request: Request, config_request: ConfigUpdateRequest):
    """Update configuration."""
    try:
        traffic_generator = request.app.state.traffic_generator
        
        # Convert to dict and filter out None values
        config_dict = {k: v for k, v in config_request.model_dump().items() if v is not None}
        
        traffic_generator.update_config(config_dict)
        updated_config = traffic_generator.get_config()
        
        return {"success": True, "data": updated_config}
    except Exception as e:
        logger.error(f"Error updating config: {e}")
        raise HTTPException(status_code=400, detail=str(e))
