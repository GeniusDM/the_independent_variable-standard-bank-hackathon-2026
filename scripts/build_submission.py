#!/usr/bin/env python3
"""Build the submission artefacts from live model output.

    python scripts/build_submission.py

Writes:
    docs/figures/*.png            charts shared by the one-pager and the deck
    docs/executive_summary.html   the one-page solution summary
    docs/presentation_deck.pptx   the judging deck

Every figure is read from the model at build time, so the documents cannot drift
from the code. Convert the one-pager to PDF with:

    msedge --headless --disable-gpu --print-to-pdf=docs/executive_summary.pdf \
        --no-pdf-header-footer file:///<abs>/docs/executive_summary.html
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

logging.disable(logging.WARNING)

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from models.opportunity_engine import build_scored_dataset  # noqa: E402
from models.wallet_engine import (  # noqa: E402
    load_benchmarks,
    load_external_financials,
    load_raw_tables,
    measure_captured_flow,
    sensitivity_analysis,
)

DOCS = ROOT / "docs"
FIGS = DOCS / "figures"

# Validated categorical slots 1-2: blue = held by Syn Bank, orange = not held.
BLUE, ORANGE = "#2a78d6", "#eb6834"
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e6e6e3"

TEAM = "The Independent Variable"
MEMBERS = "Daniel Mataranyika · Herton Mabongue"

plt.rcParams.update(
    {
        "figure.dpi": 200,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.edgecolor": GRID,
        "axes.labelcolor": MUTED,
        "axes.titlecolor": INK,
        "axes.titlesize": 11,
        "axes.titleweight": "600",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.color": GRID,
        "grid.linewidth": 0.7,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "font.size": 9,
        "legend.frameon": False,
    }
)


def zar(v: float) -> str:
    v = float(v)
    if abs(v) >= 1e12:
        return f"R{v / 1e12:.2f}tn"
    if abs(v) >= 1e9:
        return f"R{v / 1e9:.2f}bn"
    if abs(v) >= 1e6:
        return f"R{v / 1e6:,.0f}M"
    return f"R{v:,.0f}"


# --------------------------------------------------------------------------
# figures
# --------------------------------------------------------------------------

def fig_share_by_client(df, portfolio_share: float) -> Path:
    d = df.sort_values("syn_share")
    fig, ax = plt.subplots(figsize=(7.4, 5.0))
    ax.axvline(portfolio_share * 100, color=ORANGE, linewidth=1.5, zorder=2)
    bars = ax.barh(d["client_name"], d["syn_share"] * 100, height=0.62, color=BLUE, zorder=3)
    for bar, v in zip(bars, d["syn_share"] * 100):
        ax.text(
            v + 1.1,
            bar.get_y() + bar.get_height() / 2,
            f"{v:.1f}%",
            va="center",
            fontsize=8,
            color=MUTED,
            zorder=4,
            bbox=dict(facecolor="white", edgecolor="none", pad=1.1),
        )
    ax.text(
        portfolio_share * 100 + 1.1,
        -1.05,
        f"portfolio {portfolio_share * 100:.1f}%",
        color=ORANGE,
        fontsize=8,
        fontweight="600",
    )
    ax.set_xlabel("Estimated share of wallet (%)")
    ax.set_xlim(0, 76)
    ax.grid(axis="y", visible=False)
    path = FIGS / "share_by_client.png"
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path


def fig_opportunity(df) -> Path:
    top = df.head(8).iloc[::-1]
    fig, ax = plt.subplots(figsize=(7.4, 3.4))
    bars = ax.barh(
        top["client_name"], top["revenue_opportunity"] / 1e6, height=0.6, color=BLUE, zorder=3
    )
    for bar, row in zip(bars, top.itertuples()):
        ax.text(
            row.revenue_opportunity / 1e6 + 16,
            bar.get_y() + bar.get_height() / 2,
            f"R{row.revenue_opportunity / 1e6:,.0f}M   ·   {row.syn_share * 100:.1f}% held",
            va="center",
            fontsize=8.5,
            color=INK,
            fontweight="600",
            zorder=4,
            bbox=dict(facecolor="white", edgecolor="none", pad=1.2),
        )
    ax.set_xlabel("Annual fee revenue opportunity (ZAR millions)")
    ax.set_xlim(0, top["revenue_opportunity"].max() / 1e6 * 1.72)
    ax.grid(axis="y", visible=False)
    path = FIGS / "opportunity.png"
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path


def fig_before_after(old_shares, new_shares) -> Path:
    fig, ax = plt.subplots(figsize=(7.4, 2.3))
    rng = np.random.default_rng(7)
    for y, (vals, colour, label) in enumerate(
        [(old_shares, ORANGE, "Original"), (new_shares, BLUE, "Two-sided")]
    ):
        ax.scatter(
            vals * 100,
            np.full(len(vals), y) + rng.uniform(-0.1, 0.1, len(vals)),
            s=36,
            color=colour,
            alpha=0.85,
            linewidth=1.1,
            edgecolor="white",
            zorder=3,
        )
        lo, hi = vals.min() * 100, vals.max() * 100
        ax.annotate(
            "",
            xy=(lo, y - 0.27),
            xytext=(hi, y - 0.27),
            arrowprops=dict(arrowstyle="<->", color=MUTED, linewidth=0.85),
        )
        ax.text(
            (lo + hi) / 2,
            y - 0.4,
            f"{hi - lo:.1f} pt spread",
            ha="center",
            va="top",
            fontsize=8,
            color=MUTED,
        )
    ax.set_yticks([0, 1])
    ax.set_yticklabels(["Original", "Two-sided"], fontsize=9, color=INK)
    ax.set_xlabel("Estimated share of wallet (%)")
    ax.set_xlim(-3, 75)
    ax.set_ylim(-0.72, 1.45)
    ax.grid(axis="y", visible=False)
    path = FIGS / "before_after.png"
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path


def fig_sensitivity(sens) -> Path:
    fig, ax = plt.subplots(figsize=(6.4, 2.9))
    x = sens["multiplier_shift"] * 100
    ax.plot(
        x,
        sens["portfolio_share"] * 100,
        color=BLUE,
        linewidth=2,
        marker="o",
        markersize=7,
        markeredgecolor="white",
        markeredgewidth=1.5,
        zorder=3,
    )
    for xv, yv in zip(x, sens["portfolio_share"] * 100):
        ax.annotate(
            f"{yv:.2f}%",
            (xv, yv),
            textcoords="offset points",
            xytext=(0, 10),
            ha="center",
            fontsize=8,
            color=MUTED,
        )
    ax.set_xlabel("Shift applied to every flow multiple (%)")
    ax.set_ylabel("Portfolio share (%)")
    ax.set_xticks(x)
    ax.set_ylim(3.4, 7.4)
    path = FIGS / "sensitivity.png"
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path


def fig_pillars(df) -> Path:
    pillars = ["Transactional", "FX", "Trade finance"]
    capt = [
        df["captured_transactional"].sum(),
        df["captured_fx"].sum(),
        df["captured_trade_finance"].sum(),
    ]
    gap = [df["gap_transactional"].sum(), df["gap_fx"].sum(), df["gap_trade_finance"].sum()]

    fig, ax = plt.subplots(figsize=(6.4, 2.7))
    y = np.arange(3)
    ax.barh(y, np.array(capt) / 1e9, height=0.55, color=BLUE, label="Captured", zorder=3)
    ax.barh(
        y,
        np.array(gap) / 1e9,
        height=0.55,
        left=np.array(capt) / 1e9 + 12,
        color=ORANGE,
        label="Uncaptured",
        zorder=3,
    )
    for i, (c, g) in enumerate(zip(capt, gap)):
        ax.text((c + g) / 1e9 + 45, i, f"{c / (c + g) * 100:.1f}% held", va="center", fontsize=8, color=MUTED)
    ax.set_yticks(y)
    ax.set_yticklabels(pillars)
    ax.set_xlabel("Annual flow (ZAR billions)")
    ax.set_xlim(0, 3700)
    ax.set_ylim(-0.6, 2.9)
    ax.grid(axis="y", visible=False)
    ax.legend(loc="upper right", ncol=2)
    path = FIGS / "pillars.png"
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path


# --------------------------------------------------------------------------
# the original circular model, for the before/after comparison
# --------------------------------------------------------------------------

def original_model(transactional):
    """Returns (shares, wallet_size_ratio) for the original circular model.

    The size ratio is taken from that model's own wallet estimate, so the claim
    "it gave very different companies the same answer" is stated on its terms
    rather than mixing in the replacement's numbers.
    """
    g = (
        transactional.groupby("entity_id")
        .agg(
            flow=("amount_zar", "sum"),
            transaction_count=("amount_zar", "size"),
            channel_count=("channel", "nunique"),
            inbound_ratio=("direction", lambda s: float((s == "inbound").mean())),
        )
        .reset_index()
    )
    ratio = (
        0.10
        + 0.05 * np.minimum(g["transaction_count"] / 4500.0, 1.0)
        + 0.04 * np.minimum(g["channel_count"] / 4.0, 1.0)
        + 0.03 * g["inbound_ratio"]
    )
    wallet = g["flow"] * 0.0018
    return np.clip(ratio.to_numpy(), 0.08, 0.32), float(wallet.max() / wallet.min())


def main() -> int:
    FIGS.mkdir(parents=True, exist_ok=True)

    benchmarks = load_benchmarks()
    external = load_external_financials(benchmarks)
    transactional, cross_border, trade = load_raw_tables()
    captured = measure_captured_flow(transactional, cross_border, trade)
    df = build_scored_dataset()
    sens = sensitivity_analysis(external, captured, benchmarks=benchmarks)

    addressable = float(df["addressable_base"].sum())
    captured_total = float(df["captured_total"].sum())
    share = captured_total / addressable
    gap = float(df["gap"].sum())
    oppty = float(df["revenue_opportunity"].sum())

    facts = {
        "addressable": addressable,
        "captured": captured_total,
        "share": share,
        "gap": gap,
        "oppty": oppty,
        "clients": len(df),
        "share_min": float(df["syn_share"].min()),
        "share_max": float(df["syn_share"].max()),
        "sens_min": float(sens["portfolio_share"].min()),
        "sens_max": float(sens["portfolio_share"].max()),
        "top": df.head(5),
        "sens": sens,
        # Derived rather than hardcoded, so the prose cannot drift from the model.
        "lead_pillar": df["top_pillar"].value_counts().idxmax(),
        "lead_pillar_n": int(df["top_pillar"].value_counts().max()),
        "estimated_inputs": int((df["source_quality"] == "estimated").sum()),
    }

    old, size_ratio = original_model(transactional)
    facts["old_spread"] = float(old.max() - old.min())
    facts["size_ratio"] = size_ratio
    figs = {
        "share": fig_share_by_client(df, share),
        "oppty": fig_opportunity(df),
        "before_after": fig_before_after(old, df["syn_share"].to_numpy()),
        "sensitivity": fig_sensitivity(sens),
        "pillars": fig_pillars(df),
    }
    print(f"  figures -> {FIGS.relative_to(ROOT)} ({len(figs)})")

    from _submission_docs import build_deck, build_onepager  # noqa: E402

    build_onepager(DOCS, figs, facts, old)
    build_deck(DOCS, figs, facts)
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent))
    raise SystemExit(main())
