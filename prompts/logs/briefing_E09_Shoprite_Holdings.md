# briefing_E09_Shoprite Holdings

- provider: `gemini`
- model: `gemini-3.1-flash-lite`
- latency: 3040 ms
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
Client: Shoprite Holdings (E09)
Sector: Consumer Goods
Estimated addressable annual banking flow: R663.23B (range R502.62B to R850.50B)
Flow currently captured by Syn Bank: R15.56B
Estimated share of wallet: 2.3%
Uncaptured flow gap: R647.67B
Annual fee revenue that gap represents: R1.36B
Largest gap product pillar: Transactional
Estimate confidence: 80%
Opportunity rank in portfolio: 1 of 20
Urgency band: Medium
Per-pillar uncaptured gap: Transactional R576.69B, FX R31.88B, Trade Finance R39.10B
90-day flow trend: transactional 43.7%, cross-border -23.0%, trade 6.6%
Observed activity: 203,157 transactional items, 15,867 cross-border payments, 2,110 trade instruments

Write the briefing.
```

## Output

SUMMARY: Syn Bank currently captures R15.56B of Shoprite’s estimated R663.23B addressable flow, representing an estimated 2.3% share of wallet. The primary opportunity is to aggressively target the R576.69B transactional gap to unlock an estimated R1.36B in annual fee revenue.

SIGNALS:
* Transactional flow has increased by 43.7% over the last 90 days.
* The client currently processes 203,157 transactional items and 15,867 cross-border payments.
* Transactional services represent the largest uncaptured gap at R576.69B.

AGENDA:
* Propose an integrated liquidity management solution to capture a larger portion of the R576.69B transactional gap.
* Discuss the 43.7% growth in transactional activity to identify specific operational pain points.
* Review the R39.10B trade finance gap to align our instruments with their current volume of 2,110 trade items.

RISK: The 23.0% decline in cross-border flow over the last 90 days requires investigation to ensure it does not signal a shift in procurement strategy.
