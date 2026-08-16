"""Two-sided share-of-wallet invariants.

The defining property of this model is that the addressable side and the captured
side come from independent inputs. test_share_varies_across_clients is the
regression guard for the defect that motivated the rewrite: when both sides were
derived from the same internal flows, share collapsed to the assumed capture rate
and sat within two points of 20% for every client.
"""

from __future__ import annotations

import pandas as pd

from models.wallet_engine import (
    BANDS,
    PILLARS,
    PILLAR_LABELS,
    _normalize_sector,
    _sector_band,
    compute_share_of_wallet,
    sensitivity_analysis,
)


# --- configuration -------------------------------------------------------

def test_benchmarks_expose_all_three_pillars(benchmarks):
    assert set(benchmarks["pillars"]) == set(PILLARS)


def test_every_pillar_has_ordered_low_base_high_bands(benchmarks):
    for pillar in PILLARS:
        for sector in ("mining", "consumer", "infrastructure", "unknown_sector"):
            low, base, high = (_sector_band(benchmarks, pillar, sector, b) for b in BANDS)
            assert 0 < low <= base <= high, f"{pillar}/{sector} bands out of order"


def test_every_pillar_declares_a_fee_margin(benchmarks):
    for pillar in PILLARS:
        assert 0 < float(benchmarks["pillars"][pillar]["fee_margin"]) < 0.05


def test_sector_aliases_normalize_to_canonical_keys():
    assert _normalize_sector("retail") == "consumer"
    assert _normalize_sector("Consumer Goods") == "consumer"
    assert _normalize_sector("pharma") == "industrials_pharma"
    assert _normalize_sector(None) == "consumer"


# --- top-down side -------------------------------------------------------

def test_addressable_bands_are_ordered(addressable_df):
    assert (addressable_df["addressable_low"] <= addressable_df["addressable_base"]).all()
    assert (addressable_df["addressable_base"] <= addressable_df["addressable_high"]).all()


def test_addressable_total_is_the_sum_of_its_pillars(addressable_df):
    parts = sum(addressable_df[f"addressable_{p}_base"] for p in PILLARS)
    assert ((addressable_df["addressable_base"] - parts).abs() < 1e-6).all()


def test_addressable_scales_with_the_external_signal(addressable_df):
    """C001 has 2x C002's revenue and a far larger foreign share, so its
    addressable flow must be larger — the top-down side is driven by published
    financials, not by anything Syn Bank observed."""
    c1 = addressable_df.set_index("client_id").loc["C001"]
    c2 = addressable_df.set_index("client_id").loc["C002"]
    assert c1["addressable_base"] > c2["addressable_base"]
    assert c1["addressable_fx_base"] > c2["addressable_fx_base"]


def test_client_with_no_foreign_revenue_has_no_fx_wallet(addressable_df):
    row = addressable_df.set_index("client_id").loc["C003"]
    assert row["addressable_fx_base"] == 0.0


# --- combined ------------------------------------------------------------

def test_share_is_captured_over_addressable(wallet_df):
    for _, row in wallet_df.iterrows():
        expected = row["captured_total"] / row["addressable_base"]
        assert abs(row["syn_share"] - expected) < 1e-9


def test_share_varies_across_clients(wallet_df):
    """Regression guard for the flat-share defect. See module docstring."""
    spread = wallet_df["syn_share"].max() - wallet_df["syn_share"].min()
    assert spread > 0.05, f"share only spans {spread:.4f} across the portfolio"


def test_gap_equals_addressable_minus_captured(wallet_df):
    for pillar in PILLARS:
        expected = (
            wallet_df[f"addressable_{pillar}_base"] - wallet_df[f"captured_{pillar}"]
        ).clip(lower=0.0)
        assert ((wallet_df[f"gap_{pillar}"] - expected).abs() < 1e-6).all()


def test_gap_is_never_negative(wallet_df):
    assert (wallet_df["gap"] >= 0).all()


def test_revenue_opportunity_applies_the_pillar_fee_margin(wallet_df, benchmarks):
    for pillar in PILLARS:
        margin = float(benchmarks["pillars"][pillar]["fee_margin"])
        expected = wallet_df[f"gap_{pillar}"] * margin
        assert ((wallet_df[f"revenue_opportunity_{pillar}"] - expected).abs() < 1e-6).all()


def test_zero_addressable_fx_does_not_divide_by_zero(wallet_df):
    row = wallet_df.set_index("client_id").loc["C003"]
    assert row["share_fx"] == 0.0
    assert pd.notna(row["syn_share"])


def test_top_pillar_is_a_known_label(wallet_df):
    assert set(wallet_df["top_pillar"]).issubset(set(PILLAR_LABELS.values()))


def test_confidence_penalises_imputed_and_estimated_inputs(wallet_df):
    by_id = wallet_df.set_index("client_id")
    # C001 has reported COGS and inventory; C003 is imputed and estimated.
    assert by_id.loc["C001"]["confidence"] > by_id.loc["C003"]["confidence"]
    assert wallet_df["confidence"].between(0.35, 0.95).all()


def test_share_above_one_is_flagged_not_hidden(addressable_df, captured_df, benchmarks):
    inflated = captured_df.copy()
    inflated["captured_transactional"] *= 5000.0
    inflated["captured_total"] = (
        inflated["captured_transactional"]
        + inflated["captured_fx"]
        + inflated["captured_trade_finance"]
    )
    result = compute_share_of_wallet(addressable_df, inflated, benchmarks)
    assert result["share_exceeds_estimate"].any()


# --- sensitivity ---------------------------------------------------------

def test_captured_side_is_invariant_to_assumption_shifts(external_df, captured_df, benchmarks):
    """Shifting the multipliers must move only the estimated side. If captured
    flow moved too, the two sides would not be independent."""
    result = sensitivity_analysis(external_df, captured_df, benchmarks=benchmarks)
    assert result["portfolio_captured"].nunique() == 1


def test_higher_multipliers_lower_the_share(external_df, captured_df, benchmarks):
    result = sensitivity_analysis(
        external_df, captured_df, shifts=(-0.25, 0.0, 0.25), benchmarks=benchmarks
    ).sort_values("multiplier_shift")
    shares = result["portfolio_share"].tolist()
    assert shares == sorted(shares, reverse=True)


def test_sensitivity_reports_every_requested_shift(external_df, captured_df, benchmarks):
    shifts = (-0.25, -0.10, 0.0, 0.10, 0.25)
    result = sensitivity_analysis(external_df, captured_df, shifts=shifts, benchmarks=benchmarks)
    assert len(result) == len(shifts)
