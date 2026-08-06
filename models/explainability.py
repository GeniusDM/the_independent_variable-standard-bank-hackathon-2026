"""
explainability.py
Generates plain-English gap explanations for each client's wallet shortfall
without requiring a live LLM call — used as fallback and for unit testing.
"""
import pandas as pd


PILLAR_LABELS = {
    "transactional": "Transactional Banking",
    "fx": "Cross-Border FX / Global Markets",
    "trade_finance": "Trade Finance",
    "lending": "Lending & DCM",
}


def pillar_gaps(row: pd.Series) -> dict:
    """Returns ZAR gap per pillar for a single client row."""
    return {
        "transactional": row["wallet_transactional"] - row.get("syn_transactional", 0),
        "fx": row["wallet_fx"] - row.get("syn_fx", 0),
        "trade_finance": row["wallet_trade_finance"] - row.get("syn_trade_finance", 0),
        "lending": row["wallet_lending"] - row.get("syn_lending", 0),
    }


def explain_client(row: pd.Series) -> str:
    gaps = pillar_gaps(row)
    top_pillar = max(gaps, key=gaps.get)
    top_gap = gaps[top_pillar]
    share = row.get("share_pct", 0)

    lines = [
        f"Client: {row.get('client_name', row['client_id'])} | Sector: {row['sector']}",
        f"Syn Bank captures {share:.1f}% of an estimated ZAR {row['total_wallet']:,.0f} total wallet.",
        f"Largest gap: {PILLAR_LABELS[top_pillar]} — ZAR {top_gap:,.0f} uncaptured.",
        "Pillar breakdown:",
    ]
    for pillar, gap in sorted(gaps.items(), key=lambda x: -x[1]):
        lines.append(f"  • {PILLAR_LABELS[pillar]}: ZAR {gap:,.0f} gap")
    return "\n".join(lines)


def explain_portfolio(scored_df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """Adds an 'explanation' column to the top-N ranked clients."""
    df = scored_df.head(top_n).copy()
    df["explanation"] = df.apply(explain_client, axis=1)
    return df
