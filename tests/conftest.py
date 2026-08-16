"""Shared fixtures.

The tests run against small in-memory frames rather than the ~429MB CSVs in
data/raw/, so `pytest tests/` stays fast and works on a fresh clone before the
hackathon data has been placed.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

# Allow `import models...` when pytest is invoked from anywhere.
ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT))

RAW_DIR = ROOT / "data" / "raw"
RAW_FILES = (
    "transactional_banking.csv",
    "cross_border_payments.csv",
    "trade_finance.csv",
)

#: The supplied datasets are ~429MB and are deliberately not in the repo, so a
#: fresh clone has no data/raw/. Tests that exercise the full pipeline are
#: skipped there rather than failing, keeping `pytest tests/` green for anyone
#: who clones the repo before placing the CSVs.
requires_raw_data = pytest.mark.skipif(
    not all((RAW_DIR / name).exists() for name in RAW_FILES),
    reason="hackathon CSVs not present in data/raw/ (see README setup step 3)",
)


def make_external_frame() -> pd.DataFrame:
    """Published-financial inputs, in the shape load_external_financials returns.

    C001 has reported COGS and inventory; C002 has neither, so it exercises the
    imputation path; C003 is a small domestic client with no foreign revenue.
    """
    rows = [
        {
            "client_id": "C001",
            "client_name": "Acme Mining Ltd",
            "sector": "mining",
            "revenue_zar_m": 120_000.0,
            "cogs_zar_m": 78_000.0,
            "inventory_zar_m": 11_000.0,
            "total_debt_zar_m": 30_000.0,
            "foreign_revenue_share": 0.80,
            "sa_attribution_share": 0.90,
            "source_quality": "reported",
            "cogs_imputed": False,
            "inventory_imputed": False,
        },
        {
            "client_id": "C002",
            "client_name": "Beta Retail Group",
            "sector": "consumer",
            "revenue_zar_m": 60_000.0,
            "cogs_zar_m": 45_000.0,
            "inventory_zar_m": 9_000.0,
            "total_debt_zar_m": 4_000.0,
            "foreign_revenue_share": 0.10,
            "sa_attribution_share": 1.00,
            "source_quality": "derived",
            "cogs_imputed": True,
            "inventory_imputed": True,
        },
        {
            "client_id": "C003",
            "client_name": "Cape Infrastructure SOC",
            "sector": "infrastructure",
            "revenue_zar_m": 8_000.0,
            "cogs_zar_m": 6_400.0,
            "inventory_zar_m": 640.0,
            "total_debt_zar_m": 12_000.0,
            "foreign_revenue_share": 0.00,
            "sa_attribution_share": 1.00,
            "source_quality": "estimated",
            "cogs_imputed": True,
            "inventory_imputed": True,
        },
    ]

    df = pd.DataFrame(rows)
    for col in ("revenue_zar_m", "cogs_zar_m", "inventory_zar_m", "total_debt_zar_m"):
        df[col.replace("_zar_m", "_zar")] = df[col] * 1_000_000.0

    df["addressable_revenue_zar"] = df["revenue_zar"] * df["sa_attribution_share"]
    df["addressable_foreign_revenue_zar"] = (
        df["revenue_zar"] * df["foreign_revenue_share"] * df["sa_attribution_share"]
    )
    df["addressable_cogs_inventory_zar"] = (
        df["cogs_zar"] + df["inventory_zar"]
    ) * df["sa_attribution_share"]
    return df


def make_captured_frame() -> pd.DataFrame:
    """Bottom-up measured flow, in the shape measure_captured_flow returns.

    C003 has no cross-border activity at all, so share and gap must both handle
    a zero addressable FX base without dividing by zero.
    """
    rows = [
        {
            "client_id": "C001",
            "captured_transactional": 40_000_000_000.0,
            "captured_fx": 30_000_000_000.0,
            "captured_trade_finance": 5_000_000_000.0,
            "transaction_count": 4000,
            "fx_transaction_count": 800,
            "trade_transaction_count": 300,
            "channel_count": 3,
            "corridor_count": 6,
            "instrument_count": 3,
            "inbound_ratio": 0.55,
            "avg_tenor_days": 90.0,
            "tx_growth_90d": 0.12,
            "fx_growth_90d": 0.30,
            "trade_growth_90d": 0.05,
        },
        {
            "client_id": "C002",
            "captured_transactional": 9_000_000_000.0,
            "captured_fx": 400_000_000.0,
            "captured_trade_finance": 1_200_000_000.0,
            "transaction_count": 9000,
            "fx_transaction_count": 200,
            "trade_transaction_count": 900,
            "channel_count": 4,
            "corridor_count": 2,
            "instrument_count": 2,
            "inbound_ratio": 0.70,
            "avg_tenor_days": 200.0,
            "tx_growth_90d": -0.04,
            "fx_growth_90d": 0.02,
            "trade_growth_90d": 0.18,
        },
        {
            "client_id": "C003",
            "captured_transactional": 900_000_000.0,
            "captured_fx": 0.0,
            "captured_trade_finance": 50_000_000.0,
            "transaction_count": 700,
            "fx_transaction_count": 0,
            "trade_transaction_count": 60,
            "channel_count": 2,
            "corridor_count": 0,
            "instrument_count": 1,
            "inbound_ratio": 0.35,
            "avg_tenor_days": 365.0,
            "tx_growth_90d": 0.01,
            "fx_growth_90d": 0.0,
            "trade_growth_90d": -0.10,
        },
    ]

    df = pd.DataFrame(rows)
    df["captured_total"] = (
        df["captured_transactional"] + df["captured_fx"] + df["captured_trade_finance"]
    )
    df["active_pillars"] = (
        (df["captured_transactional"] > 0).astype(int)
        + (df["captured_fx"] > 0).astype(int)
        + (df["captured_trade_finance"] > 0).astype(int)
    )
    df["relationship_depth_score"] = df["active_pillars"] / 3.0
    df["recent_growth_signal"] = (
        df[["tx_growth_90d", "fx_growth_90d", "trade_growth_90d"]].mean(axis=1).clip(-1.0, 2.0)
    )
    return df


@pytest.fixture
def benchmarks() -> dict:
    from models.wallet_engine import load_benchmarks

    return load_benchmarks()


@pytest.fixture
def external_df() -> pd.DataFrame:
    return make_external_frame()


@pytest.fixture
def captured_df() -> pd.DataFrame:
    return make_captured_frame()


@pytest.fixture
def addressable_df(external_df, benchmarks) -> pd.DataFrame:
    from models.wallet_engine import estimate_addressable_flow

    return estimate_addressable_flow(external_df, benchmarks)


@pytest.fixture
def wallet_df(addressable_df, captured_df, benchmarks) -> pd.DataFrame:
    from models.wallet_engine import compute_share_of_wallet

    return compute_share_of_wallet(addressable_df, captured_df, benchmarks)


@pytest.fixture
def scored_df(wallet_df) -> pd.DataFrame:
    from models.opportunity_engine import score_opportunities

    return score_opportunities(wallet_df)
