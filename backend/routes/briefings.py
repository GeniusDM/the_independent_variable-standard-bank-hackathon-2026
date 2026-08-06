from fastapi import APIRouter, HTTPException
from backend.schemas import BriefingRequest, BriefingResponse

router = APIRouter()


@router.post("/", response_model=BriefingResponse)
def generate_briefing(req: BriefingRequest):
    """Generates a GenAI briefing note for a given client."""
    # TODO: load client row from processed data, call ai.briefing.generate_briefing
    raise HTTPException(status_code=501, detail="Not yet implemented")
