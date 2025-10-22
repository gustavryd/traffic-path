"""Traveller Temporal workflow for navigating a graph."""

from datetime import timedelta
from typing import List

from pydantic import BaseModel
from temporalio import activity, workflow


class TravellerInput(BaseModel):
    """Input for starting a traveller workflow."""
    start_node: str
    end_node: str
    workflow_id: str


class TravellerState(BaseModel):
    """Current state of a traveller."""
    workflow_id: str
    current_node: str
    end_node: str
    route: List[str]
    route_index: int
    status: str  # "Walking" or "Finished"


@activity.defn
async def fetch_traffic_model() -> dict:
    """Fetch traffic model from traffic-api (Node.js server on host)."""
    import httpx
    activity.logger.info("Fetching traffic model from traffic-api")
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Traffic generator is Node.js on host at port 3000
        response = await client.get("http://host.docker.internal:3000/api/traffic/current")
        response.raise_for_status()
        return response.json()


@activity.defn
async def fetch_route(start_node: str, end_node: str) -> dict:
    """Fetch route from graph-api."""
    import httpx
    activity.logger.info(f"Fetching route from {start_node} to {end_node}")
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Graph API is a Polytope service
        response = await client.post(
            "http://graph-api:3030/shortest-path",
            json={"start_node": start_node, "end_node": end_node}
        )
        response.raise_for_status()
        return response.json()


@workflow.defn
class TravellerWorkflow:
    """Workflow for a traveller navigating through a graph."""

    def __init__(self):
        self.current_node: str = ""
        self.end_node: str = ""
        self.route: List[str] = []
        self.route_index: int = 0
        self.status: str = "Walking"
        self.workflow_id: str = ""
        self.interrupted: bool = False

    @workflow.run
    async def run(self, input: TravellerInput) -> TravellerState:
        """Main workflow execution."""
        workflow.logger.info(f"Starting traveller from {input.start_node} to {input.end_node}")
        
        self.workflow_id = input.workflow_id
        self.current_node = input.start_node
        self.end_node = input.end_node
        
        # Initial route calculation
        await self._calculate_route()
        
        # Walk the route
        while self.route_index < len(self.route):
            # Check if interrupted
            if self.interrupted:
                workflow.logger.info("Traveller interrupted, recalculating route")
                await self._calculate_route()
                self.interrupted = False
                continue
            
            # Move to next node
            self.current_node = self.route[self.route_index]
            workflow.logger.info(f"At node: {self.current_node}")
            
            # Check if we reached the end
            if self.current_node == self.end_node:
                self.status = "Finished"
                workflow.logger.info("Reached destination")
                break
            
            # Wait 1 second before next step
            await workflow.sleep(1)
            self.route_index += 1
        
        return self.get_state()
    
    async def _calculate_route(self):
        """Calculate route from current position to end."""
        # Fetch traffic model
        traffic_model = await workflow.execute_activity(
            fetch_traffic_model,
            start_to_close_timeout=timedelta(seconds=30),
        )
        
        # Fetch route
        route_data = await workflow.execute_activity(
            fetch_route,
            args=[self.current_node, self.end_node],
            start_to_close_timeout=timedelta(seconds=30),
        )
        
        self.route = route_data.get("route", [])
        self.route_index = 0
        workflow.logger.info(f"New route calculated: {self.route}")
    
    @workflow.signal
    async def interrupt(self):
        """Signal to interrupt and recalculate route."""
        workflow.logger.info("Received interrupt signal")
        self.interrupted = True
    
    @workflow.query
    def get_state(self) -> TravellerState:
        """Query current state of the traveller."""
        return TravellerState(
            workflow_id=self.workflow_id,
            current_node=self.current_node,
            end_node=self.end_node,
            route=self.route,
            route_index=self.route_index,
            status=self.status
        )
