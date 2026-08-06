from fastapi import APIRouter
from backend.schemas import CopilotRequest, CopilotResponse

router = APIRouter()


@router.post("/", response_model=CopilotResponse)
def query_copilot(req: CopilotRequest):
    """Natural language query over the opportunity dataset."""
    # TODO: load scored_df, call ai.copilot.run_query
    return CopilotResponse(narrative="", results=[])
