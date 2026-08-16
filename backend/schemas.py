from typing import Literal, Optional

from pydantic import BaseModel


class WalletEstimate(BaseModel):
    low: float
    base: float
    high: float
    confidence: float


class ClientSummary(BaseModel):
    id: str
    name: str
    sector: str
    synShare: float
    wallet: WalletEstimate
    synVolume: float
    gap: float
    # Annual ZAR fee revenue the uncaptured gap represents. This is the number a
    # coverage banker is actually chasing; `gap` is the flow behind it.
    revenueOpportunity: float
    opportunityScore: float
    urgency: Literal["Low", "Medium", "High"]
    topPillar: Literal["Transactional", "FX", "Trade Finance", "Investment Banking"]
    whySignal: str
    whatToPitch: str


class SectorSummary(BaseModel):
    sector: str
    wallet: float
    synVolume: float


class PortfolioSummary(BaseModel):
    totalWallet: float
    synShare: float
    totalGap: float
    clientCount: int
    bySector: list[SectorSummary]


class Briefing(BaseModel):
    clientId: str
    summary: str
    keySignals: list[str]
    recommendedAgenda: list[str]
    risk: Optional[str]


class CopilotRequest(BaseModel):
    question: str


class CopilotMessage(BaseModel):
    role: Literal["assistant"]
    content: str
    sources: list[str]
