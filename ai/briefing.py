"""Client briefing generation.

The deterministic payload built by models.explainability is always produced
first. The LLM's job is to turn that evidence into something a coverage banker
would actually want to read ten minutes before a meeting — it is given the
figures and told to reuse them verbatim, never to compute or estimate.

If no provider is configured or the call fails, the deterministic payload is
returned unchanged, so the product degrades in quality rather than breaking.
"""

from __future__ import annotations

from ai import llm
from ai.retrieval import retrieve_briefing

SYSTEM_PROMPT = """You are a corporate banking coverage analyst at Syn Bank, a \
South African corporate and investment bank. You write short pre-meeting \
briefings for relationship bankers.

Hard rules:
- Use ONLY the figures in the EVIDENCE block. Never invent, round differently, \
recompute, or extrapolate a number. If a figure is not in EVIDENCE, do not state it.
- Share of wallet is an ESTIMATE from public financial statements, not an \
observed fact. Never assert it as certain.
- Be concrete and commercial. A banker should finish reading knowing which \
product to lead with and why now.
- No filler, no restating the brief back, no apologies. British English. \
Rands as given (e.g. R1.36B).

Return exactly these sections, in this order, and nothing else:

SUMMARY: two sentences on where the relationship stands and the single biggest \
opportunity.
SIGNALS: three bullet lines, each one short sentence of evidence.
AGENDA: three bullet lines, each a concrete thing to raise in the meeting.
RISK: one sentence, or the single word None."""


def _evidence_block(row) -> str:
    def zar(value: float) -> str:
        value = float(value)
        if abs(value) >= 1e12:
            return f"R{value / 1e12:.2f}T"
        if abs(value) >= 1e9:
            return f"R{value / 1e9:.2f}B"
        return f"R{value / 1e6:.0f}M"

    lines = [
        f"Client: {row['client_name']} ({row['client_id']})",
        f"Sector: {row['sector_display']}",
        f"Estimated addressable annual banking flow: {zar(row['wallet_base'])} "
        f"(range {zar(row['wallet_low'])} to {zar(row['wallet_high'])})",
        f"Flow currently captured by Syn Bank: {zar(row['syn_volume'])}",
        f"Estimated share of wallet: {float(row['syn_share']) * 100:.1f}%",
        f"Uncaptured flow gap: {zar(row['gap'])}",
        f"Annual fee revenue that gap represents: {zar(row['revenue_opportunity'])}",
        f"Largest gap product pillar: {row['top_pillar']}",
        f"Estimate confidence: {float(row['confidence']) * 100:.0f}%",
        f"Opportunity rank in portfolio: {int(row['rank'])} of 20",
        f"Urgency band: {row['urgency']}",
        "Per-pillar uncaptured gap: "
        + ", ".join(
            [
                f"Transactional {zar(row['gap_transactional'])}",
                f"FX {zar(row['gap_fx'])}",
                f"Trade Finance {zar(row['gap_trade_finance'])}",
            ]
        ),
        "90-day flow trend: "
        + ", ".join(
            [
                f"transactional {float(row['tx_growth_90d']):.1%}",
                f"cross-border {float(row['fx_growth_90d']):.1%}",
                f"trade {float(row['trade_growth_90d']):.1%}",
            ]
        ),
        f"Observed activity: {int(row['transaction_count']):,} transactional items, "
        f"{int(row['fx_transaction_count']):,} cross-border payments, "
        f"{int(row['trade_transaction_count']):,} trade instruments",
    ]
    return "\n".join(lines)


def _parse_sections(text: str) -> dict:
    sections: dict[str, list[str]] = {}
    current = None
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        upper = line.upper()
        for label in ("SUMMARY", "SIGNALS", "AGENDA", "RISK"):
            if upper.startswith(label):
                current = label
                remainder = line[len(label):].lstrip(": ").strip()
                sections[current] = [remainder] if remainder else []
                break
        else:
            if current:
                sections[current].append(line.lstrip("-•* ").strip())
    return sections


def generate_briefing(client_identifier: str) -> dict:
    payload, sources = retrieve_briefing(client_identifier)
    if payload is None:
        return {
            "clientId": client_identifier,
            "summary": "No grounded briefing is available for this client identifier.",
            "keySignals": [],
            "recommendedAgenda": [],
            "risk": None,
            "sources": [],
            "generatedBy": "none",
        }

    payload["sources"] = sources
    payload["generatedBy"] = "deterministic"

    row = payload.pop("_row", None)
    if row is None:
        return payload

    evidence = _evidence_block(row)
    try:
        response = llm.generate(
            SYSTEM_PROMPT,
            f"EVIDENCE\n{evidence}\n\nWrite the briefing.",
            allowed_facts=evidence,
            log_name=f"briefing_{row['client_id']}_{row['client_name']}",
        )
    except llm.LLMUnavailable:
        return payload  # deterministic text stands

    parsed = _parse_sections(response.text)
    summary = " ".join(parsed.get("SUMMARY", [])).strip()
    signals = [s for s in parsed.get("SIGNALS", []) if s]
    agenda = [a for a in parsed.get("AGENDA", []) if a]
    risk = " ".join(parsed.get("RISK", [])).strip()

    # Only take the model's version where it actually produced content, so a
    # malformed response degrades section by section rather than wholesale.
    if summary:
        payload["summary"] = summary
    if signals:
        payload["keySignals"] = signals
    if agenda:
        payload["recommendedAgenda"] = agenda
    if risk:
        payload["risk"] = None if risk.lower().startswith("none") else risk

    payload["generatedBy"] = f"{response.provider}:{response.model}"
    payload["latencyMs"] = round(response.latency_ms)
    payload["cached"] = response.cached
    if response.grounding_warnings:
        payload["groundingWarnings"] = response.grounding_warnings
    return payload
