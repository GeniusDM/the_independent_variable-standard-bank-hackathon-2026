"""Wallet engine invariants.

NOTE (Phase 1): these tests currently assert the behaviour of the flow-based
model. The share-of-wallet figure it produces is driven by the capture-ratio
heuristics rather than by any external estimate of total wallet, which is why
`test_share_is_currently_flat_across_clients` below is marked xfail — it
documents the known weakness the top-down rebuild is meant to remove.
"""

from __future__ import annotations

import pytest

from models.wallet_engine import (
    PILLAR_LABELS,
    _normalize_sector,
    _pillar_ratio,
    load_benchmarks,
)


def test_benchmarks_load_with_all_three_pillars():
    benchmarks = load_benchmarks()
    assert set(benchmarks["pillars"]) == {"transactional", "fx", "trade_finance"}


def test_every_pillar_has_ordered_low_base_high_bands():
    benchmarks = load_benchmarks()
    for pillar in benchmarks["pillars"]:
        for sector in ("mining", "consumer", "infrastructure", "unknown_sector"):
            low = _pillar_ratio(benchmarks, pillar, sector, "low")
            base = _pillar_ratio(benchmarks, pillar, sector, "base")
            high = _pillar_ratio(benchmarks, pillar, sector, "high")
            assert 0 < low <= base <= high, f"{pillar}/{sector} bands out of order"


def test_sector_aliases_normalize_to_canonical_keys():
    assert _normalize_sector("retail") == "consumer"
    assert _normalize_sector("Consumer Goods") == "consumer"
    assert _normalize_sector("pharma") == "industrials_pharma"
    assert _normalize_sector(None) == "consumer"


def test_wallet_bands_are_ordered_per_client(wallet_df):
    assert (wallet_df["wallet_low"] <= wallet_df["wallet_base"]).all()
    assert (wallet_df["wallet_base"] <= wallet_df["wallet_high"]).all()


def test_total_wallet_is_positive(wallet_df):
    assert (wallet_df["wallet_base"] > 0).all()


def test_wallet_base_is_the_sum_of_its_pillars(wallet_df):
    parts = (
        wallet_df["wallet_transactional_base"]
        + wallet_df["wallet_fx_base"]
        + wallet_df["wallet_trade_finance_base"]
    )
    assert ((wallet_df["wallet_base"] - parts).abs() < 1e-6).all()


def test_share_is_between_zero_and_one(wallet_df):
    assert wallet_df["syn_share"].between(0.0, 1.0).all()


def test_gap_equals_wallet_minus_captured(wallet_df):
    diff = (wallet_df["gap"] - (wallet_df["wallet_base"] - wallet_df["syn_volume"])).abs()
    assert (diff < 1e-6).all()


def test_pillar_gaps_sum_to_total_gap(wallet_df):
    parts = (
        wallet_df["gap_transactional"] + wallet_df["gap_fx"] + wallet_df["gap_trade_finance"]
    )
    assert ((wallet_df["gap"] - parts).abs() < 1e-6).all()


def test_top_pillar_is_a_known_label(wallet_df):
    assert set(wallet_df["top_pillar"]).issubset(set(PILLAR_LABELS.values()))


def test_confidence_stays_within_declared_bounds(wallet_df):
    assert wallet_df["confidence"].between(0.55, 0.90).all()


def test_a_client_with_no_fx_flow_has_no_fx_wallet(wallet_df):
    row = wallet_df[wallet_df["client_id"] == "C003"].iloc[0]
    assert row["wallet_fx_base"] == 0.0
    assert row["gap_fx"] == 0.0


@pytest.mark.xfail(
    reason="Known Phase 1 defect: share is set by the capture heuristic, not by an "
    "independent wallet estimate, so it barely varies across very different clients.",
    strict=True,
)
def test_share_is_currently_flat_across_clients(wallet_df):
    spread = wallet_df["syn_share"].max() - wallet_df["syn_share"].min()
    assert spread > 0.10, f"share only spans {spread:.3f} across the portfolio"
