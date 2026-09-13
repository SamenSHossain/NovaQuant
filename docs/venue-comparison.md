# Kalshi vs Polymarket US — incentive programme comparison

**Last verified: 2026-09-02.** Side-by-side of the two CFTC-regulated venues' liquidity and
market-maker programmes. Full detail and primary sources in
[`kalshi-incentive-programmes.md`](kalshi-incentive-programmes.md) and
[`polymarket-us-incentive-programmes.md`](polymarket-us-incentive-programmes.md).

> Scope: **Kalshi Inc.** (DCM) and **Polymarket US / QCX LLC** (DCM). The offshore CLOB at
> `polymarket.com` (Adventure One QSS) is a different venue with a different program and no
> notice regime — one row at the bottom, not in the body.

---

## 1. Programme roster

| | Kalshi | Polymarket US |
|---|---|---|
| **Open resting-order programme** | Liquidity Incentive Program (LIP) | Market Liquidity Incentive Program (MLIP) |
| **Open volume programme** | Volume Incentive Program (VIP) | Market Volume Incentive Program (MVIP) |
| **MM-only liquidity tier** | Liquidity Provider Program (LPP) — **live**, reverse auction | LPP — **expired 2026-05-22**, no successor filed |
| **Market Maker Program** | **Live**; all terms in Confidential Schedule II | **Expired 2026-05-22** |
| **Net** | Four live programmes, two of them MM-gated | **Two live programmes, both open to everyone** |

The structural headline: **Kalshi still has a sealed market-maker tier; Polymarket US does not.**
Everything currently payable on Polymarket US is available without an agreement.

---

## 2. The resting-order scoring function — the row that matters

Both venues run a per-second snapshot, exponential-decay, pro-rata-share-of-pool model. They
diverge on four points, and each divergence changes optimal quoting.

| Mechanic | Kalshi LIP | Polymarket US MLIP |
|---|---|---|
| **Snapshot cadence** | 1/second, within-second offset drawn randomly on a **periodic** basis | 1/second, "random snapshot" |
| **Decay exponent measured from** | **Reference Price** — the level where *cumulative* depth first reaches `TargetSize / 5` | **Best price** — top of book |
| **Role of Target Size** | Gate **and** walk terminator: depth beyond cumulative `TargetSize` scores **nothing** | **Gate only.** Does not enter the score at all |
| **Two-sided requirement** | **Yes.** Snapshot excluded entirely unless both sides meet Target Size | **No.** Each side normalized independently; a single-sided quoter scores |
| **Illiquidity scaling** | Payout × (non-excluded snapshots ÷ total snapshots) — **new 2026-07-30** | None filed. Headline pool is not scaled down |
| **Normalization** | Per side to 1.0, summed → snapshot worth ≤ **2.0** across all participants | Per side to 1.0, independently |
| **Payout floor** | **$1.00**, rounded down to the cent | **$1.00** |
| **Clawback** | **None** | **None** |

### Formulae

**Kalshi LIP**
```
Score(bid)   = DiscountFactor ^ (ReferencePrice − Price(bid)) × Size(bid)
Payout(user) = TimePeriodScore(user) × TimePeriodReward
             × (non-excluded Snapshots ÷ total Snapshots)
```

**Polymarket US MLIP**
```
Score(order) = DiscountFactor ^ (ticks from best price) × OrderSize
Payout(user) = (user's share of total score) × TimePeriodReward
```

### Practical consequences

1. **Top-of-book leverage is cheap on Polymarket US and expensive on Kalshi.** One small order
   at best price moves the Polymarket reference for everyone. On Kalshi you must accumulate
   `TargetSize / 5` in cumulative depth before the Reference Price is set — a lone top-of-book
   order does nothing.
2. **Kalshi punishes depth past Target Size with zero, not a small number.** The walk stops.
   Polymarket US keeps paying the decayed score.
3. **Kalshi requires a partner.** If nobody quotes the other side to Target Size, your snapshot
   is excluded *and* the period's pool shrinks. Polymarket US pays you alone.
4. **Marginal size that lifts a side over `targetSize` is worth disproportionately more on
   Polymarket US**, because the gate is binary and the size does not otherwise score.

---

## 3. Pool economics — the easiest thing to get wrong

| | Kalshi LIP | Polymarket US MLIP |
|---|---|---|
| **What a pool attaches to** | **One market** | **One programme**, spread across every market in it |
| **Reward cap** | **$1,000 per calendar day, per market** | **None filed** |
| **Reward floor** | **$1** (was $10 until 2026-07-30) | None filed |
| **Observed pool** | `period_reward` 200000 uniformly (≈ **$20**/period, units undocumented) | **$20 – $10,500** per period, 41 distinct values |
| **Observed period** | 15 min (183/200) or 90 min (17/200) | 15 min – full day |
| **Per-market reality** | Pool *is* the per-market figure | `rewardPool ÷ market_count` — e.g. **$4.31** for CFB T1 Spreads Live ($10,500 ÷ 2,434 markets) |

**Polymarket US per-market economics vary ~1,500×** between programmes ($3,333/market for a
3-market golf round vs $2.16/market for a 2,434-market CFB programme). Concentration, not headline
pool, is where the money is. Kalshi has no such trap — one pool, one market.

MM-only tiers, for scale: Kalshi's LPP caps at **$50,000 per week per series**, roughly 50× the
LIP's per-market ceiling. Polymarket US's equivalent is dead.

---

## 4. Parameters — envelope and transparency

| | Kalshi | Polymarket US |
|---|---|---|
| **Filed numeric bounds** | Target Size `>100, <20,000`; Discount ≤1.00; Reward $1–$1,000/day; Period ≤31 days | **None at all.** Envelope entirely open |
| **Observed Target Size** | 300 or 1,000 | **500 – 75,000**, 20 distinct values |
| **Observed Discount Factor** | **0.50 uniformly** (`discount_factor_bps: 5000`) | **0.10 – 0.90**, 10 distinct values |
| **Confidential appendix** | LPP Appx B and MMP Schedule II are **genuinely sealed** | Appx B filed — **but live values published on a public page anyway** |
| **Access** | Real JSON API, unauthenticated: `api.elections.kalshi.com/trade-api/v2/incentive_programs` | **No API.** Scrape of the Next.js flight payload in `/rewards` |
| **Version stamp** | none | `programId` embeds a date (`cfb_t1_spreads_live_20260826`) |

Polymarket US is **more transparent in practice and less bounded in law**. Kalshi is the reverse:
a hard filed envelope you can rely on, with the MM tier fully sealed.

---

## 5. Change control and notice

| What changes | Kalshi | Polymarket US |
|---|---|---|
| **Headline parameters** (reward, discount, target size) | Per market/period, published | **No notice obligation whatsoever** — publication *is* the notice, contemporaneous |
| **Programme terms** | CFTC Reg 40.6(a) self-certification | Prospective only; published to website; filed under Part 40 where required |
| **Programme termination** | "Kalshi may end the Program at any time" | Sole discretion, none stated |
| **Participant status** | CRO may **revoke** for abuse or inconsistency with purpose | Disqualification/exclusion, **sole arbiter of all disputes** |
| **Clawback / recoupment** | **None in any filing** | **None in any filing** |
| **Sunset** | LIP hard sunset **2027-01-01**; VIP 2027-09-01; LPP 2027-12-01 | **No end date** on MLIP |

**Never cache Polymarket US parameters across a period boundary.** A game-day contract can run
three regimes in one day (`early` → `day_of` → `live`), each independently re-parameterized with
no notice.

---

## 6. Volume programmes

| | Kalshi VIP | Polymarket US MVIP |
|---|---|---|
| **Eligibility** | Excludes affiliates, **MM-agreement holders**, IB/FCM non-disclosed customers | Excludes DMM holders, LPP participants, IB/FCM. **Must be direct clearing via API/ISV** |
| **Price band** | Hard-coded **$0.03 – $0.97** | "Between the price levels specified on the website" — discretionary |
| **Per-contract cap** | **$0.005/contract/participant**, explicitly to avoid price distortion | **None** |
| **Multipliers** | none | **Volume Multipliers** during designated windows |
| **Term** | Eligible Term ≤ 31 days | Eligible Term |

Kalshi's $0.005 cap is the binding constraint: 1,000 contracts → max $5 regardless of pool size.
Polymarket US files no analogue, so MVIP scales with volume without a ceiling.

---

## 7. Fees

| | Kalshi | Polymarket US |
|---|---|---|
| **Standard** | `roundup(0.07 × C × P × (1−P))`; **0.035** for index markets | **Maker fee: zero for all participants** |
| **Maker rebate** | In confidential Schedule II | **10 / 15 / 20%** of gross taker fees generated, by prior-month maker notional ($2M / $15M / $50M) |
| **Taker rebate** | — | **10 / 25 / 90%** of taker fees paid, by prior-month taker notional ($500K / $25M / $100M). **Paid weekly** |
| **Tier determinism** | — | Keyed to **prior calendar month** → "rebate levels are deterministic and known at the start of each month" |
| **Onboarding** | — | **Accelerated Tier Placement**: claim a tier with verifiable 30-day volume from another prediction market. **Usable once** |

Polymarket US's 90% taker rebate at $100M+ and its zero maker fee are materially more aggressive
than anything Kalshi discloses publicly — but Kalshi's market-maker fee treatment is sealed, so
this comparison is between a published schedule and an unknown.

---

## 8. Market-maker privileges

| | Kalshi | Polymarket US |
|---|---|---|
| **Programme status** | **Live** | **Expired 2026-05-22** |
| **Obligations (public)** | Continuous two-sided quotes, max spread, min size — **values sealed** | Categories only, programme now dead |
| **Availability standard** | **98% of each 1h increment**, ~90 covered series | Min uptime (expired LPP) |
| **Non-cash benefits** | **Cancel-on-disconnect**, **greater throughput**, explicitly acknowledged to "give market makers a trading advantage" | none live |
| **Position treatment** | Accountability Levels **10×** non-MM; Rule 5.15 **Position Limits do not apply** | — |
| **Termination** | "may be suspended, terminated or restricted by Kalshi **at any time and for any reason**" | — |
| **Opt-out** | On any change to a Covered Product's Liquidity Conditions, MM may **opt out of that product without penalty** | LPP had **≥7 days' notice**; immediate for gaming |

Kalshi's 10× position accountability and Rule 5.15 exemption are the most valuable non-cash terms
on either venue, and are the strongest reason to pursue an MM agreement independent of rebates.

---

## 9. Absent on both venues

Three things asked for routinely that **exist in no filing at either venue**:

- **Tiering within a liquidity programme.** Both are flat pro-rata share-of-pool with a floor.
  (Polymarket US tiers *fees*, not incentives.)
- **Top-N / ranked structure.** Neither ranks participants; both normalize continuously.
- **Clawback / recoupment / reversal.** Every remedy at both venues is forward-looking.

---

## 10. The other Polymarket — for contrast only

`polymarket.com` (Adventure One QSS, offshore) runs an unrelated program:
`S(v,s) = ((v−s)/v)² × b`, scaling factor **c = 3.0**, two-sided required when midpoint is outside
[0.10, 0.90]. **15,976 reward-enabled markets, ~148,425 USDC/day**, paid daily ~midnight UTC in
USDC.e on Polygon. Real JSON API, **no notice regime at all** — the mirror image of the tradeoff
above. Fields do **not** map onto Polymarket US.

---

## Open questions

1. **Kalshi `period_reward` units are undocumented.** 200000 as cents = $2,000 would breach the
   $1,000/day cap, so it is almost certainly fixed-point 1e-4 USD = **$20.00**. Verify against a
   paid credit before wiring into any P&L model.
2. **Kalshi LIP eligibility.** The 2026-07-30 clean text **deleted** the exclusions for affiliates
   and MM-agreement holders; the help centre is **stale** and still lists MMs as ineligible.
3. **Kalshi Reference Price behaviour above the reference.** Filed algebra gives `0.50^−2 = 4×`
   for bids inside the Reference Price; the help centre says full credit is capped at 1.0×.
   **Unresolved** — verify against actual paid credits.
4. **Polymarket US successor filings.** Nothing replaced the LPP or MMP after 2026-05-22 as of
   2026-09-02.
5. **Polymarket US period taxonomy.** `daily`, `daily_event`, `tournament_with_cutoff` appear in
   the API but in **no filing and no doc**. Filing and docs also disagree on the Pre-Event boundary
   (day-before vs 6-hours).
