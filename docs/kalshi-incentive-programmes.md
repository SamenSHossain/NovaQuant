# Kalshi incentive & market-maker programmes — reference

**Last verified: 2026-09-02.** Compiled from CFTC self-certification filings, Kalshi
Exchange Notices, the DCM Rulebook, and the public Trade API. Primary PDFs are cached in
[`docs/sources/`](sources/).

Side-by-side against Polymarket US: [`venue-comparison.md`](venue-comparison.md).

There is no single "Kalshi market-maker programme." There are four, and which one you fall
under determines both what you can earn and what you are allowed to know.

| Programme | Who is eligible | Terms public? | Ceiling |
|---|---|---|---|
| Liquidity Incentive (LIP) | All members except IB/FCM and their customers | **Fully public** — exact scoring algebra is filed | $1,000/day/market |
| Volume Incentive (VIP) | All except affiliates, MM-agreement holders, IB/FCM | Fully public | $0.005/contract/participant |
| Liquidity Provider (LPP) | **Market Maker Agreement holders only** | Envelope public; values in Confidential Appx B | $50,000/week/series |
| Market Maker Program | **Market Maker Agreement holders only** | Obligation *categories* only; values in Confidential Schedule II | Undisclosed |

Three things that are commonly assumed to exist **do not appear in any public Kalshi
document**:

- **Tiering** — every public programme is flat pro-rata share-of-pool with a payout floor.
- **Top-N structure** — no ranked or capped participant count in the scoring.
- **Clawback** — no filing contains a recoupment, reversal, or offset clause. The only
  remedy is forward-looking revocation by the Chief Regulatory Officer.

---

## 1. Liquidity Incentive Program (LIP)

Governing text: Appendix A to the **July 15, 2026** amendment, as modified **July 30, 2026**
(clean version). Sources: [LIP-2026-07-30-modification.pdf](sources/LIP-2026-07-30-modification.pdf),
[LIP-2026-07-15-update.pdf](sources/LIP-2026-07-15-update.pdf),
[LIP-2026-02-11-amendment.pdf](sources/LIP-2026-02-11-amendment.pdf).

### Scope, duration, eligibility

- Applies to **all Kalshi markets**.
- Runs until the earlier of **January 1, 2027** or the date Kalshi amends or terminates it.
  (The February 2026 text said September 1, 2026; July 15 extended it.)
- Eligible Participants = **all Kalshi members except Introducing Brokers, Futures
  Commission Merchants, and customers thereof when transacting via the IB or FCM.**

> **Eligibility changed on 2026-07-30 and the help centre is stale.** The clean July 30 text
> deleted the exclusions for (i) affiliates of Kalshi and (ii) members who have executed a
> Market Maker Agreement. The cover letter's stated purpose is to "make the program more
> uniformly available to market participants." Kalshi's help-centre article still lists
> market makers as ineligible. Confirm with Kalshi before acting on this.

### Parameter envelope (per market, per Time Period)

| Variable | Bound |
|---|---|
| Time Period | ≤ 31 days; periods may overlap; must start and end on a whole second |
| Target Size | > 100 and < 20,000 contracts |
| Discount Factor | ≤ 1.00 |
| Time Period Reward | ≥ **$1.00** and ≤ **$1,000 per calendar day** in the period, applied **per market** |

The Time Period Reward floor was **$10** until July 30, 2026.

### Sampling cadence

One Snapshot of the book **per second**. The exact within-second offset is drawn from a
random uniform distribution **on a periodic basis** — the February 11, 2026 amendment
explicitly removed the requirement to redraw per snapshot, "to conserve exchange resources,
while continuing to meet the purpose of that mechanism (to ensure that the exact snapshot
times will be nonpublic, fairly and randomly chosen, and changed on a periodic basis)."

A Snapshot is **excluded** if:

- the market is not open for trading, or
- there is not two-sided liquidity — resting orders meeting Target Size on **both** the yes
  and no sides.

### Qualifying orders — the "qualifying spread" analogue

There is **no fixed spread band**. Qualification is a per-side, per-snapshot depth walk.
A yes ask counts as a no bid.

```
QualifyingBids      := ∅
QualifyingTotalSize := 0
ReferencePrice      := unset
currentPrice        := highest bid price on this side

loop:
    QualifyingTotalSize += size available at currentPrice
    QualifyingBids      += all bids at currentPrice

    if ReferencePrice is unset and QualifyingTotalSize >= TargetSize / 5:
        ReferencePrice := currentPrice

    if QualifyingTotalSize >= TargetSize:
        stop                       # this side qualifies

    currentPrice := next highest bid price
    if none exists:
        QualifyingBids := ∅        # side does not qualify at all
        stop
```

Consequences that matter for a quoting model:

- The Reference Price is the level at which **cumulative** depth first reaches **one fifth
  of Target Size**. A lone small order at the top of the book does **not** set it.
- Depth resting below the level where cumulative size reaches Target Size earns **nothing**.
- The July 30 text also **dropped** the February 2026 condition that the highest bid be
  strictly less than the highest possible price.

### Payout formula

```
Score(bid)            = DiscountFactor ^ (ReferencePrice − Price(bid)) × Size(bid)
                        # exponent N = number of ticks between ReferencePrice and the bid

NormalizedScore(bid)  = Score(bid) ÷ Σ_{b ∈ bids on that side} Score(b)

SnapshotScore(user)   = Σ NormalizedQualifyingYesScore(yes bids of user)
                      + Σ NormalizedQualifyingNoScore(no bids of user)
                        # one snapshot is worth at most 2.0 across ALL participants

TimePeriodScore(user) = Σ_snapshots SnapshotScore(user)
                      ÷ Σ_snapshots Σ_users SnapshotScore(u)

Payout(user)          = TimePeriodScore(user)
                      × TimePeriodReward
                      × (non-excluded Snapshots ÷ total Snapshots)
```

Paid only if the result is **≥ $1.00**, **rounded down to the nearest cent**. Anything below
$1.00 is not paid.

> **Unresolved discrepancy — bids priced better than the Reference Price.** In the filed
> formula the exponent `ReferencePrice − Price(bid)` goes **negative** for a bid inside the
> Reference Price, so at a 0.50 Discount Factor a bid two ticks better scores **4×**, not 1×.
> Kalshi's help centre instead states that orders "priced at or better than the Reference
> Price get full credit (1.0x multiplier)." The filing governs, but the two disagree and the
> gap is large. Resolve it before sizing quotes inside the reference level.

The `× non-excluded/total` scaling factor is **new in the July 30, 2026 version** — the
February 2026 text had no such term. A market that loses two-sided depth for part of a
period now pays out proportionally less than its headline pool.

Kalshi's worked example: a $100 reward over 10,000 snapshots, of which 8,000 are
non-excluded; a 20% share gives `20% × $100 × 0.8 = $16.00`.

### Live parameters

Unauthenticated, no API key required:

```
GET https://api.elections.kalshi.com/trade-api/v2/incentive_programs?limit=200
```

Returns `{discount_factor_bps, target_size_fp, period_reward, start_date, end_date,
market_id, market_ticker, incentive_type, incentive_description, paid_out, id}`.

200-row sample taken 2026-09-02, all `incentive_type: liquidity`,
`incentive_description: series_lip`:

| Field | Observed |
|---|---|
| `discount_factor_bps` | 5000 (= 0.50) uniformly — a 2× score penalty per tick away from the Reference Price |
| `target_size_fp` | 300 (108/200) or 1000 (92/200) contracts — so the Reference Price is set at 60 or 200 cumulative contracts |
| `period_reward` | 200000 uniformly |
| `end_date` − `start_date` | 15 minutes (183/200) or 90 minutes (17/200) |

**`period_reward` units are undocumented.** Read as cents, 200000 would be $2,000 and would
breach the $1,000/day/market cap, so it is almost certainly fixed-point 1e-4 USD =
**$20.00** per period. Verify against an actual paid credit before wiring this into a P&L
model.

### Monitoring, suspension, clawback

- Kalshi monitors trading activity and participants' performance and "shall retain the right
  to **revoke participant status** if Kalshi's **Chief Regulatory Officer** concludes from
  review that a participant's participation in the program is abusive or in any way
  inconsistent with the purpose of the Program."
- "Kalshi may end the Program at any time."
- **No clawback, recoupment, or reversal clause.** Revocation is forward-looking only.
- A verified SSN must be on file to receive reward credits above annual IRS reporting
  thresholds; that threshold is shared with referral credits.

---

## 2. Liquidity Provider Program (LPP) — market-maker-only tier

Governing text: **May 4, 2026** filing, Appendix A, as amended June 11 and **June 18, 2026**.
Effective on or after May 18, 2026; runs until the earlier of **December 1, 2027** or
termination. Sources: [LPP-2026-05-04-filing.pdf](sources/LPP-2026-05-04-filing.pdf),
[LPP-2026-06-18-amendment.pdf](sources/LPP-2026-06-18-amendment.pdf).

- **Eligibility: only Kalshi members who have executed a Market Maker Agreement.**
- Kalshi designates **Incentivized Series** and **Incentive Periods**. Series are drawn from:
  Weather, Commodities, Crypto, Economics, Culture, Financials, Politics, Mentions,
  **Sports** (added by the June 18, 2026 amendment, effective July 6, 2026), and Science and
  Technology.
- **Pool cap: "The Incentive Period Reward for any Incentivized Series shall not exceed
  $50,000 USD per week."** Applied per week, including each partial week, for longer periods.
  Roughly 50× the LIP's per-market daily ceiling, on a per-series basis.
- **Incentive Period Requirements** — the categories are published, the values are not:
  - Maximum Spread (on the Designated Liquidity Provider's resting orders)
  - Minimum Size within Spread
  - Minimum Uptime
  - Market Coverage (all markets in the series unless otherwise specified)
- **Selection is a reverse auction.** Providers submit the minimum amount they are willing to
  receive as the Incentive Period Reward. Kalshi "may consider factors including, but not
  limited to, current liquidity conditions and the total number of Designated Liquidity
  Providers." The procedure is **Confidential Appendix B**. Auctions run periodically;
  contact `marketmaker@kalshi.com`.
- **Public disclosure obligation is deliberately narrow:** only the identity of the series
  and the period dates must be posted before the period begins — not the spread, the size,
  the uptime, or the reward.
- **Suspension:** the CRO may revoke DLP status in a particular series for conduct that is
  abusive or inconsistent with the Program, the Rulebook, or applicable law. Kalshi may end
  the Program or any component at any time. **No clawback.**

### Active programmes (per Kalshi help centre; all terminate 2026-12-31)

Two providers: **WTI** (KXWTI, KXWTIW); **Crypto 15-minute** markets.

One provider each: Truth (KXTRUTHSOCIAL); Primary Daily & Weekly Commodities (BRENT, CORN,
GOLD, SILVER, COPPER); Crypto Hourly & Daily; Hourly Commodities (KXWTIH, KXGOLDH,
KXSILVERH); Rotten Tomatoes; Weekly Trump (KXAPRPOTUS, TRUMPACT); Election Primary Voting
(KXVOTEPRIMARY, KXPRIMARYTURNOUT); Election Margin of Victory (KXMIDTERMMOV); Album
Equivalents (KXALBUMEQUIV); Hourly Weather; Hourly Commodities; Commodities 15-minute;
Baseball (KXMLBF5/F3/F7 families, KXMLBTB, KXMLBHRR, KXMLBHR, KXMLBHIT, KXMLBTEAMTOTAL,
KXMLBRBI, KXMLBEXTRAS, KXMLBRFI); Golf (KXPGAROUNDSCORE, KXPGATOP5/10/20/40, KXPGAMAKECUT,
KXDPWORLDTOURMAKECUT, KXPGAH2H, KXLIVH2H, KXDPWTH2H, KXPGA3BALL); Tennis (KXATPGTOTAL,
KXWTAGTOTAL, KXATPSETWINNER, KXWTASETWINNER); Diesel (KXDIESELD, KXDIESELW, KXDIESELMON);
Hourly Temp (KXTEMPMIAH); Daily Rain (KXRAIN); AI Share (KXANTHSHARE, KXBABASHARE,
KXDEEPSHARE, KXGOOGSHARE, KXOPENSHARE, KXSTEALTHSHARE, KXTENCENTSHARE, KXXIAOMISHARE); Gas
Daily & Weekly (KXAAAGASD, KXAAAGASW); Primary Commodities Daily & Weekly (KXBRENTD/W,
KXNATGASD/W, KXSILVERD/W, KXCOPPERD/W); Alternate Indices (KXIBOV, KXRUT, KXTSX, KXNIKKEI,
KXME, KXKOSPI, KXFTSE, KXCAC40).

---

## 3. Market Maker Program — Rulebook Chapter 4 and Schedule II

Governing text: **February 26, 2024** filing, Appendix A ("Initial Market Maker Program"),
effective March 11, 2024 through March 11, 2026 unless extended. Superseded in practice by
the **"2025 Market Maker Program,"** whose Schedule II is amended periodically — amendments
filed August 30, 2025 and June 3, 2026. Sources:
[MMP-2024-02-26-filing-and-rulebook.pdf](sources/MMP-2024-02-26-filing-and-rulebook.pdf),
[MMP-2025-08-30-schedule-II-amendment.pdf](sources/MMP-2025-08-30-schedule-II-amendment.pdf),
[MMP-2026-06-03-schedule-II-amendment.pdf](sources/MMP-2026-06-03-schedule-II-amendment.pdf).

The entire public statement of obligations and incentives is this:

> **Liquidity Conditions.** In designated contracts during specified hours Program
> participants must:
> - quote predetermined continuous two-sided markets
> - maintain maximum bid/offer spreads
> - maintain minimum quote sizes
>
> **Incentives for adhering to the Liquidity Conditions.** Predetermined incentives will be
> available upon satisfying all Program obligations as determined by the Exchange.

**Every spread, size, uptime, and payment figure is in Confidential Schedule II**, filed
with a FOIA confidential-treatment request. The June 3, 2026 amendment added tailored
liquidity conditions and benefits for **Perpetual Futures Contracts** on a time-limited
basis — also confidential.

### What is public

- **Excluded from incentives:** intra-firm trading by direct or indirect means, even where
  otherwise permitted by the Kalshi Rules; and any trading prohibited by the Kalshi Rules,
  Commission Regulations, or CFTC Regulations.
- **Schedule II governance:** it is consistent for all participants in the programme; Kalshi
  must give notice of any amendment to all participants; and on any change to the Liquidity
  Conditions for a Covered Product, a Market Maker may **opt out of that Covered Product
  without penalty** by written notice. Amendments may be treated as retroactive to the
  self-certification filing date, but no payments are made before acceptance.
- **Availability standard** (Exchange Notices): **"98% of each 1h increment"**, historically
  within 8:00 a.m. – 5:00 p.m. ET, with product carve-outs — FX pairs "except last 10m",
  BTC/ETH "until 4pm". The current covered-product list runs to roughly 90 series:
  KXINX/KXINXU/KXINXY, KXNASDAQ100 family, KXBTC/KXBTCD/KXBTCMAX150, KXETH/KXETHD, KXDOGE,
  KXSHIBA, NBA/NHL/NFL/MLB/NCAA, EPL/UCL/Serie A/Bundesliga/La Liga/Ligue 1, KXCPI/KXCPIYOY,
  KXFED/KXFEDDECISION/KXRATECUTCOUNT, KXGDP, KXPAYROLLS, KXU3, tennis majors, KXNASCARRACE,
  KXUFCFIGHT, KXHEISMAN, KXIPO, KXLLM1. The list is explicitly subject to change.
- **Benefits**, per the Membership Agreement text added March 11, 2024
  ([notice](sources/MMP-2024-03-11-membership-agreement-notice.pdf)): "discounts on fees,
  rebates on fees, revenue share from fees, and other monetary benefits"; plus
  **cancel-on-disconnect order protections** and **greater throughput to the Exchange** —
  with an explicit acknowledgement that market makers "may be able to price their quotes in
  ways that are materially different from other Kalshi members" and that these tools "may
  give market makers a trading advantage over members who are not market makers."

### Rulebook Chapter 4 (DCM Rulebook v1.29)

Source: [Kalshi-DCM-Rulebook-v1.29.pdf](sources/Kalshi-DCM-Rulebook-v1.29.pdf), Chapter 4.

- **4.1 Eligibility.** Only Members in good standing. Kalshi has **sole discretion**. A market
  maker agreement must be completed and filed. **"The designation of any Market Maker may be
  suspended, terminated or restricted by Kalshi at any time and for any reason."** Multiple
  market makers and multiple concurrent programmes are permitted.
- **4.2 Designation.** Kalshi considers available financial resources, relevant experience,
  business reputation, and any other relevant factor. No designation without the Member's
  consent. Kalshi may periodically evaluate performance standards — quality of the markets,
  competitive market making, observance of ethical standards, administrative soundness — and
  on failure may suspend, terminate, or restrict the designation.
- **4.3 Benefits.** May include financial benefits, reduced fees, **differing Position Limits
  and Position Accountability Levels**, and enhanced access.
- **4.4 Obligations.** Transactions must be reasonably calculated to contribute to the
  maintenance of a fair and orderly market. Obligations "include but are not limited to
  maintaining two-sided markets within a defined spread and with a minimum depth during
  trading."
- **4.5 Position accountability.** On contracts where the Market Maker has quoting
  obligations, Position Accountability Levels are **10× the non-market-maker levels** unless
  otherwise specified, and **Rule 5.15 Position Limits do not apply** to those contracts
  (accountability applies instead). CFTC limits always bind.

---

## 4. Volume Incentive Program (VIP) — for contrast

Governing text: August 2025 VIP as updated **August 18, 2026**. Runs until the earlier of
**September 1, 2027** or termination. Source:
[VIP-2026-08-18-update.pdf](sources/VIP-2026-08-18-update.pdf).

- Excludes affiliates of Kalshi, **members who have executed a Market Maker Agreement**, and
  IBs/FCMs and their **non-disclosed** customers.
- Fixed per-market **Volume Reward** over an **Eligible Term ≤ 31 days**, split **pro rata by
  Eligible Volume**.
- **Eligible Volume** = trades on the central limit order book at prices **between $0.03 and
  $0.97**. The price band does **not** apply to perpetual futures. Eligible volume may be
  limited to taker-side or maker-side only, provided the limit is disclosed on the market page.
- **Hard cap: $0.005 per contract traded, per participant** — stated as being "to help avoid
  price distortion caused by these Volume Incentives." 1,000 contracts → at most $5,
  regardless of pool size or other participants' activity.
- Same CRO revocation clause. **No clawback.**

Standard exchange fee formula for reference: `fees = roundup(0.07 × C × P × (1−P))`, reduced
to a `0.035` coefficient for index markets.

---

## Keeping this current

1. **Live parameter check** — confirm the envelope above still brackets live values:

   ```sh
   curl -s 'https://api.elections.kalshi.com/trade-api/v2/incentive_programs?limit=200' \
     | python3 -c 'import json,sys,collections;r=json.load(sys.stdin)["incentive_programs"];\
   print(collections.Counter((x["discount_factor_bps"],x["target_size_fp"],x["period_reward"]) for x in r))'
   ```

   Expect `discount_factor_bps ≤ 10000` and `100 < target_size_fp < 20000`.

2. **New filings** — Kalshi's public docs bucket is listable and is the fastest way to detect
   a new amendment. `kalshi.com/regulatory/notices` itself sits behind a Vercel JS challenge
   and is not scrapable.

   ```sh
   curl -s 'https://kalshi-public-docs.s3.amazonaws.com/?list-type=2&prefix=regulatory/notices/&max-keys=1000' \
     | grep -oE '<Key>[^<]*</Key>' | sed 's/<[^>]*>//g' \
     | grep -iE 'market maker|liquidity|incentive'
   ```

   The bucket paginates via `<NextContinuationToken>`; 488 keys under this prefix as of
   2026-09-02.

3. **Open question** — resolve the `period_reward` unit with Kalshi support or against a
   paid credit before relying on it quantitatively.

## Source index

| File | Date | What it establishes |
|---|---|---|
| [LIP-2026-07-30-modification.pdf](sources/LIP-2026-07-30-modification.pdf) | 2026-07-30 | Current LIP terms (clean + tracked): $1 floor, snapshot-ratio scaling, eligibility change |
| [LIP-2026-07-15-update.pdf](sources/LIP-2026-07-15-update.pdf) | 2026-07-15 | Extension to 2027-01-01; stated purpose of the changes |
| [LIP-2026-02-11-amendment.pdf](sources/LIP-2026-02-11-amendment.pdf) | 2026-02-11 | Prior LIP text; two-sided exclusion; periodic snapshot-time redraw |
| [LPP-2026-05-04-filing.pdf](sources/LPP-2026-05-04-filing.pdf) | 2026-05-04 | LPP creation: $50k/week/series cap, requirement categories, Confidential Appx B |
| [LPP-2026-06-18-amendment.pdf](sources/LPP-2026-06-18-amendment.pdf) | 2026-06-18 | Sports added to eligible series categories |
| [MMP-2024-02-26-filing-and-rulebook.pdf](sources/MMP-2024-02-26-filing-and-rulebook.pdf) | 2024-02-26 | Initial MM Program Appendix A; Rulebook Chapter 4 introduction |
| [MMP-2024-03-11-membership-agreement-notice.pdf](sources/MMP-2024-03-11-membership-agreement-notice.pdf) | 2024-03-11 | Disclosed MM benefits: fee rebates, revenue share, cancel-on-disconnect, throughput |
| [MMP-2024-08-16-liquidity-conditions-notice.pdf](sources/MMP-2024-08-16-liquidity-conditions-notice.pdf) | 2024-08-16 | Covered-product format and the 98%-of-each-1h-increment standard |
| [MMP-2025-08-30-schedule-II-amendment.pdf](sources/MMP-2025-08-30-schedule-II-amendment.pdf) | 2025-08-30 | Schedule II governance; opt-out-without-penalty; confidentiality |
| [MMP-2026-06-03-schedule-II-amendment.pdf](sources/MMP-2026-06-03-schedule-II-amendment.pdf) | 2026-06-03 | Perpetual-futures liquidity conditions added, confidential |
| [VIP-2026-08-18-update.pdf](sources/VIP-2026-08-18-update.pdf) | 2026-08-18 | Current VIP: $0.005/contract cap, $0.03–$0.97 band, 2027-09-01 end |
| [Kalshi-DCM-Rulebook-v1.29.pdf](sources/Kalshi-DCM-Rulebook-v1.29.pdf) | current | Chapter 4 Rules 4.1–4.5 |

Kalshi help-centre articles used for the active-programme lists and product tables:
`help.kalshi.com/en/articles/` — 13823851 (LIP), 13823850 (VIP), 15410219 (LPP), 13823819
(market makers), 16076644 (where to find programmes in the product).
