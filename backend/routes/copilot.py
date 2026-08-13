from __future__ import annotations

from fastapi import APIRouter

from ai.copilot import answer_question
from backend.schemas import CopilotMessage, CopilotRequest

router = APIRouter()


@router.post("/ask-ai", response_model=CopilotMessage)
def query_copilot(req: CopilotRequest):
    payload = answer_question(req.question)
    return CopilotMessage(role="assistant", content=payload["content"], sources=payload.get("sources", []))
