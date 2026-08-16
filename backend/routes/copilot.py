from __future__ import annotations

from fastapi import APIRouter

from ai import llm
from ai.copilot import answer_question
from backend.schemas import CopilotMessage, CopilotRequest

router = APIRouter()


@router.post("/ask-ai", response_model=CopilotMessage)
def query_copilot(req: CopilotRequest):
    payload = answer_question(req.question)
    return CopilotMessage(
        role="assistant",
        content=payload["content"],
        sources=payload.get("sources", []),
        generatedBy=payload.get("generatedBy", "deterministic"),
        latencyMs=payload.get("latencyMs"),
        cached=bool(payload.get("cached", False)),
        groundingWarnings=payload.get("groundingWarnings", []),
    )


@router.get("/ai-status")
def ai_status():
    """Which model is answering, if any. Surfaced so the AI path is auditable
    rather than something the audience has to take on trust."""
    return llm.provider_status()
