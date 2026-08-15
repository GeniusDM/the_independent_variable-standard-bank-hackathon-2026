"""Shared fixtures.

The tests below run against small in-memory frames rather than the 400MB CSVs in
data/raw/, so `pytest tests/` stays fast and works on a fresh clone before the
hackathon data has been placed.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

# Allow `import models...` when pytest is invoked from anywhere.
sys.path.insert(0, str(Path(__file__).parents[1]))


def make_activity_frame() -> pd.DataFrame:
    """A minimal client-activity frame with every column estimate_wallet_ranges reads."""
    rows = [
        {
            "client_id": "C001",
            "client_name": "Acme Mining Ltd",
            "sector": "mining",
            "transactional_flow": 900_000_000.0,
            "fx_flow": 400_000_000.0,
            "trade_flow": 150_000_000.0,
            "transaction_count": 4000,
            "fx_transaction_count": 800,
            "trade_transaction_count": 300,
            "channel_count": 3,
            "corridor_count": 6,
            "instrument_count": 3,
            "inbound_ratio": 0.55,
            "fx_inbound_ratio": 0.40,
            "avg_tenor_days": 90.0,
            "tx_growth_90d": 0.12,
            "fx_growth_90d": 0.30,
            "trade_growth_90d": 0.05,
        },
        {
            "client_id": "C002",
            "client_name": "Beta Retail Group",
            "sector": "consumer",
            "transactional_flow": 2_100_000_000.0,
            "fx_flow": 90_000_000.0,
            "trade_flow": 600_000_000.0,
            "transaction_count": 9000,
            "fx_transaction_count": 200,
            "trade_transaction_count": 900,
            "channel_count": 4,
            "corridor_count": 2,
            "instrument_count": 2,
            "inbound_ratio": 0.70,
            "fx_inbound_ratio": 0.20,
            "avg_tenor_days": 200.0,
            "tx_growth_90d": -0.04,
            "fx_growth_90d": 0.02,
            "trade_growth_90d": 0.18,
        },
        {
            "client_id": "C003",
            "client_name": "Cape Infrastructure SOC",
            "sector": "infrastructure",
            "transactional_flow": 300_000_000.0,
            "fx_flow": 0.0,
            "trade_flow": 25_000_000.0,
            "transaction_count": 700,
            "fx_transaction_count": 0,
            "trade_transaction_count": 60,
            "channel_count": 2,
            "corridor_count": 0,
            "instrument_count": 1,
            "inbound_ratio": 0.35,
            "fx_inbound_ratio": 0.0,
            "avg_tenor_days": 365.0,
            "tx_growth_90d": 0.01,
            "fx_growth_90d": 0.0,
            "trade_growth_90d": -0.10,
        },
    ]

    df = pd.DataFrame(rows)
    df["active_pillars"] = (
        (df["transactional_flow"] > 0).astype(int)
        + (df["fx_flow"] > 0).astype(int)
        + (df["trade_flow"] > 0).astype(int)
    )
    df["relationship_depth_score"] = (df["active_pillars"] / 3.0).clip(0.0, 1.0)
    df["recent_growth_signal"] = (
        df[["tx_growth_90d", "fx_growth_90d", "trade_growth_90d"]].mean(axis=1).clip(-1.0, 2.0)
    )
    return df


@pytest.fixture
def activity_df() -> pd.DataFrame:
    return make_activity_frame()


@pytest.fixture
def wallet_df(activity_df: pd.DataFrame) -> pd.DataFrame:
    from models.wallet_engine import estimate_wallet_ranges

    return estimate_wallet_ranges(activity_df)


@pytest.fixture
def scored_df(wallet_df: pd.DataFrame) -> pd.DataFrame:
    from models.opportunity_engine import score_opportunities

    return score_opportunities(wallet_df)
