# Return benchmark — T-bill yield on the same cash

**Last verified: 2026-09-08.** Rates as of the Treasury close of **2026-09-04** (most recent
row published). This document defines the measurement convention for every return figure in
this repo.

> **The rule.** The benchmark is the **coupon-equivalent US Treasury bill yield on the same
> cash**. Every return quoted anywhere in this repo is a **spread to that benchmark, in basis
> points**, never a bare dollar figure and never a bare percentage.

The reason this needs stating: every number in
[`kalshi-incentive-programmes.md`](kalshi-incentive-programmes.md) is an absolute dollar
amount with no denominator — a $1,000/day LIP pool, a $0.005/contract VIP cap, a $50,000/week
LPP series. Kalshi is fully collateralised, so earning any of it requires committing cash that
could otherwise sit in bills. A revenue figure without that hurdle attached is not a return.

---

## 1. The benchmark

**Instrument.** US Treasury bills, quoted on a **coupon-equivalent (bond-equivalent) basis**,
from Treasury's Daily Treasury Bill Rates.

Two deliberate exclusions:

- **Not the bank-discount rate.** Discount basis divides by face value rather than price and
  understates the actual return on cash. It is also not comparable to a stated APY, which is
  what the venue quotes. Using it would flatter every spread by roughly 6–9bp at current
  levels.
- **Not SOFR or fed funds.** Those are borrowing rates. The question here is what this cash
  could *earn*, risk-free, which is a bill.

**Tenor — matched to capital availability.** Market-making collateral recycles continuously
rather than being locked to a term, so the **4-week coupon equivalent is the primary
benchmark**. The 13-week is carried alongside for capital committed to a full programme term.
This is the one assumption in this document most likely to need changing; it is isolated here
so that changing it is a one-line edit.

### Anchor values — Treasury close, 2026-09-04

| Tenor | Bank discount | **Coupon equivalent** | |
|---|---:|---:|---|
| 4-week | 3.66 | **3.72%** | ← primary benchmark |
| 13-week | 3.77 | **3.86%** | programme-term capital |
| 26-week | 3.88 | **4.01%** | reference only |

September 2026 to date, 4-week coupon equivalent has traded 3.72–3.76% and 13-week 3.84–3.87%
— a ~4bp band. The curve is mildly upward-sloping at the front end, so **tenor choice is worth
roughly 14bp** between 4-week and 13-week. That is small against incentive P&L but not against
a marginal strategy, which is why the tenor is stated rather than assumed.

---

## 2. The venue carry leg — collateral on Kalshi is not dead cash

The single most important input to this benchmark, and the one that inverts the naive
assumption:

> **Kalshi pays interest on cash *and* on open-position collateral.** From the help centre:
> *"This means that you will also earn interest on the underlying collateral for your
> positions."* Accrual is daily — *"based on the net value of the portfolio at 12am ET each
> day"* — and paid monthly.

Treating Kalshi collateral as zero-yield would overstate the hurdle by the entire APY and make
essentially every strategy look unviable. It does not. The carry leg is a modest drag, not a
wall:

| | Rate | |
|---|---:|---|
| Kalshi APY | **3.25%** | as of 2026-09-08, **variable** |
| less: 4-week T-bill CE | 3.72% | |
| **= carry drag (primary)** | **−47 bp** | annualised |
| less: 13-week T-bill CE | 3.86% | |
| **= carry drag (13-week)** | **−61 bp** | annualised |

**So the hurdle for a Kalshi strategy is ~47bp of carry drag, not ~372bp of foregone yield.**
Incentive P&L is very nearly the whole spread.

### Conditions that bind

- **$250 minimum balance.** Below it, no interest accrues at all and the drag becomes the full
  benchmark rate. This binds on small-scale testing.
- **SSN required** for interest payments above $10/year — the same reporting threshold that
  governs LIP credits.
- **Payment lag.** Accrued daily, paid monthly, *"normally within the first week of the
  following month but can take up to 10 business days."* Accrual date, not payment date, is
  the correct basis for attribution.
- **Rate is variable** and moves with prevailing Fed rates. It is set by what Kalshi receives
  from its banking partners, not by any published formula, so it cannot be forecast from the
  curve.

> **Source conflict, recorded not resolved.** Kalshi's help centre states **3.25%** (fetched
> twice, 2026-09-08). Several secondary aggregators reported **3.75%** and **4.00%** for early
> September 2026. The help centre is the primary source and is used here. Because a
> **50bp discrepancy is comparable to the entire carry drag**, confirm against an actual
> monthly interest statement before treating any spread below ~100bp as real.

---

## 3. The convention

```
r_gross  = (incentive credits + trading P&L + APY credited) / capital_base
r_bench  = T-bill coupon-equivalent yield, tenor-matched, same period

spread   = r_gross − r_bench                    ← quote this, in bps
```

Report the spread **decomposed into three legs**, always. The decomposition is what makes a
result diagnosable rather than merely a number:

```
spread = incentive leg + trading leg + carry leg

  incentive leg = incentive credits / capital_base       (annualised)
  trading leg   = trading P&L / capital_base             (annualised)
  carry leg     = APY − r_bench                          (already annual, ≈ −47bp)
```

The carry leg is near-constant and known in advance. The trading leg is where adverse
selection shows up. Collapsing them hides the fact that an incentive programme can pay well
while the fills underneath it lose money.

### Three definitional guards

Each of these is a specific way prediction-market returns get quoted meaninglessly.

**1. Capital base is time-weighted committed collateral.** Locked collateral plus the free
cash that must sit at the venue to support the strategy. **Not** average account equity, and
**never** notional traded. VIP's $0.005/contract cap earns $5 on 1,000 contracts; quoted
against notional that can be made to look like almost any number.

**2. APY belongs in the numerator, not the benchmark.** It is tempting to benchmark against
Kalshi's 3.25% instead — "what the cash earns if I do nothing here." Don't. Keeping the APY in
strategy return and the bill in the benchmark makes the venue drag visible as its own named
line. Netting it away silently concedes 47bp and hides the $250 minimum and the payment lag.

**3. Annualise simply, and always show the raw period figure beside it.** LIP periods are 15
or 90 minutes. Scaling a 15-minute return by 35,040 periods/year produces numbers that are
arithmetically valid and completely unreal. Rules:

- `spread_annual = spread_period × (365 / days_committed)`
- Annualise only over the hours capital was **actually committed**, not wall-clock elapsed.
- **Simple, not compounded** — capacity does not scale with the balance, so the proceeds are
  not reinvestable into the same edge.
- Any annualised figure above ~2,000bp should be treated as a capacity question, not a return.

---

## 4. Worked example

$100,000 committed to LIP market-making for 30 days. Suppose it earns $1,400 in LIP credits
and loses $300 on the fills.

| Component | Period | Annualised |
|---|---:|---:|
| LIP credits | +$1,400 | **+17.03%** |
| Trading P&L | −$300 | **−3.65%** |
| Kalshi APY credited | +$267 | +3.25% |
| **Gross return** | **+$1,367** | **+16.63%** |
| less benchmark (4-week CE) | | −3.72% |
| **Spread to benchmark** | | **+12.91% = +1,291 bp** |

Decomposed:

```
incentive leg   +1,703 bp
trading leg       −365 bp
carry leg          −47 bp        (3.25% APY − 3.72% bill)
                 ─────────
spread           +1,291 bp
```

The carry leg is **3.6% of the total spread**. That is the point of doing this properly: the
thing everyone worries about (foregone T-bill yield) is nearly irrelevant here, while the
trading leg — 21% of gross incentive income, negative — is where the strategy actually lives
or dies.

---

## 5. Open questions

1. **Does APY accrue on collateral locked behind *unfilled resting orders*?** ⚠️ **Blocking.**
   The help centre defines the accrual base as available funds plus *"your portfolio value at
   the end of the day, based on last traded prices."* Cash locked behind a resting order that
   has never filled is arguably neither — it is not available, and it is not a position. For a
   market maker whose entire strategy is unfilled resting orders, this determines whether the
   carry leg is −47bp or −372bp, an **8× difference in the hurdle**. No public document
   answers it. Verify against a real monthly interest statement.
2. **The 3.25% / 3.75% source conflict** above. 50bp, comparable to the whole carry leg.
3. **`period_reward` units are undocumented** — carried forward from the programme reference.
   The LIP incentive leg cannot be computed until this is settled; 200000 is inferred as
   fixed-point 1e-4 USD = $20.00/period.
4. **LIP Reference Price behaviour above the reference** — carried forward. The filed algebra
   gives 4× at a 0.50 discount factor where the help centre says credit caps at 1.0×. Affects
   the size of the incentive leg directly.

Items 3 and 4 block the numerator; item 1 blocks the denominator's carry treatment. Until all
three are resolved, spreads computed under this convention are **structurally correct but not
yet trustworthy in magnitude**.

---

## Keeping this current

Both legs move independently, and a September 2026 Fed decision is live, so neither figure
should be treated as durable.

**Benchmark rates** — Treasury's XML endpoint, no auth, no JS challenge:

```sh
curl -s 'https://home.treasury.gov/resource-center/data-chart-center/interest-rates/pages/xml?data=daily_treasury_bill_rates&field_tdr_date_value_month=202609' \
  | grep -oE '<d:(INDEX_DATE|ROUND_B1_YIELD_4WK_2|ROUND_B1_YIELD_13WK_2)[^<]*</d:[^>]*>'
```

`ROUND_B1_YIELD_*` is the coupon equivalent; `ROUND_B1_CLOSE_*` is the bank discount rate.
Use the former. Change `field_tdr_date_value_month` to the current `YYYYMM`.

**Kalshi APY** — no API; the help centre is the only primary source:
`help.kalshi.com/en/articles/13823847-apy-on-kalshi`. Re-read and re-stamp the as-of date
whenever a spread is computed, and prefer an actual monthly interest statement over the
published figure when one is available.

## Sources

| Source | What it establishes |
|---|---|
| Treasury Daily Treasury Bill Rates (XML, month `202609`) | Benchmark rates, both bases, daily |
| `help.kalshi.com/en/articles/13823847-apy-on-kalshi` | APY rate, accrual base incl. position collateral, $250 minimum, SSN threshold, monthly payment |
| `news.kalshi.com/p/interest-cash-open-positions` | Programme announcement; interest applies to *"the underlying collateral for your positions"*; rate tracks prevailing Fed rates |
| [`kalshi-incentive-programmes.md`](kalshi-incentive-programmes.md) | The numerator — programme terms, pool sizes, payout algebra |
