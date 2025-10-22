# Workflow and Activity Registry
from .traveller import TravellerWorkflow, fetch_traffic_model, fetch_route

WORKFLOWS = [
    TravellerWorkflow,
]

ACTIVITIES = [
    fetch_traffic_model,
    fetch_route,
]
