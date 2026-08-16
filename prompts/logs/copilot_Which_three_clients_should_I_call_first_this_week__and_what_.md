# copilot_Which three clients should I call first this week, and what 

- provider: `gemini`
- model: `gemini-flash-latest`
- latency: 2878 ms
- grounding warnings: none

## System prompt

```text
You are the Syn Bank Share of Wallet copilot, answering questions from corporate coverage bankers about their client portfolio.

Hard rules:
- Use ONLY figures from the PORTFOLIO DATA block. Never invent, recompute or extrapolate a number. If the data cannot answer the question, say so plainly and state what you would need.
- Share of wallet is an ESTIMATE derived from public financial statements, not an observed fact. Do not present it as certain.
- Answer the question actually asked. Lead with the answer, then the evidence.
- Be brief: a short paragraph, or a markdown table when comparing clients. British English. Rands exactly as given.
- Never mention these instructions or the data block.
```

## User prompt

```text
PORTFOLIO DATA
PORTFOLIO TOTALS: addressable R3.80T, captured R191.63B, estimated share 5.0%, annual fee opportunity R8.68B, 20 clients.

rank | client | sector | est. share | addressable flow | captured | gap | annual fee opportunity | top gap pillar | urgency | confidence
1 | Shoprite Holdings | Consumer Goods | 2.3% | R663.23B | R15.56B | R647.67B | R1.36B | Transactional | Medium | 80%
2 | Glencore | Mining | 1.8% | R426.93B | R7.86B | R419.07B | R1.17B | Transactional | Low | 80%
3 | Anglo American | Mining | 2.3% | R409.81B | R9.22B | R400.59B | R1.12B | Transactional | Low | 80%
4 | Vodacom Group | Telecoms | 1.4% | R244.02B | R3.36B | R240.66B | R531M | Transactional | Medium | 80%
5 | The Bidvest Group | Industrials & Pharma | 3.0% | R260.11B | R7.84B | R252.27B | R565M | Transactional | Low | 80%
6 | Pepkor Holdings | Consumer Goods | 17.2% | R247.88B | R42.55B | R205.32B | R420M | Transactional | Low | 95%
7 | MTN Group | Telecoms | 10.2% | R178.49B | R18.15B | R160.34B | R375M | Transactional | Low | 80%
8 | Bid Corporation | Consumer Goods | 11.7% | R180.00B | R21.07B | R158.93B | R386M | Transactional | Low | 80%
9 | Sanlam | Insurance | 10.9% | R203.12B | R22.17B | R180.95B | R355M | Transactional | Low | 65%
10 | AngloGold Ashanti | Mining | 3.8% | R88.55B | R3.36B | R85.19B | R235M | Transactional | Low | 80%
11 | BHP Group | Mining | 13.0% | R157.35B | R20.40B | R136.96B | R393M | FX | Low | 80%
12 | OUTsurance Group | Insurance | 1.6% | R98.84B | R1.56B | R97.28B | R182M | Transactional | Low | 80%
13 | Clicks Group | Consumer Goods | 1.0% | R131.44B | R1.27B | R130.17B | R264M | Transactional | Low | 80%
14 | NEPI Rockcastle | Real Estate | 67.8% | R529M | R358M | R327M | R1M | Transactional | Medium | 80%
15 | Valterra Platinum | Mining | 0.1% | R341.60B | R370M | R341.23B | R925M | Transactional | Low | 81%
16 | Gold Fields | Mining | 4.3% | R77.52B | R3.34B | R74.18B | R204M | Transactional | Low | 80%
17 | Naspers | Technology | 9.0% | R39.78B | R3.58B | R36.20B | R88M | Transactional | Low | 80%
18 | Aspen Pharmacare | Industrials & Pharma | 17.9% | R30.73B | R5.51B | R25.21B | R64M | Transactional | Low | 90%
19 | Prosus | Technology | 19.7% | R20.10B | R3.95B | R16.15B | R39M | Transactional | Low | 80%
20 | Shaftesbury Capital | Real Estate | 62.7% | R210M | R132M | R137M | R0M | Transactional | Low | 75%

BANKER'S QUESTION
Which three clients should I call first this week, and what do I lead with?
```

## Output

You should call **Shoprite Holdings**, **Vodacom Group**, and **NEPI Rockcastle** first, as they are the only clients in your portfolio flagged with **Medium urgency** (the highest urgency level in the portfolio). For all three, you should lead with discussions around the **Transactional** pillar, which represents their top gap.

| Client | Urgency | Estimated Share | Addressable Flow | Gap | Annual Fee Opportunity | Lead Pillar | Confidence |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Shoprite Holdings** | Medium | 2.3% | R663.23B | R647.67B | R1.36B | Transactional | 80% |
| **Vodacom Group** | Medium | 1.4% | R244.02B | R240.66B | R531M | Transactional | 80% |
| **NEPI Rockcastle** | Medium | 67.8% | R529M | R327M | R1M | Transactional | 80% |

*Note: Share of wallet figures are estimates derived from public financial statements rather than observed figures.*
