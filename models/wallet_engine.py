"""
wallet_engine.py
Estimates total addressable banking wallet per client across four product pillars,
then calculates Syn Bank's current share and the ZAR gap.
"""
import pandas as pd
import yaml
from pathlib import Path

CONFIG_PATH = Path(__file__).parents[1] / "config" / "benchmarks.yaml"


def load_benchmarks() -> dict:
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)


def _ratio(benchmarks: dict, pillar: str, sector: str) -> float:
    sector_key = sector.lower().replace(" ", "_")
    return (
        benchmarks[pillar]["by_sector"].get(sector_key)
        or benchmarks[pillar]["default"]
    )


def estimate_wallet(clients_df: pd.DataFrame, benchmarks: dict) -> pd.DataFrame:
    """
    Parameters
    ----------
    clients_df : DataFrame with columns:
        client_id, sector, revenue, cogs, inventory, foreign_revenue,
        foreign_purchases, total_debt
    benchmarks : dict loaded from benchmarks.yaml

    Returns
    -------
    DataFrame with estimated wallet per pillar and totals.
    """
    df = clients_df.copy()

    df["wallet_transactional"] = df.apply(
        lambda r: r["revenue"] * _ratio(benchmarks, "transactional_banking", r["sector"]), axis=1
    )
    df["wallet_fx"] = df.apply(
        lambda r: (r["foreign_revenue"] + r["foreign_purchases"])
        * _ratio(benchmarks, "cross_border_fx", r["sector"]),
        axis=1,
    )
    df["wallet_trade_finance"] = df.apply(
        lambda r: (r["cogs"] + r["inventory"])
        * _ratio(benchmarks, "trade_finance", r["sector"]),
        axis=1,
    )
    df["wallet_lending"] = df.apply(
        lambda r: r["total_debt"] * _ratio(benchmarks, "lending_dcm", r["sector"]), axis=1
    )
    df["total_wallet"] = (
        df["wallet_transactional"]
        + df["wallet_fx"]
        + df["wallet_trade_finance"]
        + df["wallet_lending"]
    )
    return df


def calculate_share(wallet_df: pd.DataFrame, syn_bank_df: pd.DataFrame) -> pd.DataFrame:
    """
    Merges estimated wallet with Syn Bank's captured volumes to compute share and gap.

    syn_bank_df must have: client_id, syn_transactional, syn_fx, syn_trade_finance, syn_lending
    """
    df = wallet_df.merge(syn_bank_df, on="client_id", how="left")

    df["syn_total"] = (
        df["syn_transactional"].fillna(0)
        + df["syn_fx"].fillna(0)
        + df["syn_trade_finance"].fillna(0)
        + df["syn_lending"].fillna(0)
    )
    df["share_pct"] = (df["syn_total"] / df["total_wallet"]).clip(0, 1) * 100
    df["gap_zar"] = df["total_wallet"] - df["syn_total"]
    return df
