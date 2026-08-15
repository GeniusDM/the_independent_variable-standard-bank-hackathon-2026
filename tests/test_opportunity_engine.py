import pytest
import pandas as pd
from models.wallet_engine import load_benchmarks, estimate_wallet, calculate_share
from models.opportunity_engine import score_opportunities

SAMPLE_CLIENTS = pd.DataFrame([
    {"client_id": "C001", "sector": "mining", "revenue": 10_000_000, "cogs": 6_000_000,
     "inventory": 1_000_000, "foreign_revenue": 4_000_000, "foreign_purchases": 2_000_000, "total_debt": 5_000_000},
    {"client_id": "C002", "sector": "retail", "revenue": 20_000_000, "cogs": 14_000_000,
     "inventory": 3_000_000, "foreign_revenue": 1_000_000, "foreign_purchases": 5_000_000, "total_debt": 8_000_000},
    {"client_id": "C003", "sector": "infrastructure", "revenue": 5_000_000, "cogs": 3_000_000,
     "inventory": 500_000, "foreign_revenue": 500_000, "foreign_purchases": 200_000, "total_debt": 10_000_000},
])

SAMPLE_SYN = pd.DataFrame([
    {"client_id": "C001", "syn_transactional": 5_000, "syn_fx": 5_000, "syn_trade_finance": 5_000, "syn_lending": 5_000},
    {"client_id": "C002", "syn_transactional": 60_000, "syn_fx": 10_000, "syn_trade_finance": 80_000, "syn_lending": 100_000},
    {"client_id": "C003", "syn_transactional": 1_000, "syn_fx": 1_000, "syn_trade_finance": 1_000, "syn_lending": 1_000},
])


@pytest.fixture
def scored():
    benchmarks = load_benchmarks()
    wallet_df = estimate_wallet(SAMPLE_CLIENTS, benchmarks)
    share_df = calculate_share(wallet_df, SAMPLE_SYN)
    return score_opportunities(share_df)


def test_rank_column_exists(scored):
    assert "rank" in scored.columns


def test_ranks_are_sequential(scored):
    assert list(scored["rank"]) == list(range(1, len(scored) + 1))


def test_scores_descending(scored):
    scores = scored["opportunity_score"].tolist()
    assert scores == sorted(scores, reverse=True)
