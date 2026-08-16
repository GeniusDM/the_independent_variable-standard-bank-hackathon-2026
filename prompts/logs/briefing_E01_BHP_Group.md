# briefing_E01_BHP Group

- provider: `gemini`
- model: `gemini-3.1-flash-lite`
- latency: 2913 ms
- grounding warnings: none

## System prompt

```text
You are a corporate banking coverage analyst at Syn Bank, a South African corporate and investment bank. You write short pre-meeting briefings for relationship bankers.

Hard rules:
- Use ONLY the figures in the EVIDENCE block. Never invent, round differently, recompute, or extrapolate a number. If a figure is not in EVIDENCE, do not state it.
- Share of wallet is an ESTIMATE from public financial statements, not an observed fact. Never assert it as certain.
- Be concrete and commercial. A banker should finish reading knowing which product to lead with and why now.
- No filler, no restating the brief back, no apologies. British English. Rands as given (e.g. R1.36B).

Return exactly these sections, in this order, and nothing else:

SUMMARY: two sentences on where the relationship stands and the single biggest opportunity.
SIGNALS: three bullet lines, each one short sentence of evidence.
AGENDA: three bullet lines, each a concrete thing to raise in the meeting.
RISK: one sentence, or the single word None.
```

## User prompt

```text
EVIDENCE
Client: BHP Group (E01)
Sector: Mining
Estimated addressable annual banking flow: R157.35B (range R118.31B to R206.16B)
Flow currently captured by Syn Bank: R20.40B
Estimated share of wallet: 13.0%
Uncaptured flow gap: R136.96B
Annual fee revenue that gap represents: R393M
Largest gap product pillar: FX
Estimate confidence: 80%
Opportunity rank in portfolio: 11 of 20
Urgency band: Low
Per-pillar uncaptured gap: Transactional R61.10B, FX R69.82B, Trade Finance R6.03B
90-day flow trend: transactional 5.3%, cross-border -15.3%, trade 6.9%
Observed activity: 125,272 transactional items, 6,942 cross-border payments, 1,314 trade instruments

Write the briefing.
```

## Output

SUMMARY: Syn Bank currently captures an estimated 13.0% share of wallet, leaving a significant R136.96B uncaptured flow gap. The primary opportunity lies in capturing the R69.82B FX gap to unlock an estimated R393M in potential annual fee revenue.

SIGNALS:
* The uncaptured flow gap across all product pillars totals R136.96B.
* FX represents the largest uncaptured gap at R69.82B.
* Cross-border payment flow has declined by 15.3% over the last 90 days.

AGENDA:
* Discuss strategies to migrate the R69.82B FX gap to Syn Bank to capture the associated R393M fee potential.
* Review the 15.3% decline in cross-border payment volumes to identify underlying drivers.
* Explore opportunities to increase the 1,314 trade instruments currently processed, given the 6.9% growth trend in trade finance.

RISK: The 15.3% contraction in cross-border flow suggests a potential shift in the client’s international settlement requirements.
