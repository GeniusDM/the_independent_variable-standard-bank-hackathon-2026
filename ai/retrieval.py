"""Grounded retrieval over precomputed wallet/opportunity tables."""

from __future__ import annotations

from functools import lru_cache

import pandas as pd

from models.explainability import build_briefing_payload
from models.opportunity_engine import build_scored_dataset


@lru_cache(maxsize=1)
def get_scored_table() -> pd.DataFrame:
    return build_scored_dataset()


def _format_source(row: pd.Series, column: str) -> str:
    return f"{row['client_id']}:{column}={row[column]:.2f}" if isinstance(row[column], float) else f"{row['client_id']}:{column}={row[column]}"


def retrieve_top_opportunities(limit: int = 5) -> tuple[pd.DataFrame, list[str]]:
    table = get_scored_table().head(limit).copy()
    sources: list[str] = []
    for _, row in table.iterrows():
        sources.extend(
            [
                _format_source(row, "opportunity_score"),
                _format_source(row, "gap"),
                _format_source(row, "syn_share"),
            ]
        )
    return table, sources


def retrieve_fx_gap_clients(limit: int = 5) -> tuple[pd.DataFrame, list[str]]:
    table = get_scored_table().copy().sort_values("gap_fx", ascending=False).head(limit)
    sources = [_format_source(row, "gap_fx") for _, row in table.iterrows()]
    return table, sources


def retrieve_client(identifier: str) -> tuple[pd.Series | None, list[str]]:
    table = get_scored_table()
    needle = identifier.strip().lower()

    exact = table[table["client_id"].str.lower() == needle]
    if exact.empty:
        exact = table[table["client_name"].str.lower().str.contains(needle)]
    if exact.empty:
        return None, []

    row = exact.iloc[0]
    sources = [
        _format_source(row, "wallet_base"),
        _format_source(row, "gap"),
        _format_source(row, "opportunity_score"),
        _format_source(row, "top_pillar"),
    ]
    return row, sources


def retrieve_briefing(identifier: str) -> tuple[dict | None, list[str]]:
    row, sources = retrieve_client(identifier)
    if row is None:
        return None, []

    payload = build_briefing_payload(row)
    combined = sources + [s for s in payload.get("sources", []) if s not in sources]
    return payload, combined
