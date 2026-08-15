"""Opportunity scoring and ranking invariants."""

from __future__ import annotations

from models.opportunity_engine import load_weights, score_opportunities


def test_weights_sum_to_one():
    weights = load_weights()
    assert abs(sum(weights.values()) - 1.0) < 1e-9


def test_weights_cover_the_four_documented_features():
    assert set(load_weights()) == {
        "gap_size",
        "ease_of_conversion",
        "relationship_depth",
        "urgency_freshness",
    }


def test_rank_column_exists(scored_df):
    assert "rank" in scored_df.columns


def test_ranks_are_sequential(scored_df):
    assert list(scored_df["rank"]) == list(range(1, len(scored_df) + 1))


def test_scores_descending(scored_df):
    scores = scored_df["opportunity_score"].tolist()
    assert scores == sorted(scores, reverse=True)


def test_scores_stay_on_a_zero_to_hundred_scale(scored_df):
    assert scored_df["opportunity_score"].between(0.0, 100.0).all()


def test_urgency_uses_only_the_three_documented_bands(scored_df):
    assert set(scored_df["urgency"]).issubset({"Low", "Medium", "High"})


def test_no_client_is_dropped_during_scoring(wallet_df, scored_df):
    assert len(scored_df) == len(wallet_df)
    assert set(scored_df["client_id"]) == set(wallet_df["client_id"])


def test_the_largest_gap_client_outranks_the_smallest(scored_df):
    biggest = scored_df.loc[scored_df["gap"].idxmax()]
    smallest = scored_df.loc[scored_df["gap"].idxmin()]
    assert biggest["rank"] < smallest["rank"]


def test_scoring_is_deterministic(wallet_df):
    first = score_opportunities(wallet_df)
    second = score_opportunities(wallet_df)
    assert first["opportunity_score"].tolist() == second["opportunity_score"].tolist()
