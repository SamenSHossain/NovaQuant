# Polymarket US incentive & market-maker programmes — reference

**Last verified: 2026-09-02.** Compiled from CFTC self-certification filings, Polymarket US
Exchange Notices, the DCM Rulebook, the public docs site, and a by-hand pull of the live
schedule. Primary PDFs are cached in [`docs/sources-polymarket-us/`](sources-polymarket-us/).

Side-by-side against Kalshi: [`venue-comparison.md`](venue-comparison.md).

This is the companion to [`kalshi-incentive-programmes.md`](kalshi-incentive-programmes.md) and
deliberately follows the same shape. **Polymarket US (QCX LLC) is a CFTC-registered DCM, not the
offshore CLOB.** Everything here is filed under CFTC Regulation 40.6(a), so the change-and-notice
regime is a legal one rather than a product decision — see [§5](#5-what-can-change-and-on-what-notice).

> **Do not confuse this venue with polymarket.com.** The offshore CLOB runs an entirely different
> program keyed on `min_size` / `max_spread` / `rewards_daily_rate` (`clob.polymarket.com/sampling-markets`).
> The fields are **not** interchangeable with the ones below. One footnote in [§6](#6-the-other-polymarket).

Of the programmes filed since Aug 2025, **two are live**:

| Programme | Who is eligible | Terms public? | Ceiling |
|---|---|---|---|
| Market Liquidity Incentive (MLIP) | **All** Participants in good standing, auto-enrolled | Envelope public; values in Confidential Appx B — **but live values published weekly** | None stated |
| Market Volume Incentive (MVIP) | All except DMM-agreement holders, LPP participants, IB/FCM | Envelope public; values in Confidential Appx B | None stated |
| ~~Liquidity Provider (LPP)~~ | Application + approval, MM-agreement holders excluded | Envelope public; values confidential | **Expired 2026-05-22** |
| ~~Market Maker Program~~ | Approval only | Obligation categories only | **Expired 2026-05-22** |

Three things worth stating up front, because they differ from Kalshi:

- **There is no confidential-appendix blackout on the live numbers.** Kalshi's LPP hides Target
  Size and reward behind Confidential Appendix B. Polymarket US files an Appendix B too, but then
  **publishes the actual per-programme parameters on a public page**, refreshed continuously. You
  can read today's `discountFactor` and `targetSize` for all 144 programmes without an agreement.
- **No two-sided requirement to earn.** Kalshi's LIP excludes any snapshot lacking two-sided depth
  meeting Target Size. Polymarket US normalizes **each side independently**, so a single-sided
  quoter can score, provided Target Size is met on that side.
- **No clawback**, same as Kalshi. Remedies are forward-looking: disqualification, exclusion,
  revocation. No recoupment or reversal clause appears in any filing.

---

## 1. Market Liquidity Incentive Program (MLIP) — the live resting-order programme

Governing text: **Amended Market Liquidity Incentive Program**, self-certified **April 7, 2026**.
Lineage: Standing Order Liquidity Incentive Program (2025-11-25, effective 2025-12-12) → Amended
Standing Order Incentive Program (2026-03-03) → renamed Market Liquidity Incentive Program
(2026-03-17) → current amendment (2026-04-07). Sources:
[MLIP-2026-04-07-amended.pdf](sources-polymarket-us/MLIP-2026-04-07-amended.pdf),
[MLIP-2026-03-17.pdf](sources-polymarket-us/MLIP-2026-03-17.pdf),
[SOIP-2026-03-03-amended.pdf](sources-polymarket-us/SOIP-2026-03-03-amended.pdf),
[SOIP-2025-11-25-original.pdf](sources-polymarket-us/SOIP-2025-11-25-original.pdf).

### Scope, duration, eligibility

- Adopted under **Rulebook 3.15 (Incentive Programs)** — renumbered from 3.11 between the March
  and May 2026 filings; older filings cite 3.11.
- Runs from 10 business days after certification **"through the date on which Polymarket US
  determines to modify, extend, or terminate the program."** No end date — unlike Kalshi's LIP,
  which carries a hard 2027-01-01 sunset.
- Eligible Participants = **all Participants in good standing**, plus "any other eligibility
  criteria as Polymarket US may implement in its sole discretion, provided such eligibility
  criteria shall be posted publicly." **No limit** on participant count, and **all Eligible
  Participants are automatically enrolled for each Time Period** — there is nothing to opt into.
- The MLIP filing states **no** exclusion for market makers or IB/FCM. (MVIP does exclude them;
  see §2. The asymmetry appears deliberate.)

### Parameter envelope (per programme, per Time Period)

Unlike Kalshi's LIP, the filings state **no numeric bounds at all** — no Target Size floor or cap,
no Discount Factor ceiling, no reward floor or per-day cap. The envelope is entirely open and the
only constraint on values is what gets published. Observed live bounds are in §1.5.

| Variable | Filed bound | Observed 2026-09-02 |
|---|---|---|
| Time Period | Named types only, no length cap | 15 min – full day |
| `targetSize` | none | 500 – 75,000 contracts |
| `discountFactor` | none | 0.10 – 0.90 |
| `rewardPool` | none | $20 – $10,500 per period |

**Time Period definitions.** The filing and the docs site disagree, and the filing governs:

| Type | Filing (2026-04-07) | Docs site |
|---|---|---|
| Pre-Event | "from Contract listing through the day before the relevant event" | "from market listing until **6 hours** before the event" |
| Event-Day Pre-Event | "from the start of the event day through the start of the event" | "from **6 hours** before until the event starts" |
| Mid-Event | "from the start of the event through settlement" | "from event start until settlement" |

The API surfaces these as `period`: `early`, `day_of`, `live`, plus `daily`, `daily_event`, and
`tournament_with_cutoff` — **three period values that appear in no filing and in no doc.** Treat
the 6-hour figure as unverified.

### Sampling cadence

**"Every second, a random snapshot of the order book is taken."** Each snapshot is equally
weighted regardless of liquidity. The filing says only "periodic snapshots" — the per-second
figure comes from the docs site.

Kalshi contrast: Kalshi also samples once per second but draws the within-second offset randomly
and *excludes* snapshots without two-sided depth. Polymarket US publishes no exclusion rule, so
its headline pool is not scaled down by illiquid snapshots the way Kalshi's is.

### Qualifying orders and payout

```
Score(order)     = DiscountFactor ^ (ticks from best price) × OrderSize

# Each side normalized independently to 1.0 per snapshot, provided
# TargetSize is met on that side. A side that misses TargetSize scores nothing.

Payout(user)     = (user's share of total score) × TimePeriodReward
```

Paid only if the result is **≥ $1.00**; "Rewards under $1.00 are not paid out."

Two structural points that matter for a quoting model:

- **The exponent is ticks from the *best price*, not from a depth-derived reference price.** This
  is the sharpest divergence from Kalshi, whose Reference Price is the level where cumulative
  depth first reaches `TargetSize / 5`. On Polymarket US a single small order at top-of-book
  *does* set the reference for everyone. Cheaper to influence, and cheaper to be displaced from.
- **`targetSize` is a gate, not a scoring input.** It does not appear in the score. It only
  determines whether the side pays at all, so being the marginal size that lifts a side over
  `targetSize` is worth far more than the same size added above the threshold.

**A programme is not a market.** `rewardPool`, `discountFactor` and `targetSize` are set **per
programme per time period and apply to every market in it — they are not summed across markets.**
`CFB T1 Spreads Live` spreads one $10,500 pool across **2,434 markets**. Per-market economics are
`rewardPool / market_count`, which for that programme is **$4.31**. This is the single easiest
number to get wrong here, and it is wrong by three orders of magnitude.

### Live parameters

No JSON API. `gamma-api` / `clob` / `data-api.polymarket.us` do not resolve; `api.polymarket.us`
resolves but is **401**-gated and undocumented. Parameters exist only in the Next.js flight payload
embedded in the `/rewards` HTML, so the pull is a scrape:

```sh
python3 scripts/pull_polymarket_us_rewards.py
```

Returns, verbatim field names: `{programId, name, subcategories, period, rewardPool,
discountFactor, targetSize, symbols[]}`.

Full pull taken 2026-09-02 — **144 programmes, $176,620 total per time period, 86,591
programme-market pairs.** Snapshot: [`data/polymarket_us_rewards_2026-09-02.json`](../data/polymarket_us_rewards_2026-09-02.json).

| Field | Observed |
|---|---|
| `discountFactor` | 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.9 — 0.9 is near-flat (golf/tennis, thin books); 0.10–0.15 concentrates hard at top-of-book (CFB) |
| `targetSize` | 500 … 75,000 contracts, 20 distinct values |
| `rewardPool` | $20 … $10,500 per period, 41 distinct values |
| `period` | `live` (50), `day_of` (41), `daily_event` (28), `early` (19), `tournament_with_cutoff` (4), `daily` (2) |

Largest programmes:

| name | period | rewardPool | discountFactor | targetSize | markets | $/market |
|---|---|---:|---:|---:|---:|---:|
| CFB T1 Spreads Live | `live` | 10,500 | 0.15 | 75,000 | 2,434 | 4.31 |
| Lpga Tour Round 4 | `tournament_with_cutoff` | 10,000 | 0.30 | 10,000 | 3 | 3,333 |
| PGA Round 4 | `tournament_with_cutoff` | 10,000 | 0.35 | 10,000 | 3 | 3,333 |
| UFC Main Moneyline Live | `live` | 10,000 | 0.30 | 20,000 | 482 | 20.75 |
| CFB T1 Totals Live | `live` | 8,250 | 0.15 | 30,000 | 1,579 | 5.22 |
| CFB T1 Spreads DAY OF | `day_of` | 5,250 | 0.15 | 22,500 | 2,434 | 2.16 |
| PGA Pretournament | `tournament_with_cutoff` | 5,000 | 0.90 | 10,000 | 3 | 1,667 |

The `$/market` spread is roughly **1,500×** between the golf and CFB programmes. Concentration,
not headline pool size, is where the economics live.

`programId` embeds a date (`cfb_t1_spreads_live_20260826`), which is the closest thing to a
version stamp on a parameter set. A changed `programId` for the same `name` is a re-parameterization.

### Monitoring, suspension, clawback

- The Exchange's **Control Desk**, with the **National Futures Association (NFA)** as Regulatory
  Service Provider, "actively monitors for trading abuses." **"Trading activity that violates the
  Exchange Rulebook will be disqualified from awards under the Program."**
- Polymarket US "reserves the right to cancel or withdraw the Program if it suspects abuse, fraud,
  or violations of applicable law," participants subject to compliance review.
- Non-compliant Participants "may, in Polymarket US' sole discretion, be excluded from
  eligibility, or have their participation in the Program removed."
- **Polymarket US is "the sole arbiter of the Program, and any dispute will be resolved by
  Polymarket US in its sole discretion."**
- **No clawback, recoupment, or reversal clause** in any filing reviewed.

---

## 2. Market Volume Incentive Program (MVIP) — for contrast

Governing text: **Amended Market Volume Incentive Program**, self-certified **April 7, 2026**;
originally Market Incentive Program (2026-03-05, effective 2026-03-19). Sources:
[MVIP-2026-04-07-amended.pdf](sources-polymarket-us/MVIP-2026-04-07-amended.pdf),
[MIP-2026-03-05.pdf](sources-polymarket-us/MIP-2026-03-05.pdf).

- Volume-based, not resting-liquidity-based: pro-rata share of a fixed per-market **Volume Reward**
  over an **Eligible Term**, by **Eligible Volume**.
- Eligible Participants must be **direct clearing Participants connecting via API or ISV** and in
  good standing. **Excluded:** DMM-agreement holders, LPP participants, and IBs/FCMs and their
  customers transacting through them. Auto-enrolled, no participant limit.
- **Eligible Volume** = CLOB trades "between the price levels specified on the Exchange website" —
  the band is discretionary and published, not fixed in the filing. Kalshi hard-codes $0.03–$0.97.
- **Volume Multipliers** may be applied during designated windows, as published.
- **No per-contract cap.** Kalshi's VIP caps at $0.005/contract/participant explicitly to avoid
  price distortion; Polymarket US files no analogous cap.

## 3. Expired: LPP and Market Maker Program

Both **expired 2026-05-22** ([LPP-2026-05-08-expiry.pdf](sources-polymarket-us/LPP-2026-05-08-expiry.pdf),
[MMP-2026-05-08-expiry.pdf](sources-polymarket-us/MMP-2026-05-08-expiry.pdf)). Recorded because
the terms are the template if either is revived, and because the LPP carried the only **explicit
numeric notice periods** in the whole corpus:

- **Fixed weekly Stipend** per opted-in Series for continuous two-sided quotes; requirement
  categories published (minimum display size, maximum quote width, minimum uptime, minimum market
  coverage), values in Confidential Appendix B. Stipends pro-rata reduced if uptime falls short;
  aggregated and **paid monthly**.
- Entry by application, **approval at sole discretion**, with an **indefinite waitlist** — the
  Exchange may hold applicants until an incumbent exits.
- **Revocation on ≥ 7 days' written notice**, except for material breach, Rulebook/law violation,
  or **gaming**, where revocation is **immediate**.
- **Parameter changes on 7 days' notice before the first day of the Eligible Period.**
- A **Specialized** LPP was also filed 2026-03-18 ([SLPP-2026-03-18.pdf](sources-polymarket-us/SLPP-2026-03-18.pdf));
  a **2026 Market Maker Program** was filed 2026-04-24 ([MMP-2026-04-24.pdf](sources-polymarket-us/MMP-2026-04-24.pdf))
  before the May expiry. Whether anything replaced these after 2026-05-22 is an **open question** —
  no successor filing appears in the notices index as of 2026-09-02.

---

## 4. Fees — current schedule

Self-certified **2026-08-28**, effective 10 business days later
([Fees-2026-08-28.pdf](sources-polymarket-us/Fees-2026-08-28.pdf)). Relevant because maker
economics interact directly with MLIP scoring.

- **Maker fee: zero for all Participants.** The prior at-trade maker rebate was discontinued and
  replaced.
- **At-trade maker rebate**, as a % of gross taker fees generated on the Participant's maker-side
  transactions, tiered on **prior-calendar-month** notional maker volume:
  **10%** ($2M–$15M), **15%** ($15M–$50M), **20%** ($50M+). Below $2M: no fee, no rebate.
- **Taker fee rebate**, % of taker fees actually paid, tiered on prior-month notional taker volume:
  **10%** ($500K–$25M), **25%** ($25M–$100M), **90%** ($100M+). **Paid weekly.**
- **Accelerated Tier Placement**: a Participant may claim a tier by showing verifiable trailing
  30-day volume **on another prediction market** — usable **once**.
- Because tiers key off the prior calendar month, **"rebate levels are deterministic and known at
  the start of each month."** That is a genuine planning guarantee and worth exploiting.
- The Exchange "retains the discretion to update the volume thresholds and rebate amounts as the
  Exchange evolves, subject to applicable self-certification requirements."

---

## 5. What can change, and on what notice

The core question. Answers differ sharply by parameter, and the strongest guarantees are
regulatory rather than contractual.

| What | Who may change it | Notice |
|---|---|---|
| `rewardPool`, `discountFactor`, `targetSize` | Exchange, sole discretion | **None.** "may be adjusted between time periods"; publication to the website *is* the notice, and it is contemporaneous |
| Which contracts/Time Periods are in a programme | Exchange, sole discretion | None; published on the website |
| MLIP/MVIP **Terms and Conditions** | Exchange, "at any time" | **Prospective only**; communicated "in writing… by publishing the updated Terms and Conditions on the Website"; **filed with CFTC under Part 40** where required |
| Programme existence (modify/extend/terminate) | Exchange, sole discretion | None stated for MLIP. Cf. LPP/MMP, which were wound down via a filed **expiry amendment ~2 weeks ahead** |
| Eligibility criteria | Exchange, sole discretion | Must be "posted publicly on the Exchange Website" |
| Fees / rebate tiers | Exchange | **10 business days** after CFTC self-certification |
| Rulebook (substantive) | Exchange | CFTC Reg **40.6(a)**: filed ≥ 1 business day before effect; in practice **10 business days** |
| Rulebook (non-substantive) | Exchange | CFTC Reg **40.6(d)**: **weekly** notification *after the fact* |
| Participant's programme status | Exchange, sole discretion | Immediate — disqualification/exclusion for Rulebook violations |

**The load-bearing points:**

1. **The three headline parameters carry no notice obligation whatsoever.** The filing says they
   may be adjusted between Time Periods; the docs say the current schedule is published live. For
   a game-day contract that means up to three parameter regimes in one day (`early` → `day_of` →
   `live`), each of which can differ. **Never cache `discountFactor` or `targetSize` across a
   period boundary** — re-read before quoting.
2. **But the *rules* are genuinely protected, and that is the real difference from polymarket.com.**
   Being a DCM means programme terms, fees and Rulebook changes route through CFTC Part 40
   self-certification, which is public, dated, and archived. Polymarket US has committed in every
   incentive filing that **"the effective terms of the Program will be posted and publicly
   available on the Exchange's website"** — the original 2025-11-25 SOIP filing said **"every
   week."** The offshore CLOB offers none of this.
3. **Watch for the withdrawal pattern.** The notices index contains filings later re-posted as
   `(Withdrawn)` — RFQ Rulebook Update (2026-07-02), Refer-A-Friend (2026-08-10), Deposit and
   Trading Incentive (2026-08-12). A certified filing is not final until its effective date passes
   without withdrawal.
4. **Personnel/structure churn is high.** The CCO signing changed from Andrew Clifford to Megan
   McGrath between March and August 2026; the incentive-programme Rulebook cite moved from **3.11
   to 3.15**. Cite rule numbers by date.
5. **Unverified:** the ToS/Website Terms of Use pages on polymarket.us and polymarket.com are
   SPA-rendered and return no terms text to a fetch, so no contractual notice clause from the
   *website* terms could be read. Recorded as **not verified**, not as "no such clause." The
   Rulebook itself is at `polymarketexchange.com/files/legal/latest/rulebook` and is fetchable.

---

## 6. The other Polymarket

`polymarket.com` — the offshore CLOB, Adventure One QSS Inc. — runs an unrelated program. Fields
do **not** map onto anything above. Verified by hand 2026-09-02 via
`clob.polymarket.com/sampling-markets`: **15,976 reward-enabled markets, 501 distinct
`(min_size, max_spread, rewards_daily_rate)` configs, ~148,425 USDC/day**, paid daily at ~midnight
UTC in USDC.e on Polygon (`0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174`). Scoring is
`S(v,s) = ((v−s)/v)² × b` with scaling factor **c = 3.0**, two-sided liquidity required when the
midpoint is outside [0.10, 0.90]. That venue has a real JSON API and **no regulatory notice regime
at all** — the mirror image of the tradeoff here.

## Keeping this current

1. **Live parameters** — re-pull and diff. `data/*.json` is the committed, diffable record; the
   raw payload is gitignored because 86k symbol slugs churn daily and would bury real changes.

   ```sh
   python3 scripts/pull_polymarket_us_rewards.py
   git diff --stat data/
   ```

2. **New filings** — the notices index is a plain JSON listing, no auth, no JS challenge. This is
   the fastest way to detect an amendment:

   ```sh
   curl -s 'https://www.polymarketexchange.com/files/notices/' \
     | python3 -c 'import json,sys;fs=json.load(sys.stdin)["files"];\
   [print(f["lastModified"][:10], f["filename"]) for f in sorted(fs,key=lambda x:x["lastModified"])[-15:]]'
   ```

   114 notices as of 2026-09-02. Filter on `Incentive|Liquidity|Market Maker|Fee`.

3. **Open questions** —
   - Did anything replace the LPP / Market Maker Program after they expired 2026-05-22?
   - Do `daily`, `daily_event` and `tournament_with_cutoff` correspond to filed Time Period types,
     or are they product-side inventions outside the filed taxonomy?
   - Filing vs docs disagree on the Pre-Event / Event-Day boundary (day-before vs 6-hours). Resolve
     before relying on period timing.

## Source index

| File | Date | What it establishes |
|---|---|---|
| [MLIP-2026-04-07-amended.pdf](sources-polymarket-us/MLIP-2026-04-07-amended.pdf) | 2026-04-07 | **Current MLIP terms**: eligibility, pro-rata scoring, Time Period definitions, modification clause |
| [MLIP-2026-03-17.pdf](sources-polymarket-us/MLIP-2026-03-17.pdf) | 2026-03-17 | Rename from Standing Order Incentive Program |
| [SOIP-2026-03-03-amended.pdf](sources-polymarket-us/SOIP-2026-03-03-amended.pdf) | 2026-03-03 | First amendment to the original programme |
| [SOIP-2025-11-25-original.pdf](sources-polymarket-us/SOIP-2025-11-25-original.pdf) | 2025-11-25 | Programme origin; Rulebook 3.11; **"terms… posted… every week"**; NFA as RSP |
| [MVIP-2026-04-07-amended.pdf](sources-polymarket-us/MVIP-2026-04-07-amended.pdf) | 2026-04-07 | Current volume programme |
| [MIP-2026-03-05.pdf](sources-polymarket-us/MIP-2026-03-05.pdf) | 2026-03-05 | Volume programme origin; Eligible Volume/Multiplier definitions |
| [LPP-2026-04-07-amended.pdf](sources-polymarket-us/LPP-2026-04-07-amended.pdf) | 2026-04-07 | LPP terms: 7-day notice periods, waitlist, stipend structure |
| [LPP-2026-05-08-expiry.pdf](sources-polymarket-us/LPP-2026-05-08-expiry.pdf) | 2026-05-08 | **LPP expires 2026-05-22**; Rulebook cite moves to 3.15 |
| [MMP-2026-05-08-expiry.pdf](sources-polymarket-us/MMP-2026-05-08-expiry.pdf) | 2026-05-08 | **Market Maker Program expires 2026-05-22** |
| [MMP-2026-04-24.pdf](sources-polymarket-us/MMP-2026-04-24.pdf) | 2026-04-24 | 2026 Market Maker Program, filed weeks before the expiry |
| [SLPP-2026-03-18.pdf](sources-polymarket-us/SLPP-2026-03-18.pdf) | 2026-03-18 | Specialized Liquidity Provider Program |
| [Fees-2026-08-28.pdf](sources-polymarket-us/Fees-2026-08-28.pdf) | 2026-08-28 | Current fees: zero maker fee, tiered maker/taker rebates, Accelerated Tier Placement |
| [WeeklyRuleChange-2026-08-28.pdf](sources-polymarket-us/WeeklyRuleChange-2026-08-28.pdf) | 2026-08-28 | Reg 40.6(d) weekly non-substantive notification in practice |

Docs site pages used for scoring/cadence detail not present in the filings:
`docs.polymarket.us/incentives/liquidity`; live schedule at `polymarket.us/rewards`.
Rulebook: `polymarketexchange.com/files/legal/latest/rulebook`.
