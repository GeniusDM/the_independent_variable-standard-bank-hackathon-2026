import pytest
import pandas as pd
from models.wallet_engine import load_benchmarks, estimate_wallet, calculate_share

SAMPLE_CLIENTS = pd.DataFrame([
    {
        "client_id": "C001", "sector": "mining",
        "revenue": 10_000_000, "cogs": 6_000_000, "inventory": 1_000_000,
        "foreign_revenue": 4_000_000, "foreign_purchases": 2_000_000, "total_debt": 5_000_000,
    },
    {
        "client_id": "C002", "sector": "retail",
        "revenue": 20_000_000, "cogs": 14_000_000, "inventory": 3_000_000,
        "foreign_revenue": 1_000_000, "foreign_purchases": 5_000_000, "total_debt": 8_000_000,
    },
])

SAMPLE_SYN = pd.DataFrame([
    {"client_id": "C001", "syn_transactional": 20_000, "syn_fx": 30_000, "syn_trade_finance": 50_000, "syn_lending": 40_000},
    {"client_id": "C002", "syn_transactional": 60_000, "syn_fx": 10_000, "syn_trade_finance": 80_000, "syn_lending": 100_000},
])


@pytest.fixture
def benchmarks():
    return load_benchmarks()


def test_estimate_wallet_columns(benchmarks):
    result = estimate_wallet(SAMPLE_CLIENTS, benchmarks)
    for col in ["wallet_transactional", "wallet_fx", "wallet_trade_finance", "wallet_lending", "total_wallet"]:
        assert col in result.columns


def test_total_wallet_positive(benchmarks):
    result = estimate_wallet(SAMPLE_CLIENTS, benchmarks)
    assert (result["total_wallet"] > 0).all()


def test_share_pct_between_0_and_100(benchmarks):
    wallet_df = estimate_wallet(SAMPLE_CLIENTS, benchmarks)
    result = calculate_share(wallet_df, SAMPLE_SYN)
    assert result["share_pct"].between(0, 100).all()


def test_gap_equals_total_minus_syn(benchmarks):
    wallet_df = estimate_wallet(SAMPLE_CLIENTS, benchmarks)
    result = calculate_share(wallet_df, SAMPLE_SYN)
    diff = (result["gap_zar"] - (result["total_wallet"] - result["syn_total"])).abs()
    assert (diff < 1).all()
