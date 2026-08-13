"""Opportunity scoring engine over wallet estimation outputs."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import pandas as pd
import yaml

from models.wallet_engine import build_wallet_dataset


WEIGHTS_PATH = Path(__file__).parents[1] / "config" / "scoring_weights.yaml"


def load_weights() -> dict:
    with open(WEIGHTS_PATH, "r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    return payload["weights"]


def _normalize(series: pd.Series) -> pd.Series:
    min_v = float(series.min())
    max_v = float(series.max())
    if max_v <= min_v:
        return pd.Series(0.0, index=series.index)
    return (series - min_v) / (max_v - min_v)


def score_opportunities(wallet_df: pd.DataFrame, weights: dict | None = None) -> pd.DataFrame:
    if weights is None:
        weights = load_weights()

    df = wallet_df.copy()

    df["gap_size_feature"] = _normalize(df["gap"])

    df["ease_of_conversion_raw"] = (
        0.50 * df["relationship_depth_score"]
        + 0.25 * (df["transaction_count"] / 3500.0).clip(0.0, 1.0)
        + 0.25 * (df["fx_transaction_count"] / 900.0).clip(0.0, 1.0)
    )
    df["ease_of_conversion_feature"] = _normalize(df["ease_of_conversion_raw"])

    df["relationship_depth_feature"] = _normalize(df["relationship_depth_score"])

    df["urgency_freshness_raw"] = (
        0.60 * df["recent_growth_signal"].clip(lower=0.0, upper=1.5)
        + 0.25 * df["fx_growth_90d"].clip(lower=0.0, upper=1.5)
        + 0.15 * df["trade_growth_90d"].clip(lower=0.0, upper=1.5)
    )
    df["urgency_freshness_feature"] = _normalize(df["urgency_freshness_raw"])

    df["opportunity_score"] = (
        weights["gap_size"] * df["gap_size_feature"]
        + weights["ease_of_conversion"] * df["ease_of_conversion_feature"]
        + weights["relationship_depth"] * df["relationship_depth_feature"]
        + weights["urgency_freshness"] * df["urgency_freshness_feature"]
    ) * 100.0

    df["urgency_score"] = 0.65 * df["urgency_freshness_feature"] + 0.35 * df["gap_size_feature"]
    df["urgency"] = pd.cut(
        df["urgency_score"],
        bins=[-0.01, 0.33, 0.66, 1.01],
        labels=["Low", "Medium", "High"],
    ).astype(str)

    df = df.sort_values("opportunity_score", ascending=False).reset_index(drop=True)
    df["rank"] = df.index + 1
    return df


@lru_cache(maxsize=1)
def build_scored_dataset() -> pd.DataFrame:
    return score_opportunities(build_wallet_dataset())
