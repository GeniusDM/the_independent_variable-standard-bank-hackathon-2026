from __future__ import annotations

from fastapi import APIRouter

from backend.routes.wallet import _summary_from_row
from backend.schemas import ClientSummary
from models.explainability import add_explainability_fields
from models.opportunity_engine import build_scored_dataset

router = APIRouter()


@router.get("/opportunities", response_model=list[ClientSummary])
def get_opportunities():
    df = add_explainability_fields(build_scored_dataset())
    return [_summary_from_row(row) for _, row in df.iterrows()]
