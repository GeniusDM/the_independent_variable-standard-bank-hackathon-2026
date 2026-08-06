"""
opportunity_engine.py
Scores and ranks clients by revenue growth opportunity using configurable weights.
"""
import pandas as pd
import yaml
from pathlib import Path
from sklearn.preprocessing import MinMaxScaler

WEIGHTS_PATH = Path(__file__).parents[1] / "config" / "scoring_weights.yaml"

PRIORITY_SECTORS = {"mining", "infrastructure"}


def load_weights() -> dict:
    with open(WEIGHTS_PATH) as f:
        return yaml.safe_load(f)


def score_opportunities(share_df: pd.DataFrame, weights: dict | None = None) -> pd.DataFrame:
    """
    Parameters
    ----------
    share_df : output of wallet_engine.calculate_share(), plus:
        revenue_cagr (3-year), sector
    weights : override scoring_weights.yaml if provided

    Returns
    -------
    DataFrame sorted by opportunity_score descending, with rank column.
    """
    if weights is None:
        weights = load_weights()

    df = share_df.copy()
    scaler = MinMaxScaler()

    features = {
        "wallet_gap_zar": df["gap_zar"],
        "wallet_gap_pct": 100 - df["share_pct"],
        "relationship_depth": df.get("active_pillars", pd.Series(1, index=df.index)),
        "revenue_growth_trend": df.get("revenue_cagr", pd.Series(0, index=df.index)),
    }

    scaled = pd.DataFrame(
        scaler.fit_transform(pd.DataFrame(features)),
        columns=features.keys(),
        index=df.index,
    )

    df["strategic_sector_bonus"] = df["sector"].str.lower().str.replace(" ", "_").isin(
        PRIORITY_SECTORS
    ).astype(float)

    df["opportunity_score"] = (
        scaled["wallet_gap_zar"] * weights["wallet_gap_zar"]
        + scaled["wallet_gap_pct"] * weights["wallet_gap_pct"]
        + scaled["relationship_depth"] * weights["relationship_depth"]
        + scaled["revenue_growth_trend"] * weights["revenue_growth_trend"]
        + df["strategic_sector_bonus"] * weights["strategic_sector_bonus"]
    )

    df = df.sort_values("opportunity_score", ascending=False).reset_index(drop=True)
    df["rank"] = df.index + 1
    return df
