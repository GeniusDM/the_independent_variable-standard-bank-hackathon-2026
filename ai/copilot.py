"""Scoped copilot patterns grounded in retrieval outputs."""

from __future__ import annotations

import re

from ai.briefing import generate_briefing
from ai.retrieval import retrieve_client, retrieve_fx_gap_clients, retrieve_top_opportunities


def _client_identifier_from_question(question: str) -> str:
    cleaned = question.strip().rstrip("?.!")
    ranked_match = re.search(r"why\s+is\s+(.+?)\s+ranked", cleaned, flags=re.IGNORECASE)
    if ranked_match:
        return ranked_match.group(1).strip()
    match = re.search(r"for\s+(.+)$", cleaned, flags=re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return cleaned


def _as_markdown_table(rows: list[dict]) -> str:
    if not rows:
        return ""
    header = "| Client | Sector | Opportunity Score | Wallet Gap |"
    divider = "|---|---|---:|---:|"
    body = [f"| {r['name']} | {r['sector']} | {r['score']:.1f} | R{r['gap'] / 1_000_000:.0f}M |" for r in rows]
    return "\n".join([header, divider, *body])


def answer_question(question: str) -> dict:
    lower = question.lower()

    if "prioritize" in lower or "top" in lower and "client" in lower:
        top_df, sources = retrieve_top_opportunities(limit=5)
        rows = [
            {
                "name": r["client_name"],
                "sector": r["sector_display"],
                "score": float(r["opportunity_score"]),
                "gap": float(r["gap"]),
            }
            for _, r in top_df.iterrows()
        ]
        content = (
            "## Priority Clients\n"
            "These clients rank highest on the composite opportunity score (gap size, conversion ease, relationship depth, urgency).\n\n"
            f"{_as_markdown_table(rows)}"
        )
        return {"role": "assistant", "content": content, "sources": sources}

    if "losing" in lower and "fx" in lower:
        fx_df, sources = retrieve_fx_gap_clients(limit=5)
        rows = [
            {
                "name": r["client_name"],
                "sector": r["sector_display"],
                "score": float(r["opportunity_score"]),
                "gap": float(r["gap_fx"]),
            }
            for _, r in fx_df.iterrows()
        ]
        content = (
            "## FX Leakage Candidates\n"
            "These clients show the largest estimated uncaptured FX wallet gaps.\n\n"
            f"{_as_markdown_table(rows)}"
        )
        return {"role": "assistant", "content": content, "sources": sources}

    if "why" in lower and "ranked" in lower:
        identifier = _client_identifier_from_question(question)
        row, sources = retrieve_client(identifier)
        if row is None:
            return {
                "role": "assistant",
                "content": "I could not match that client to a grounded record. Try the exact client name from the Clients page.",
                "sources": [],
            }

        content = (
            f"## Why {row['client_name']} Is Ranked #{int(row['rank'])}\n"
            f"- Opportunity score: **{row['opportunity_score']:.1f}**\n"
            f"- Wallet gap: **R{row['gap'] / 1_000_000:.0f}M**\n"
            f"- Top pillar: **{row['top_pillar']}**\n"
            f"- Confidence: **{row['confidence'] * 100:.0f}%**\n"
            f"- Signal: {row['tx_growth_90d']:.1%} TX growth, {row['fx_growth_90d']:.1%} FX growth, {row['trade_growth_90d']:.1%} trade growth over 90 days."
        )
        return {"role": "assistant", "content": content, "sources": sources}

    if "briefing" in lower or "meeting" in lower:
        identifier = _client_identifier_from_question(question)
        briefing = generate_briefing(identifier)
        content = (
            f"## Client Briefing: {identifier}\n"
            f"{briefing['summary']}\n\n"
            "### Key Signals\n"
            + "\n".join([f"- {item}" for item in briefing["keySignals"]])
            + "\n\n### Recommended Agenda\n"
            + "\n".join([f"- {item}" for item in briefing["recommendedAgenda"]])
            + (f"\n\n### Risk\n- {briefing['risk']}" if briefing["risk"] else "")
        )
        return {"role": "assistant", "content": content, "sources": briefing.get("sources", [])}

    return {
        "role": "assistant",
        "content": (
            "I can answer four grounded question types:\n"
            "- Which clients should I prioritize\n"
            "- Which clients are losing FX business\n"
            "- Why a client is ranked first\n"
            "- Generate a client briefing"
        ),
        "sources": [],
    }
