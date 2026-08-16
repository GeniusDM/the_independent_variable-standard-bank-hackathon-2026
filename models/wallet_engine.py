"""Two-sided share-of-wallet estimation.

The addressable banking flow for each client is sized TOP-DOWN from that
company's published financial statements. The flow Syn Bank actually captures is
measured BOTTOM-UP from the internal transaction datasets. Share is the ratio of
the two.

The two sides are computed from independent inputs, which is the point: an
earlier version of this module derived both the wallet and the captured amount
from the same internal flows multiplied by an assumed capture rate, so share
collapsed to that assumption and sat near 20% for every client regardless of
their size. See docs/methodology.md.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).parents[1]
CONFIG_PATH = ROOT / "config" / "benchmarks.yaml"
RAW_DIR = ROOT / "data" / "raw"
EXTERNAL_PATH = ROOT / "data" / "external" / "company_financials.csv"

PILLARS = ("transactional", "fx", "trade_finance")
BANDS = ("low", "base", "high")

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

_SECTOR_ALIASES = {
    "retail": "consumer",
    "consumer_goods": "consumer",
    "industrials": "industrials_pharma",
    "pharma": "industrials_pharma",
}


def load_benchmarks() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _normalize_sector(sector: str | None) -> str:
    if not sector or (isinstance(sector, float) and pd.isna(sector)):
        return "consumer"
    value = str(sector).strip().lower().replace(" ", "_").replace("&", "and")
    return _SECTOR_ALIASES.get(value, value)


def _display_sector(sector: str) -> str:
    key = _normalize_sector(sector)
    return SECTOR_LABELS.get(key, key.replace("_", " ").title())


def _sector_band(benchmarks: dict, pillar: str, sector: str, band: str) -> float:
    cfg = benchmarks["pillars"][pillar]
    scoped = cfg.get("by_sector", {}).get(_normalize_sector(sector))
    if scoped and band in scoped:
        return float(scoped[band])
    return float(cfg["default"][band])


def _fee_margin(benchmarks: dict, pillar: str) -> float:
    return float(benchmarks["pillars"][pillar]["fee_margin"])


# --------------------------------------------------------------------------
# Top-down: addressable flow from published financials
# --------------------------------------------------------------------------

def load_external_financials(benchmarks: dict | None = None) -> pd.DataFrame:
    """Published financials per client, normalised to ZAR and gap-filled.

    Imputed values are flagged so the methodology and the dashboard can be
    honest about which inputs are reported and which are derived.
    """
    if benchmarks is None:
        benchmarks = load_benchmarks()

    df = pd.read_csv(EXTERNAL_PATH)
    df["sector"] = df["sector"].map(_normalize_sector)

    gross_margin = benchmarks["gross_margin_by_sector"]
    inv_ratio = benchmarks["inventory_to_cogs_by_sector"]

    df["cogs_imputed"] = df["cogs_zar_m"].isna()
    df["cogs_zar_m"] = df.apply(
        lambda r: r["cogs_zar_m"]
        if pd.notna(r["cogs_zar_m"])
        else r["revenue_zar_m"] * (1.0 - float(gross_margin.get(r["sector"], 0.30))),
        axis=1,
    )

    df["inventory_imputed"] = df["inventory_zar_m"].isna()
    df["inventory_zar_m"] = df.apply(
        lambda r: r["inventory_zar_m"]
        if pd.notna(r["inventory_zar_m"])
        else r["cogs_zar_m"] * float(inv_ratio.get(r["sector"], 0.15)),
        axis=1,
    )

    df["total_debt_zar_m"] = df["total_debt_zar_m"].fillna(0.0)

    # Convert to ZAR units to match the internal transaction data.
    for col in ("revenue_zar_m", "cogs_zar_m", "inventory_zar_m", "total_debt_zar_m"):
        df[col.replace("_zar_m", "_zar")] = df[col] * 1_000_000.0

    # SA-attributable base. Syn Bank is a South African bank, so a global group's
    # addressable wallet is only the portion of its activity that touches SA.
    df["addressable_revenue_zar"] = df["revenue_zar"] * df["sa_attribution_share"]
    df["addressable_foreign_revenue_zar"] = (
        df["revenue_zar"] * df["foreign_revenue_share"] * df["sa_attribution_share"]
    )
    df["addressable_cogs_inventory_zar"] = (
        df["cogs_zar"] + df["inventory_zar"]
    ) * df["sa_attribution_share"]

    return df.rename(columns={"client_id": "client_id", "company": "client_name"})


def _signal_column(pillar: str) -> str:
    return {
        "transactional": "addressable_revenue_zar",
        "fx": "addressable_foreign_revenue_zar",
        "trade_finance": "addressable_cogs_inventory_zar",
    }[pillar]


def estimate_addressable_flow(
    external_df: pd.DataFrame, benchmarks: dict | None = None
) -> pd.DataFrame:
    """Top-down addressable flow per pillar, in low/base/high bands."""
    if benchmarks is None:
        benchmarks = load_benchmarks()

    df = external_df.copy()
    for pillar in PILLARS:
        signal = _signal_column(pillar)
        for band in BANDS:
            df[f"addressable_{pillar}_{band}"] = df.apply(
                lambda r, p=pillar, b=band: r[signal]
                * _sector_band(benchmarks, p, r["sector"], b),
                axis=1,
            )

    for band in BANDS:
        df[f"addressable_{band}"] = sum(
            df[f"addressable_{pillar}_{band}"] for pillar in PILLARS
        )

    return df


# --------------------------------------------------------------------------
# Bottom-up: captured flow measured from the internal datasets
# --------------------------------------------------------------------------

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


def _annualise(df: pd.DataFrame, date_col: str, value_col: str) -> pd.DataFrame:
    """Captured flow over the most recent 12 months, so it is comparable to an
    annual financial-statement figure."""
    latest = df[date_col].max()
    window_start = latest - pd.Timedelta(days=365)
    recent = df[df[date_col] > window_start]
    return (
        recent.groupby("entity_id", as_index=False)[value_col]
        .sum()
        .rename(columns={value_col: "captured_12m"})
    )


def _growth(df: pd.DataFrame, date_col: str, value_col: str) -> pd.DataFrame:
    latest = df[date_col].max()
    recent_start = latest - pd.Timedelta(days=90)
    prior_start = latest - pd.Timedelta(days=180)

    recent = (
        df[df[date_col] > recent_start]
        .groupby("entity_id", as_index=False)[value_col]
        .sum()
        .rename(columns={value_col: "recent"})
    )
    prior = (
        df[(df[date_col] > prior_start) & (df[date_col] <= recent_start)]
        .groupby("entity_id", as_index=False)[value_col]
        .sum()
        .rename(columns={value_col: "prior"})
    )
    merged = recent.merge(prior, on="entity_id", how="outer").fillna(0.0)
    merged["growth"] = merged.apply(
        lambda r: (r["recent"] - r["prior"]) / r["prior"] if r["prior"] > 0 else 0.0,
        axis=1,
    )
    return merged[["entity_id", "growth"]]


def measure_captured_flow(
    transactional: pd.DataFrame, cross_border: pd.DataFrame, trade: pd.DataFrame
) -> pd.DataFrame:
    """Bottom-up: what Syn Bank actually saw, per client, over the last 12 months."""
    tx = (
        transactional.groupby("entity_id", as_index=False)
        .agg(
            internal_name=("entity_name", "first"),
            internal_sector=("sector", "first"),
            transaction_count=("amount_zar", "size"),
            channel_count=("channel", "nunique"),
            inbound_ratio=("direction", lambda s: float((s == "inbound").mean())),
        )
        .merge(_annualise(transactional, "date", "amount_zar"), on="entity_id", how="left")
        .rename(columns={"captured_12m": "captured_transactional"})
        .merge(_growth(transactional, "date", "amount_zar"), on="entity_id", how="left")
        .rename(columns={"growth": "tx_growth_90d"})
    )

    fx = (
        cross_border.groupby("entity_id", as_index=False)
        .agg(
            fx_transaction_count=("value_zar", "size"),
            corridor_count=("counterparty_country", "nunique"),
        )
        .merge(_annualise(cross_border, "date", "value_zar"), on="entity_id", how="left")
        .rename(columns={"captured_12m": "captured_fx"})
        .merge(_growth(cross_border, "date", "value_zar"), on="entity_id", how="left")
        .rename(columns={"growth": "fx_growth_90d"})
    )

    tf = (
        trade.groupby("entity_id", as_index=False)
        .agg(
            trade_transaction_count=("value_zar", "size"),
            avg_tenor_days=("tenor_days", "mean"),
            instrument_count=("instrument_type", "nunique"),
        )
        .merge(_annualise(trade, "date", "value_zar"), on="entity_id", how="left")
        .rename(columns={"captured_12m": "captured_trade_finance"})
        .merge(_growth(trade, "date", "value_zar"), on="entity_id", how="left")
        .rename(columns={"growth": "trade_growth_90d"})
    )

    df = tx.merge(fx, on="entity_id", how="outer").merge(tf, on="entity_id", how="outer")
    numeric_defaults = {
        "captured_transactional": 0.0,
        "captured_fx": 0.0,
        "captured_trade_finance": 0.0,
        "transaction_count": 0,
        "fx_transaction_count": 0,
        "trade_transaction_count": 0,
        "channel_count": 0,
        "corridor_count": 0,
        "instrument_count": 0,
        "inbound_ratio": 0.0,
        "avg_tenor_days": 0.0,
        "tx_growth_90d": 0.0,
        "fx_growth_90d": 0.0,
        "trade_growth_90d": 0.0,
    }
    df = df.fillna(numeric_defaults)

    df["captured_total"] = (
        df["captured_transactional"] + df["captured_fx"] + df["captured_trade_finance"]
    )
    df["active_pillars"] = (
        (df["captured_transactional"] > 0).astype(int)
        + (df["captured_fx"] > 0).astype(int)
        + (df["captured_trade_finance"] > 0).astype(int)
    )
    df["relationship_depth_score"] = df["active_pillars"] / 3.0
    df["recent_growth_signal"] = (
        df[["tx_growth_90d", "fx_growth_90d", "trade_growth_90d"]].mean(axis=1).clip(-1.0, 2.0)
    )
    return df.rename(columns={"entity_id": "client_id"})


# --------------------------------------------------------------------------
# Combine the two sides
# --------------------------------------------------------------------------

def _safe_ratio(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    """Element-wise division that yields 0.0 wherever the denominator is 0.

    A client can legitimately have a zero addressable base in a pillar — a purely
    domestic client has no foreign revenue and so no FX wallet — and that must
    read as "no opportunity here", not as a missing value.
    """
    result = pd.Series(0.0, index=numerator.index, dtype="float64")
    mask = denominator.astype("float64") > 0.0
    result[mask] = (
        numerator.astype("float64")[mask] / denominator.astype("float64")[mask]
    )
    return result


def compute_share_of_wallet(
    addressable_df: pd.DataFrame,
    captured_df: pd.DataFrame,
    benchmarks: dict | None = None,
) -> pd.DataFrame:
    if benchmarks is None:
        benchmarks = load_benchmarks()

    df = addressable_df.merge(captured_df, on="client_id", how="left")

    for col in ("captured_transactional", "captured_fx", "captured_trade_finance"):
        df[col] = df[col].fillna(0.0)

    df["captured_total"] = (
        df["captured_transactional"] + df["captured_fx"] + df["captured_trade_finance"]
    )

    # Per-pillar share, gap and the fee-equivalent revenue that gap represents.
    for pillar in PILLARS:
        addressable = df[f"addressable_{pillar}_base"]
        captured = df[f"captured_{pillar}"]
        margin = _fee_margin(benchmarks, pillar)

        df[f"share_{pillar}"] = _safe_ratio(captured, addressable)
        df[f"gap_{pillar}"] = (addressable - captured).clip(lower=0.0)
        df[f"revenue_opportunity_{pillar}"] = df[f"gap_{pillar}"] * margin

    df["addressable_base"] = sum(df[f"addressable_{p}_base"] for p in PILLARS)
    df["gap"] = sum(df[f"gap_{p}"] for p in PILLARS)
    df["revenue_opportunity"] = sum(df[f"revenue_opportunity_{p}"] for p in PILLARS)

    df["syn_share"] = _safe_ratio(df["captured_total"], df["addressable_base"])

    # A share above 1 means the top-down estimate under-sized that client rather
    # than that Syn Bank holds more than the whole wallet. Flag rather than hide.
    df["share_exceeds_estimate"] = df["syn_share"] > 1.0

    # Confidence reflects how much of the estimate rests on reported rather than
    # imputed inputs, and how much internal activity supports the measurement.
    reported_inputs = (
        (~df["cogs_imputed"]).astype(float) + (~df["inventory_imputed"]).astype(float)
    ) / 2.0
    proxy_penalty = df["source_quality"].isin(["proxy", "estimated"]).astype(float) * 0.15
    activity = (
        (df["transaction_count"] + df["fx_transaction_count"] + df["trade_transaction_count"])
        / 5000.0
    ).clip(0.0, 1.0)

    df["confidence"] = (
        0.45
        + 0.20 * reported_inputs
        + 0.20 * df["relationship_depth_score"]
        + 0.15 * activity
        - proxy_penalty
    ).clip(0.35, 0.95)

    gap_cols = [f"gap_{p}" for p in PILLARS]
    df["top_pillar"] = df[gap_cols].idxmax(axis=1).map(
        {f"gap_{p}": PILLAR_LABELS[p] for p in PILLARS}
    )
    df["sector_display"] = df["sector"].map(_display_sector)

    # Backwards-compatible aliases for the API and explainability layers.
    df["wallet_low"] = df["addressable_low"]
    df["wallet_base"] = df["addressable_base"]
    df["wallet_high"] = df["addressable_high"]
    df["syn_volume"] = df["captured_total"]
    df["gap_transactional"] = df["gap_transactional"]
    df["gap_fx"] = df["gap_fx"]
    df["gap_trade_finance"] = df["gap_trade_finance"]
    df["transactional_flow"] = df["captured_transactional"]
    df["fx_flow"] = df["captured_fx"]
    df["trade_flow"] = df["captured_trade_finance"]

    return df


def sensitivity_analysis(
    external_df: pd.DataFrame,
    captured_df: pd.DataFrame,
    shifts: tuple[float, ...] = (-0.25, -0.10, 0.0, 0.10, 0.25),
    benchmarks: dict | None = None,
) -> pd.DataFrame:
    """How far does portfolio share move when every flow multiple is shifted?

    This is the honest answer to "how much do your assumptions drive the result".
    """
    if benchmarks is None:
        benchmarks = load_benchmarks()

    rows = []
    for shift in shifts:
        scaled = {
            **benchmarks,
            "pillars": {
                pillar: {
                    **cfg,
                    "default": {b: cfg["default"][b] * (1 + shift) for b in BANDS},
                    "by_sector": {
                        sector: {b: bands[b] * (1 + shift) for b in BANDS}
                        for sector, bands in cfg.get("by_sector", {}).items()
                    },
                }
                for pillar, cfg in benchmarks["pillars"].items()
            },
        }
        addressable = estimate_addressable_flow(external_df, scaled)
        combined = compute_share_of_wallet(addressable, captured_df, scaled)
        rows.append(
            {
                "multiplier_shift": shift,
                "portfolio_addressable": float(combined["addressable_base"].sum()),
                "portfolio_captured": float(combined["captured_total"].sum()),
                "portfolio_share": float(
                    combined["captured_total"].sum() / combined["addressable_base"].sum()
                ),
                "portfolio_gap": float(combined["gap"].sum()),
                "revenue_opportunity": float(combined["revenue_opportunity"].sum()),
            }
        )
    return pd.DataFrame(rows)


@lru_cache(maxsize=1)
def build_wallet_dataset() -> pd.DataFrame:
    benchmarks = load_benchmarks()
    external = load_external_financials(benchmarks)
    addressable = estimate_addressable_flow(external, benchmarks)
    transactional, cross_border, trade = load_raw_tables()
    captured = measure_captured_flow(transactional, cross_border, trade)
    return compute_share_of_wallet(addressable, captured, benchmarks)
