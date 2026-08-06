from pydantic import BaseModel
from typing import Optional


class ClientWallet(BaseModel):
    client_id: str
    client_name: Optional[str] = None
    sector: str
    total_wallet: float
    syn_total: float
    share_pct: float
    gap_zar: float
    wallet_transactional: float
    wallet_fx: float
    wallet_trade_finance: float
    wallet_lending: float


class OpportunityRank(ClientWallet):
    opportunity_score: float
    rank: int
    explanation: Optional[str] = None


class BriefingRequest(BaseModel):
    client_id: str


class BriefingResponse(BaseModel):
    client_id: str
    briefing: str


class CopilotRequest(BaseModel):
    question: str


class CopilotResponse(BaseModel):
    narrative: str
    results: list[dict]
