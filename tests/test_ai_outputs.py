import pytest
import pandas as pd
from models.explainability import explain_client, pillar_gaps

SAMPLE_ROW = pd.Series({
    "client_id": "C001", "client_name": "Acme Mining Ltd", "sector": "mining",
    "total_wallet": 500_000, "syn_total": 100_000, "share_pct": 20.0, "gap_zar": 400_000,
    "wallet_transactional": 50_000, "wallet_fx": 150_000,
    "wallet_trade_finance": 200_000, "wallet_lending": 100_000,
    "syn_transactional": 10_000, "syn_fx": 20_000,
    "syn_trade_finance": 50_000, "syn_lending": 20_000,
})


def test_pillar_gaps_all_positive():
    gaps = pillar_gaps(SAMPLE_ROW)
    assert all(v >= 0 for v in gaps.values())


def test_explain_client_contains_client_name():
    text = explain_client(SAMPLE_ROW)
    assert "Acme Mining Ltd" in text


def test_explain_client_contains_share():
    text = explain_client(SAMPLE_ROW)
    assert "20.0%" in text


def test_explain_client_contains_top_pillar():
    text = explain_client(SAMPLE_ROW)
    assert "Trade Finance" in text  # largest gap pillar for this sample
