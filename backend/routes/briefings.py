from __future__ import annotations

from fastapi import APIRouter

from ai.briefing import generate_briefing
from backend.schemas import Briefing

router = APIRouter()


@router.get("/briefing/{client_id}", response_model=Briefing)
def get_briefing(client_id: str):
    payload = generate_briefing(client_id)
    return Briefing(
        clientId=payload["clientId"],
        summary=payload["summary"],
        keySignals=payload["keySignals"],
        recommendedAgenda=payload["recommendedAgenda"],
        risk=payload["risk"],
    )
