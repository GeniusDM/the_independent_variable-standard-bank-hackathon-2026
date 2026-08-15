# Methodology: Share of Wallet Estimation

## Overview

The engine estimates each client's **total addressable banking wallet** across four product pillars,
then computes Syn Bank's captured share and the ZAR revenue gap.

## Product Pillars

| Pillar | Proxy Signal | Benchmark Ratio |
|--------|-------------|-----------------|
| Transactional Banking | Annual Revenue | 0.4–0.7% of revenue |
| Cross-Border FX / Global Markets | Foreign Revenue + Foreign Purchases | 1.0–1.5% |
| Trade Finance | COGS + Inventory | 1.5–2.5% |
| Lending & DCM | Total Debt Outstanding | 2.5–3.5% |

All ratios are stored in `config/benchmarks.yaml` and are sector-adjusted.

## Wallet Estimation Formula

```
Total Wallet = Σ (Financial Statement Signal × Sector Benchmark Ratio)
```

## Share of Wallet

```
Share % = Syn Bank Captured Volume / Total Estimated Wallet × 100
Gap ZAR = Total Wallet − Syn Bank Captured Volume
```

## Opportunity Scoring

Clients are ranked using a weighted composite score (see `config/scoring_weights.yaml`):
- 40% absolute ZAR gap
- 20% relative gap %
- 15% relationship depth (active product pillars)
- 15% revenue growth trend (3-year CAGR)
- 10% strategic sector bonus (mining, infrastructure)

## Data Sources

- **Internal**: Syn Bank transactional, SWIFT, and trade finance synthetic datasets
- **External**: JSE annual reports, SENS announcements, CIPC, National Treasury, DealMakers SA

## Assumptions & Limitations

1. Benchmark ratios are derived from public SA banking surveys and may not reflect individual client negotiating power.
2. Foreign revenue/purchases are estimated from financial statement notes where not explicitly disclosed.
3. The model assumes Syn Bank's internal records are complete — gaps are attributed to competitor activity.
4. Lending wallet uses total debt as a proxy; off-balance-sheet facilities are not captured.
5. All ZAR values are nominal; no inflation adjustment is applied within the hackathon scope.
