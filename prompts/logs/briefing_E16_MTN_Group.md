# briefing_E16_MTN Group

- provider: `gemini`
- model: `gemini-3.1-flash-lite`
- latency: 1781 ms
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
Client: MTN Group (E16)
Sector: Telecoms
Estimated addressable annual banking flow: R178.49B (range R137.41B to R229.74B)
Flow currently captured by Syn Bank: R18.15B
Estimated share of wallet: 10.2%
Uncaptured flow gap: R160.34B
Annual fee revenue that gap represents: R375M
Largest gap product pillar: Transactional
Estimate confidence: 80%
Opportunity rank in portfolio: 7 of 20
Urgency band: Low
Per-pillar uncaptured gap: Transactional R114.87B, FX R42.82B, Trade Finance R2.65B
90-day flow trend: transactional -1.2%, cross-border -15.0%, trade 33.1%
Observed activity: 211,227 transactional items, 31,910 cross-border payments, 2,421 trade instruments

Write the briefing.
```

## Output

SUMMARY: Syn Bank currently captures an estimated 10.2% of MTN Group’s addressable annual banking flow. The primary opportunity lies in closing the R114.87B transactional gap to capture a potential R375M in annual fee revenue.

SIGNALS:
* We currently capture R18.15B of the R178.49B total addressable annual banking flow.
* Transactional flow has declined by 1.2% over the last 90 days, while trade instruments have grown by 33.1%.
* The transactional pillar represents the largest uncaptured gap at R114.87B.

AGENDA:
* Propose a review of the current transactional mandate to capture a larger portion of the R114.87B uncaptured flow.
* Discuss the 33.1% growth in trade instrument activity to identify how Syn Bank can support increased trade finance requirements.
* Address the 15.0% decline in cross-border flow to determine if this is a shift in strategy or a temporary market fluctuation.

RISK: None.
