"""Grounded explainability text for client-level opportunity recommendations."""

from __future__ import annotations

import pandas as pd


PITCH_BY_PILLAR = {
    "Transactional": "Consolidated cash management and collections mandate",
    "FX": "Risk-managed FX hedging and cross-border payments programme",
    "Trade Finance": "Letters of credit and structured trade working capital line",
}


def _format_zar(value: float) -> str:
    if abs(value) >= 1_000_000_000_000:
        return f"R{value / 1_000_000_000_000:.2f}T"
    if abs(value) >= 1_000_000_000:
        return f"R{value / 1_000_000_000:.2f}B"
    return f"R{value / 1_000_000:.0f}M"


def pillar_gaps(row: pd.Series) -> dict[str, float]:
    return {
        "Transactional": float(row.get("gap_transactional", 0.0)),
        "FX": float(row.get("gap_fx", 0.0)),
        "Trade Finance": float(row.get("gap_trade_finance", 0.0)),
    }


def explain_client(row: pd.Series) -> str:
    gaps = pillar_gaps(row)
    top_pillar = max(gaps, key=gaps.get)
    top_gap = gaps[top_pillar]

    share_pct = float(row.get("syn_share", 0.0)) * 100.0
    wallet_base = float(row.get("wallet_base", 0.0))

    return (
        f"{row.get('client_name', row.get('client_id'))} has an estimated wallet of {_format_zar(wallet_base)} "
        f"with SynBank capturing {share_pct:.1f}%. The largest uncaptured gap is in {top_pillar} "
        f"at {_format_zar(top_gap)}, supported by 90-day growth signals "
        f"(TX {row.get('tx_growth_90d', 0.0):.1%}, FX {row.get('fx_growth_90d', 0.0):.1%}, "
        f"Trade {row.get('trade_growth_90d', 0.0):.1%})."
    )


def _build_why_signal(row: pd.Series, top_pillar: str, top_gap: float) -> str:
    share_pct = float(row.get("syn_share", 0.0)) * 100.0
    tx_count = int(row.get("transaction_count", 0))
    fx_count = int(row.get("fx_transaction_count", 0))
    trade_count = int(row.get("trade_transaction_count", 0))

    return (
        f"{top_pillar} is the largest gap at {_format_zar(top_gap)} while SynBank capture is {share_pct:.1f}% "
        f"across observed activity ({tx_count:,} transactional items, {fx_count:,} cross-border flows, "
        f"{trade_count:,} trade instruments)."
    )


def _build_pitch(row: pd.Series, top_pillar: str) -> str:
    base_pitch = PITCH_BY_PILLAR[top_pillar]
    urgency = row.get("urgency", "Medium")
    return f"{base_pitch}. Prioritize now given {urgency.lower()} urgency from recent activity acceleration."


def add_explainability_fields(df: pd.DataFrame) -> pd.DataFrame:
    enriched = df.copy()

    why_signals: list[str] = []
    pitch_signals: list[str] = []

    for _, row in enriched.iterrows():
        gaps = pillar_gaps(row)
        top_pillar = max(gaps, key=gaps.get)
        top_gap = gaps[top_pillar]
        why_signals.append(_build_why_signal(row, top_pillar, top_gap))
        pitch_signals.append(_build_pitch(row, top_pillar))

    enriched["why_signal"] = why_signals
    enriched["what_to_pitch"] = pitch_signals
    return enriched


def build_briefing_payload(row: pd.Series) -> dict:
    gaps = pillar_gaps(row)
    top_pillar = max(gaps, key=gaps.get)
    top_gap = gaps[top_pillar]

    summary = explain_client(row)
    key_signals = [
        f"Top opportunity gap: {top_pillar} at {_format_zar(top_gap)}",
        f"Wallet range: {_format_zar(row['wallet_low'])} to {_format_zar(row['wallet_high'])} with {row['confidence'] * 100:.0f}% confidence",
        f"SynBank share estimate: {row['syn_share'] * 100:.1f}%",
    ]

    agenda = [
        PITCH_BY_PILLAR[top_pillar],
        "Validate incumbent bank split by pillar and pricing terms",
        "Agree a 90-day conversion plan with measurable wallet-capture targets",
    ]

    risk = (
        "Momentum risk: recent signal acceleration suggests competitor action may already be underway."
        if row.get("urgency", "Medium") == "High"
        else None
    )

    sources = [
        f"client_id={row['client_id']}",
        f"transactional_flow={row['transactional_flow']:.2f}",
        f"fx_flow={row['fx_flow']:.2f}",
        f"trade_flow={row['trade_flow']:.2f}",
        f"gap={row['gap']:.2f}",
    ]

    return {
        "clientId": row["client_id"],
        "summary": summary,
        "keySignals": key_signals,
        "recommendedAgenda": agenda,
        "risk": risk,
        "sources": sources,
    }


def explain_portfolio(scored_df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    return add_explainability_fields(scored_df.head(top_n).copy())
