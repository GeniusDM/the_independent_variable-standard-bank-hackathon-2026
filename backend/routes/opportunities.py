from fastapi import APIRouter, Query
from backend.schemas import OpportunityRank

router = APIRouter()


@router.get("/", response_model=list[OpportunityRank])
def get_opportunities(top_n: int = Query(default=10, le=50)):
    """Returns top-N ranked growth opportunities."""
    # TODO: load from processed/opportunity_ranking.csv
    return []
