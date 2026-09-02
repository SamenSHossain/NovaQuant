#!/usr/bin/env python3
"""Pull the live polymarket.us liquidity-incentive schedule.

polymarket.us publishes no JSON API. gamma-api/clob/data-api.polymarket.us do not
resolve, and api.polymarket.us is 401-gated and undocumented. The reward parameters
exist only inside the Next.js RSC flight payload embedded in the /rewards HTML.

So this scrapes that payload. That is load-bearing and fragile -- a Next.js version
bump can change the envelope -- so every extraction step asserts, and the script exits
non-zero rather than emitting an empty table. Silent-empty is the failure mode that
would quietly poison downstream sizing, so it is the one thing engineered against.

Field names below are the venue's own, mirrored verbatim. Do not rename them.

Usage:
    python3 scripts/pull_polymarket_us_rewards.py            # write snapshot, print markdown
    python3 scripts/pull_polymarket_us_rewards.py --no-write # print only
"""

import argparse
import datetime as dt
import json
import pathlib
import sys
import urllib.request

SOURCE_URL = "https://polymarket.us/rewards"
ANCHOR = '"programs":['

# The venue's own field names, verbatim. A payload missing any of these means the
# envelope changed and the parse can no longer be trusted.
REQUIRED_FIELDS = {
    "programId",
    "name",
    "subcategories",
    "period",
    "rewardPool",
    "discountFactor",
    "targetSize",
    "symbols",
}

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent


class ParseError(RuntimeError):
    """The page no longer looks the way we expect. Never degrade to empty output."""


def fetch(url=SOURCE_URL):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read().decode("utf-8", errors="replace")


def extract_programs(html):
    """Pull the programs[] array out of the embedded flight payload.

    Bracket-matching is required, not optional: the obvious regex over objects
    containing rewardPool matches nothing, because each program nests a symbols[]
    array. Confirmed against the live page.
    """
    text = html.replace('\\"', '"')

    start_key = text.find(ANCHOR)
    if start_key == -1:
        raise ParseError(
            f"anchor {ANCHOR!r} not found in {len(html):,} bytes of HTML -- "
            "the page structure changed, or the response was a shell/redirect"
        )

    start = text.index("[", start_key + len(ANCHOR) - 1)
    depth = 0
    end = None
    for i in range(start, len(text)):
        c = text[i]
        if c == "[":
            depth += 1
        elif c == "]":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    if end is None:
        raise ParseError("programs[] array is unterminated -- payload truncated")

    try:
        programs = json.loads(text[start:end])
    except json.JSONDecodeError as exc:
        raise ParseError(f"programs[] did not parse as JSON: {exc}") from exc

    if not programs:
        raise ParseError("programs[] parsed but is empty -- refusing to emit a blank snapshot")

    missing = REQUIRED_FIELDS - set(programs[0])
    if missing:
        raise ParseError(
            f"program objects are missing expected field(s): {sorted(missing)}. "
            f"Got: {sorted(programs[0])}"
        )

    return programs


def summarize(programs, pulled_at):
    """Flatten to the reference rows. symbols[] stays in the raw JSON only --
    inlining thousands of slugs would drown the doc."""
    rows = []
    for p in programs:
        rows.append(
            {
                "programId": p["programId"],
                "name": p["name"],
                "subcategories": p.get("subcategories") or [],
                "period": p["period"],
                "rewardPool": p["rewardPool"],
                "discountFactor": p["discountFactor"],
                "targetSize": p["targetSize"],
                "market_count": len(p.get("symbols") or []),  # derived, ours
                "pulled_at": pulled_at,  # ours
                "source_url": SOURCE_URL,  # ours
            }
        )
    rows.sort(key=lambda r: (-(r["rewardPool"] or 0), r["name"]))
    return rows


def counts(rows, field):
    out = {}
    for r in rows:
        out[r[field]] = out.get(r[field], 0) + 1
    return dict(sorted(out.items(), key=lambda kv: -kv[1]))


def render_markdown(rows, pulled_at):
    total_pool = sum(r["rewardPool"] or 0 for r in rows)
    total_markets = sum(r["market_count"] for r in rows)
    discounts = sorted({r["discountFactor"] for r in rows})
    targets = sorted({r["targetSize"] for r in rows})

    L = []
    L.append(f"- **Pulled:** {pulled_at}")
    L.append(f"- **Source:** {SOURCE_URL} (Next.js flight payload; no JSON API exists)")
    L.append(f"- **Programs live:** {len(rows)}")
    L.append(f"- **Total `rewardPool`:** ${total_pool:,.0f} per time period")
    L.append(f"- **Markets covered:** {total_markets:,} (program-market pairs)")
    L.append("")
    L.append("`period` distribution: " + ", ".join(f"`{k}` ({v})" for k, v in counts(rows, "period").items()))
    L.append("")
    L.append("`discountFactor` values: " + ", ".join(str(d) for d in discounts))
    L.append("")
    L.append(f"`targetSize` values: {targets[0]:,} … {targets[-1]:,} contracts ({len(targets)} distinct)")
    L.append("")
    L.append("| programId | name | period | rewardPool | discountFactor | targetSize | markets |")
    L.append("|---|---|---|---:|---:|---:|---:|")
    for r in rows:
        L.append(
            f"| `{r['programId']}` | {r['name']} | `{r['period']}` | "
            f"{r['rewardPool']:,} | {r['discountFactor']} | {r['targetSize']:,} | {r['market_count']:,} |"
        )
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--no-write", action="store_true", help="print markdown only, do not write a snapshot")
    ap.add_argument("--url", default=SOURCE_URL, help="override source URL (testing)")
    args = ap.parse_args()

    pulled_at = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    try:
        html = fetch(args.url)
        programs = extract_programs(html)
    except ParseError as exc:
        print(f"FATAL: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # network, DNS, TLS
        print(f"FATAL: fetch failed: {exc}", file=sys.stderr)
        return 1

    rows = summarize(programs, pulled_at)

    if not args.no_write:
        day = pulled_at[:10]

        # Two artifacts, deliberately. The parameters are what we want to diff across
        # pulls; the symbols[] slugs churn every day as games are listed and settle, and
        # committing 86k of them would bury a discountFactor change in noise. So the
        # small file is the committed, diffable one and the raw payload is gitignored.
        params = REPO_ROOT / "data" / f"polymarket_us_rewards_{day}.json"
        params.parent.mkdir(parents=True, exist_ok=True)
        params.write_text(
            json.dumps({"pulled_at": pulled_at, "source_url": args.url, "programs": rows}, indent=2, sort_keys=True)
            + "\n"
        )

        raw = REPO_ROOT / "data" / "raw" / f"polymarket_us_rewards_{day}.raw.json"
        raw.parent.mkdir(parents=True, exist_ok=True)
        raw.write_text(
            json.dumps({"pulled_at": pulled_at, "source_url": args.url, "programs": programs}, indent=2, sort_keys=True)
            + "\n"
        )

        print(
            f"wrote {params.relative_to(REPO_ROOT)} ({len(rows)} programs, "
            f"{params.stat().st_size / 1024:.0f} KB) and {raw.relative_to(REPO_ROOT)} "
            f"({raw.stat().st_size / 1024 / 1024:.1f} MB, gitignored)",
            file=sys.stderr,
        )

    print(render_markdown(rows, pulled_at))
    return 0


if __name__ == "__main__":
    sys.exit(main())
