# Methodology: Share of Wallet Estimation

**Team The Independent Variable** — Daniel Mataranyika, Herton Mabongue
Standard Bank × Data School Hackathon 2026

---

## 1. The question, and why it is hard

Syn Bank can see every transaction that flows through Syn Bank. It cannot see the
transactions that flow through its competitors. So the commercially useful
number — *what fraction of this client's banking activity do we hold?* — cannot
be read off the internal data at all. It has to be estimated from outside.

This is the trap the model is built to avoid, and it is worth being explicit
because our own first version fell into it.

### 1.1 The circularity we found and removed

Our initial implementation sized each client's total wallet as
`internal_flow × benchmark_ratio`, then estimated the captured amount as
`total_wallet × capture_ratio`, where `capture_ratio` was a bounded heuristic
over transaction counts and channel counts. Substituting one into the other:

```
share = captured / wallet
      = (wallet × capture_ratio) / wallet
      = capture_ratio
```

The wallet term cancels. Share of wallet was mathematically identical to the
assumed capture rate and could not depend on the data at all. Empirically, across
twenty clients whose estimated wallets differed by a factor of **301×**, the
reported share ran from 18.2% to 20.4% — a spread of two percentage points, with
a standard deviation of 0.006.

A reviewer who tested only that shares fall between 0 and 1 would never catch
this. `tests/test_wallet_engine.py::test_share_varies_across_clients` is the
regression guard we added so it cannot come back.

## 2. The two-sided model

The fix is to compute the two sides of the ratio from **independent sources**.

| Side | Question | Source |
|---|---|---|
| Addressable flow | How much banking activity *should* this client generate? | Published annual financial statements (external) |
| Captured flow | How much did Syn Bank actually see? | Internal transaction datasets (internal) |

```
share = captured_flow / addressable_flow
gap   = addressable_flow − captured_flow
revenue opportunity = gap × pillar fee margin
```

Both sides are annual ZAR **flows**, which makes the ratio meaningful: an
estimated quantity divided by a measured one, not an assumption restated.

### 2.1 Top-down: addressable flow

For each client we take the financial-statement figure that drives each product
pillar, restrict it to the portion addressable by a South African bank, and apply
a sector flow multiple.

| Pillar | Financial-statement signal | Rationale |
|---|---|---|
| Transactional | Revenue | Collections, supplier payments, payroll and treasury sweeps all cross the bank account. Both sides of the working-capital cycle pass through, so annual flow exceeds annual revenue. |
| FX / Cross-border | Revenue × foreign revenue share | Exporters repatriate receipts, importers settle abroad, and intercompany treasury adds a further leg. |
| Trade Finance | Cost of sales + inventory | Documentary instruments (LCs, guarantees, collections) are raised against the physical goods cycle. Only a minority of trade settles under an instrument, so multiples sit well below 1. |

```
addressable_pillar = signal × sa_attribution_share × sector_flow_multiple
```

All multiples live in `config/benchmarks.yaml` with low/base/high bands.

### 2.2 The SA-attribution adjustment

Several clients are global groups. BHP's worldwide revenue is not addressable by
a South African bank. We therefore scale each client's signal by an
`sa_attribution_share` — our estimate of the portion of activity that plausibly
touches a South African banking relationship.

**This is the single most judgmental input in the model.** It ranges from 0.02
(NEPI Rockcastle, Shaftesbury Capital — property portfolios held almost entirely
outside South Africa) to 0.98 (Clicks Group — effectively a domestic-only
retailer). It is held in one column of
`data/external/company_financials.csv` so a reviewer can challenge any single
value without touching the model.

### 2.3 Bottom-up: captured flow

Captured flow is a straight measurement over the **most recent 12 months** of the
internal data, so it is directly comparable to an annual financial-statement
figure:

- Transactional: sum of `amount_zar` in `transactional_banking.csv`
- FX: sum of `value_zar` in `cross_border_payments.csv`
- Trade finance: sum of `value_zar` in `trade_finance.csv`

No assumption enters this side. That is the property that makes the sensitivity
analysis in §4 meaningful.

## 3. Opportunity ranking

Ranking on gap size alone sends bankers at the biggest client every time. The
composite score in `config/scoring_weights.yaml` blends commercial upside with
whether the business is realistically winnable:

| Weight | Feature | Reasoning |
|---|---|---|
| 50% | Gap size | Commercial upside comes first. |
| 20% | Ease of conversion | An existing multi-product relationship converts more cheaply than a cold pillar. |
| 15% | Relationship depth | Number of active product pillars. |
| 15% | Urgency / freshness | 90-day flow acceleration suggests the client is in motion now. |

## 4. Sensitivity to assumptions

Every flow multiple was shifted together and the portfolio re-estimated. The
captured side is invariant by construction — it is measured — so only the
estimate moves.

| Multiplier shift | Addressable (Rbn) | Captured (Rbn) | Portfolio share | Revenue opportunity (Rbn/yr) |
|---:|---:|---:|---:|---:|
| −25% | 2 850 | 191.6 | 6.72% | 6.39 |
| −10% | 3 420 | 191.6 | 5.60% | 7.76 |
| **0%** | **3 800** | **191.6** | **5.04%** | **8.68** |
| +10% | 4 180 | 191.6 | 4.58% | 9.59 |
| +25% | 4 750 | 191.6 | 4.03% | 10.96 |

**Reading:** if every multiple is wrong by a quarter in the same direction,
portfolio share still lands between 4.0% and 6.7%. The headline conclusion —
that Syn Bank holds a low single-digit share and the growth runway is large — is
robust to the assumption set. Client *rankings* are more stable still, because a
uniform shift affects all clients in the same direction.

Reproduce with `models.wallet_engine.sensitivity_analysis`.

## 5. Data sources

**Internal (synthetic, supplied):** `transactional_banking.csv` (2.80m rows),
`cross_border_payments.csv` (241k rows), `trade_finance.csv` (20.3k rows), all
covering 2023-07-01 to 2026-06-30 across 20 client entities.

**External (public):** FY2025 annual results and financial statements for each of
the 20 listed entities. Every figure is cited per client in
`data/external/company_financials.csv` (`source` column). Currency conversion
uses the 2025 average USD/ZAR of 17.8839; EUR and GBP are cross-rates derived
from that anchor and are flagged as approximate.

### 5.1 Treatment of the synthetic-data rules

The brief requires teams to "supplement the supplied internal data with publicly
available external sources", naming annual financial reports and investor
relations pages, and requires that external sources be cited. It separately
prohibits linking the fictional data to any real bank, client or transaction.

We hold both. Public financials are used **only to size an addressable flow
benchmark**. We make no claim that any synthetic transaction corresponds to a
real event, and Syn Bank is treated throughout as the fictional institution it
is. Where the datasets carry the name of a listed entity, we use that entity's
published financials as a scale reference and nothing more.

## 6. Assumptions and limitations

1. **Portfolio size.** The brief describes 50 JSE-listed clients; the supplied
   data contains 20 (E01–E20). We modelled what was supplied and did not
   extrapolate.
2. **Flow multiples are benchmarks, not observations.** They are informed by SARB
   payment-system and banking-fee context but are not client-specific. §4
   quantifies the consequence.
3. **SA attribution is judgmental.** See §2.2. It is the input we would most want
   to replace with disclosed segment data given more time.
4. **One estimated revenue figure.** Sanlam does not disclose a single comparable
   revenue line in its results release; we used an estimate anchored on its
   reported R15.9bn net result from financial services, flagged
   `source_quality = estimated`, and applied a confidence penalty. It should be
   verified against the audited income statement before any external use.
5. **Imputed cost of sales and inventory.** Where not separately disclosed, these
   are imputed from sector gross margins. Imputation is flagged per client
   (`cogs_imputed`, `inventory_imputed`) and lowers confidence.
6. **Gaps are attributed to competitors.** We assume Syn Bank's internal records
   are complete, so unobserved flow sits with another bank. In reality some of it
   is self-funded, netted internally, or does not exist.
7. **Share above 100% is a signal, not a cap.** If captured exceeds addressable,
   the top-down estimate under-sized that client. We flag
   (`share_exceeds_estimate`) rather than silently clipping. No client currently
   trips it.
8. **Lending and DCM are out of scope.** The supplied data covers three pillars;
   debt is captured in the external dataset but not yet modelled as a wallet.
9. **Nominal ZAR.** No inflation adjustment within the hackathon window.
