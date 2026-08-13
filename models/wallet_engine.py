"""Wallet estimation pipeline over hackathon raw transactional datasets."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import pandas as pd
import yaml


ROOT = Path(__file__).parents[1]
CONFIG_PATH = ROOT / "config" / "benchmarks.yaml"
RAW_DIR = ROOT / "data" / "raw"

PILLAR_LABELS = {
    "transactional": "Transactional",
    "fx": "FX",
    "trade_finance": "Trade Finance",
}

SECTOR_LABELS = {
    "mining": "Mining",
    "consumer": "Consumer Goods",
    "manufacturing": "Manufacturing",
    "financial_services": "Financial Services",
    "infrastructure": "Infrastructure",
    "industrials_pharma": "Industrials & Pharma",
    "insurance": "Insurance",
    "real_estate": "Real Estate",
    "tech": "Technology",
    "telecoms": "Telecoms",
}


def load_benchmarks() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _normalize_sector(sector: str | None) -> str:
    if not sector:
        return "consumer"
    value = sector.strip().lower().replace(" ", "_")
    # map legacy / alternate names to canonical keys
    aliases = {
        "retail": "consumer",
        "consumer_goods": "consumer",
        "financial_services": "financial_services",
        "industrials": "industrials_pharma",
        "pharma": "industrials_pharma",
    }
    return aliases.get(value, value)


def _display_sector(sector: str) -> str:
    return SECTOR_LABELS.get(_normalize_sector(sector), sector.replace("_", " ").title())


def _pillar_ratio(benchmarks: dict, pillar: str, sector: str, band: str) -> float:
    normalized = _normalize_sector(sector)
    pillar_cfg = benchmarks["pillars"][pillar]
    scoped = pillar_cfg.get("by_sector", {}).get(normalized)
    if scoped and band in scoped:
        return float(scoped[band])
    return float(pillar_cfg["default"][band])


def _capture_ratio_transactional(row: pd.Series) -> float:
    ratio = (
        0.10
        + 0.05 * min(row.get("transaction_count", 0) / 4500.0, 1.0)
        + 0.04 * min(row.get("channel_count", 0) / 4.0, 1.0)
        + 0.03 * row.get("inbound_ratio", 0.0)
    )
    return float(min(max(ratio, 0.08), 0.32))


def _capture_ratio_fx(row: pd.Series) -> float:
    ratio = (
        0.09
        + 0.05 * min(row.get("fx_transaction_count", 0) / 1000.0, 1.0)
        + 0.04 * min(row.get("corridor_count", 0) / 8.0, 1.0)
        + 0.02 * row.get("fx_inbound_ratio", 0.0)
    )
    return float(min(max(ratio, 0.07), 0.30))


def _capture_ratio_trade(row: pd.Series) -> float:
    short_tenor_boost = 1.0 if row.get("avg_tenor_days", 999.0) <= 120.0 else 0.0
    ratio = (
        0.10
        + 0.05 * min(row.get("trade_transaction_count", 0) / 400.0, 1.0)
        + 0.03 * min(row.get("instrument_count", 0) / 3.0, 1.0)
        + 0.02 * short_tenor_boost
    )
    return float(min(max(ratio, 0.08), 0.28))


def _volume_growth(recent: float, prior: float) -> float:
    if prior <= 0:
        return 0.0
    return float((recent - prior) / prior)


def _recent_and_prior_volumes(df: pd.DataFrame, date_col: str, value_col: str) -> pd.DataFrame:
    latest = df[date_col].max()
    recent_start = latest - pd.Timedelta(days=90)
    prior_start = latest - pd.Timedelta(days=180)

    recent = (
        df[df[date_col] >= recent_start]
        .groupby("entity_id", as_index=False)[value_col]
        .sum()
        .rename(columns={value_col: f"recent_{value_col}"})
    )
    prior = (
        df[(df[date_col] >= prior_start) & (df[date_col] < recent_start)]
        .groupby("entity_id", as_index=False)[value_col]
        .sum()
        .rename(columns={value_col: f"prior_{value_col}"})
    )

    return recent.merge(prior, on="entity_id", how="outer").fillna(0.0)


def load_raw_tables() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    transactional = pd.read_csv(
        RAW_DIR / "transactional_banking.csv",
        usecols=["entity_id", "entity_name", "sector", "date", "direction", "amount_zar", "channel"],
        parse_dates=["date"],
    )
    cross_border = pd.read_csv(
        RAW_DIR / "cross_border_payments.csv",
        usecols=["entity_id", "entity_name", "sector", "date", "direction", "value_zar", "counterparty_country"],
        parse_dates=["date"],
    )
    trade = pd.read_csv(
        RAW_DIR / "trade_finance.csv",
        usecols=["entity_id", "entity_name", "sector", "date", "tenor_days", "value_zar", "instrument_type"],
        parse_dates=["date"],
    )
    return transactional, cross_border, trade


def build_client_activity(transactional: pd.DataFrame, cross_border: pd.DataFrame, trade: pd.DataFrame) -> pd.DataFrame:
    tx_recent_prior = _recent_and_prior_volumes(transactional, "date", "amount_zar")
    fx_recent_prior = _recent_and_prior_volumes(cross_border, "date", "value_zar")
    tf_recent_prior = _recent_and_prior_volumes(trade, "date", "value_zar")

    tx = (
        transactional.groupby("entity_id", as_index=False)
        .agg(
            client_name=("entity_name", "first"),
            sector=("sector", "first"),
            transactional_flow=("amount_zar", "sum"),
            transaction_count=("amount_zar", "size"),
            channel_count=("channel", "nunique"),
            inbound_ratio=("direction", lambda s: float((s == "inbound").mean())),
        )
        .merge(tx_recent_prior, on="entity_id", how="left")
    )

    fx = (
        cross_border.groupby("entity_id", as_index=False)
        .agg(
            fx_flow=("value_zar", "sum"),
            fx_transaction_count=("value_zar", "size"),
            corridor_count=("counterparty_country", "nunique"),
            fx_inbound_ratio=("direction", lambda s: float((s == "inbound").mean())),
        )
        .merge(fx_recent_prior, on="entity_id", how="left")
    )

    tf = (
        trade.groupby("entity_id", as_index=False)
        .agg(
            trade_flow=("value_zar", "sum"),
            trade_transaction_count=("value_zar", "size"),
            avg_tenor_days=("tenor_days", "mean"),
            instrument_count=("instrument_type", "nunique"),
        )
        .merge(tf_recent_prior, on="entity_id", how="left")
    )

    df = tx.merge(fx, on="entity_id", how="outer").merge(tf, on="entity_id", how="outer")
    df = df.fillna(
        {
            "client_name": "Unknown Client",
            "sector": "consumer",
            "transactional_flow": 0.0,
            "fx_flow": 0.0,
            "trade_flow": 0.0,
            "transaction_count": 0,
            "fx_transaction_count": 0,
            "trade_transaction_count": 0,
            "channel_count": 0,
            "corridor_count": 0,
            "instrument_count": 0,
            "inbound_ratio": 0.0,
            "fx_inbound_ratio": 0.0,
            "avg_tenor_days": 0.0,
            "recent_amount_zar": 0.0,
            "prior_amount_zar": 0.0,
            "recent_value_zar_x": 0.0,
            "prior_value_zar_x": 0.0,
            "recent_value_zar_y": 0.0,
            "prior_value_zar_y": 0.0,
        }
    )

    df = df.rename(
        columns={
            "entity_id": "client_id",
            "recent_value_zar_x": "recent_fx_value",
            "prior_value_zar_x": "prior_fx_value",
            "recent_value_zar_y": "recent_trade_value",
            "prior_value_zar_y": "prior_trade_value",
            "recent_amount_zar": "recent_tx_value",
            "prior_amount_zar": "prior_tx_value",
        }
    )

    df["tx_growth_90d"] = df.apply(lambda r: _volume_growth(r["recent_tx_value"], r["prior_tx_value"]), axis=1)
    df["fx_growth_90d"] = df.apply(lambda r: _volume_growth(r["recent_fx_value"], r["prior_fx_value"]), axis=1)
    df["trade_growth_90d"] = df.apply(lambda r: _volume_growth(r["recent_trade_value"], r["prior_trade_value"]), axis=1)
    df["recent_growth_signal"] = df[["tx_growth_90d", "fx_growth_90d", "trade_growth_90d"]].mean(axis=1).clip(-1.0, 2.0)

    df["active_pillars"] = (
        (df["transactional_flow"] > 0).astype(int)
        + (df["fx_flow"] > 0).astype(int)
        + (df["trade_flow"] > 0).astype(int)
    )
    df["relationship_depth_score"] = (df["active_pillars"] / 3.0).clip(0.0, 1.0)
    df["sector"] = df["sector"].map(_normalize_sector)
    return df


def estimate_wallet_ranges(activity_df: pd.DataFrame, benchmarks: dict | None = None) -> pd.DataFrame:
    if benchmarks is None:
        benchmarks = load_benchmarks()

    df = activity_df.copy()

    for pillar, flow_col in (
        ("transactional", "transactional_flow"),
        ("fx", "fx_flow"),
        ("trade_finance", "trade_flow"),
    ):
        for band in ("low", "base", "high"):
            df[f"wallet_{pillar}_{band}"] = df.apply(
                lambda r: r[flow_col] * _pillar_ratio(benchmarks, pillar, r["sector"], band),
                axis=1,
            )

    df["wallet_transactional_low"] = df["wallet_transactional_low"].fillna(0.0)
    df["wallet_fx_low"] = df["wallet_fx_low"].fillna(0.0)
    df["wallet_trade_finance_low"] = df["wallet_trade_finance_low"].fillna(0.0)

    df["wallet_low"] = (
        df["wallet_transactional_low"] + df["wallet_fx_low"] + df["wallet_trade_finance_low"]
    )
    df["wallet_base"] = (
        df["wallet_transactional_base"] + df["wallet_fx_base"] + df["wallet_trade_finance_base"]
    )
    df["wallet_high"] = (
        df["wallet_transactional_high"] + df["wallet_fx_high"] + df["wallet_trade_finance_high"]
    )

    df["syn_capture_transactional"] = df.apply(_capture_ratio_transactional, axis=1)
    df["syn_capture_fx"] = df.apply(_capture_ratio_fx, axis=1)
    df["syn_capture_trade_finance"] = df.apply(_capture_ratio_trade, axis=1)

    df["syn_transactional"] = df["wallet_transactional_base"] * df["syn_capture_transactional"]
    df["syn_fx"] = df["wallet_fx_base"] * df["syn_capture_fx"]
    df["syn_trade_finance"] = df["wallet_trade_finance_base"] * df["syn_capture_trade_finance"]
    df["syn_volume"] = df["syn_transactional"] + df["syn_fx"] + df["syn_trade_finance"]

    df["gap_transactional"] = df["wallet_transactional_base"] - df["syn_transactional"]
    df["gap_fx"] = df["wallet_fx_base"] - df["syn_fx"]
    df["gap_trade_finance"] = df["wallet_trade_finance_base"] - df["syn_trade_finance"]
    df["gap"] = df["wallet_base"] - df["syn_volume"]
    df["syn_share"] = (df["syn_volume"] / df["wallet_base"]).fillna(0.0).clip(0.0, 1.0)

    total_tx = df["transaction_count"] + df["fx_transaction_count"] + df["trade_transaction_count"]
    density = (total_tx / 5000.0).clip(0.0, 1.0)
    stability = (1.0 - df["recent_growth_signal"].abs().clip(0.0, 1.0)).clip(0.0, 1.0)
    df["confidence"] = (
        0.55
        + 0.20 * df["relationship_depth_score"]
        + 0.15 * density
        + 0.10 * stability
    ).clip(0.55, 0.90)

    top_gap_col = df[["gap_transactional", "gap_fx", "gap_trade_finance"]].idxmax(axis=1)
    df["top_pillar"] = top_gap_col.map(
        {
            "gap_transactional": PILLAR_LABELS["transactional"],
            "gap_fx": PILLAR_LABELS["fx"],
            "gap_trade_finance": PILLAR_LABELS["trade_finance"],
        }
    )
    df["sector_display"] = df["sector"].map(_display_sector)
    return df


@lru_cache(maxsize=1)
def build_wallet_dataset() -> pd.DataFrame:
    benchmarks = load_benchmarks()
    transactional, cross_border, trade = load_raw_tables()
    activity = build_client_activity(transactional, cross_border, trade)
    return estimate_wallet_ranges(activity, benchmarks)
