# briefing_E11_Pepkor Holdings

- provider: `gemini`
- model: `gemini-flash-latest`
- latency: 2491 ms
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
Client: Pepkor Holdings (E11)
Sector: Consumer Goods
Estimated addressable annual banking flow: R247.88B (range R188.18B to R317.52B)
Flow currently captured by Syn Bank: R42.55B
Estimated share of wallet: 17.2%
Uncaptured flow gap: R205.32B
Annual fee revenue that gap represents: R420M
Largest gap product pillar: Transactional
Estimate confidence: 95%
Opportunity rank in portfolio: 6 of 20
Urgency band: Low
Per-pillar uncaptured gap: Transactional R188.67B, FX R4.47B, Trade Finance R12.18B
90-day flow trend: transactional 30.7%, cross-border -14.1%, trade -8.2%
Observed activity: 933,425 transactional items, 43,043 cross-border payments, 3,162 trade instruments

Write the briefing.
```

## Output

SUMMARY: Syn Bank currently captures R42.55B of Pepkor Holdings' banking flow, representing an estimated share of wallet of 17.2%. The single biggest opportunity is capturing the R188.67B uncaptured transactional flow gap, which forms the core of an overall R420M annual fee revenue opportunity.

SIGNALS:
- Syn Bank observes an uncaptured flow gap of R205.32B across an estimated total addressable annual banking flow of R247.88B.
- Transactional banking flow grew by 30.7% over the last 90 days across 933,425 observed transactional items.
- Cross-border payments and trade flows have contracted over the last 90 days by -14.1% and -8.2% respectively.

AGENDA:
- Pitch cash management and payment solutions to capture the R188.67B uncaptured transactional flow gap.
- Review requirements for the client's 43,043 cross-border payments to address the R4.47B uncaptured FX gap.
- Discuss structured trade facilities to target the R12.18B uncaptured trade finance gap across their 3,162 trade instruments.

RISK: Recent 90-day flow contractions in cross-border payments (-14.1%) and trade (-8.2%) signal declining client momentum in international product pillars.
