from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.schemas import ClientSummary, PortfolioSummary, WalletEstimate
from models.explainability import add_explainability_fields
from models.opportunity_engine import build_scored_dataset

router = APIRouter()


def _summary_from_row(row) -> ClientSummary:
    top_pillar = row["top_pillar"]
    if top_pillar not in {"Transactional", "FX", "Trade Finance"}:
        top_pillar = "Investment Banking"

    return ClientSummary(
        id=row["client_id"],
        name=row["client_name"],
        sector=row["sector_display"],
        synShare=float(row["syn_share"]),
        wallet=WalletEstimate(
            low=float(row["wallet_low"]),
            base=float(row["wallet_base"]),
            high=float(row["wallet_high"]),
            confidence=float(row["confidence"]),
        ),
        synVolume=float(row["syn_volume"]),
        gap=float(row["gap"]),
        revenueOpportunity=float(row["revenue_opportunity"]),
        opportunityScore=float(row["opportunity_score"]),
        urgency=row["urgency"],
        topPillar=top_pillar,
        whySignal=row["why_signal"],
        whatToPitch=row["what_to_pitch"],
    )


def _table():
    return add_explainability_fields(build_scored_dataset())


@router.get("/portfolio", response_model=PortfolioSummary)
def get_portfolio_summary():
    df = _table()
    total_wallet = float(df["wallet_base"].sum())
    total_syn = float(df["syn_volume"].sum())
    by_sector = (
        df.groupby("sector_display", as_index=False)
        .agg(wallet=("wallet_base", "sum"), synVolume=("syn_volume", "sum"))
        .rename(columns={"sector_display": "sector"})
    )

    return PortfolioSummary(
        totalWallet=total_wallet,
        synShare=(total_syn / total_wallet) if total_wallet > 0 else 0.0,
        totalGap=float(df["gap"].sum()),
        clientCount=int(df.shape[0]),
        bySector=by_sector.to_dict(orient="records"),
    )


@router.get("/clients", response_model=list[ClientSummary])
def get_clients():
    df = _table()
    return [_summary_from_row(row) for _, row in df.iterrows()]


@router.get("/client/{client_id}", response_model=ClientSummary)
def get_client(client_id: str):
    df = _table()
    match = df[df["client_id"].str.lower() == client_id.lower()]
    if match.empty:
        raise HTTPException(status_code=404, detail="Client not found")
    return _summary_from_row(match.iloc[0])
