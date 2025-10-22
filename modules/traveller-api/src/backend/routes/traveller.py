import uuid
from typing import List
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from temporalio.client import WorkflowFailureError

from ..utils import log
from ..workflows.traveller import TravellerWorkflow, TravellerInput, TravellerState

logger = log.get_logger(__name__)
router = APIRouter()

class CreateTravellerRequest(BaseModel):
    start_node: str
    end_node: str

class CreateTravellerResponse(BaseModel):
    workflow_id: str
    message: str

@router.post("/create-traveller", response_model=CreateTravellerResponse)
async def create_traveller(request: Request, traveller_request: CreateTravellerRequest):
    """Create a new traveller workflow."""
    temporal_client = request.app.state.temporal_client
    workflow_id = f"traveller-{uuid.uuid4()}"
    
    logger.info(f"Creating traveller from {traveller_request.start_node} to {traveller_request.end_node}")
    
    try:
        # Create workflow input
        workflow_input = TravellerInput(
            start_node=traveller_request.start_node,
            end_node=traveller_request.end_node,
            workflow_id=workflow_id
        )
        
        # Start the workflow
        handle = await temporal_client.start_workflow(
            TravellerWorkflow.run,
            workflow_input,
            id=workflow_id,
            task_queue=temporal_client._config.task_queue,
        )
        
        return CreateTravellerResponse(
            workflow_id=workflow_id,
            message=f"Traveller created from {traveller_request.start_node} to {traveller_request.end_node}"
        )
    except Exception as e:
        logger.error(f"Error creating traveller: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/interrupt-travellers")
async def interrupt_travellers(request: Request):
    """Interrupt all current travellers to recalculate their routes."""
    temporal_client = request.app.state.temporal_client
    
    try:
        # List all running workflows with the traveller prefix
        workflows = temporal_client.list_workflows(query='WorkflowId STARTS_WITH "traveller-" AND ExecutionStatus="Running"')
        
        interrupted_count = 0
        async for workflow in workflows:
            try:
                handle = temporal_client.get_workflow_handle(workflow.id)
                # Send interrupt signal
                await handle.signal(TravellerWorkflow.interrupt)
                interrupted_count += 1
                logger.info(f"Interrupted workflow {workflow.id}")
            except Exception as e:
                logger.warning(f"Failed to interrupt workflow {workflow.id}: {e}")
        
        return {
            "interrupted_count": interrupted_count,
            "message": f"Interrupted {interrupted_count} traveller(s)"
        }
    except Exception as e:
        logger.error(f"Error interrupting travellers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get-travellers", response_model=List[TravellerState])
async def get_travellers(request: Request):
    """Get the current position of all travellers."""
    temporal_client = request.app.state.temporal_client
    
    try:
        # List all workflows with the traveller prefix
        workflows = temporal_client.list_workflows(query='WorkflowId STARTS_WITH "traveller-"')
        
        travellers = []
        async for workflow in workflows:
            try:
                handle = temporal_client.get_workflow_handle(workflow.id)
                # Query the current state
                state = await handle.query(TravellerWorkflow.get_state)
                travellers.append(state)
            except WorkflowFailureError:
                # Workflow has failed, skip it
                logger.warning(f"Workflow {workflow.id} has failed")
            except Exception as e:
                logger.warning(f"Failed to query workflow {workflow.id}: {e}")
        
        return travellers
    except Exception as e:
        logger.error(f"Error getting travellers: {e}")
        raise HTTPException(status_code=500, detail=str(e))
