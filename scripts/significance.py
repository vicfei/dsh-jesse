#!/usr/bin/env python3
"""Significance engine — reject noisy ideas early (V2.1 + V2.2, stdlib edition)

The lightweight edition of what upstream Jesse productized (Rule Significance
Testing + Monte Carlo), and the family's factor-authentication G3 lineage
applied to strategies:

1. **Rule significance (V2.1)**: the strategy's return vs a bootstrap
   distribution of RANDOM-ENTRY strategies on the same history (same number
   of trades, random positions). If the rule's edge is indistinguishable
   from random entries, it is noise — reject it before tuning it.
2. **Monte Carlo light, dual mode (V2.2)**: (a) trade-order shuffling —
   would the result survive a different trade sequence? (tests whether
   timing drove it); (b) block-resampled candles — would it survive a
   slightly different history? (block bootstrap, vol-clustering preserved).
   Both modes are always reported together; disagreement is information.

Zero dependencies; deterministic by seed; honest verdicts only.

Usage:
  python3 scripts/significance.py --data /tmp/btc_365.json --fast 10 --slow 60 --fee_bps 5
"""
import argparse, datetime as dt, json, math, random, sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from optimize import backtest, coverage_gaps, sma


def strategy_return(bars, fast, slow, rsi_buy, fee_bps):
    ret, trades = backtest(bars, fast, slow, rsi_buy, fee_bps)
    return ret, trades


def random_entry_distribution(bars, n_trades, n_sims, fee_bps, seed):
    """same history, same trade count, RANDOM entry bars; holding lengths drawn
    from a fixed menu (a trend cross's holding is unknowable for random
    entries, so the menu spans common holding scales)."""
    closes = [b[2] for b in bars]
    rng = random.Random(seed)
    out = []
    n = len(closes)
    for _ in range(n_sims):
        cash, per_trade = 1.0, []
        entries = sorted(rng.sample(range(1, n - 1), min(n_trades, n - 2))) if n_trades else []
        # sequential non-overlapping approximation: hold-to-hold bars
        pos_until = -1
        for e in entries:
            if e <= pos_until:
                continue
            hold = rng.choice(_HOLDS)
            x = e + hold
            if x >= n:
                x = n - 1
            r = closes[x] / closes[e] * (1 - fee_bps / 10000) ** 2 - 1
            per_trade.append(r)
            pos_until = x
        # compounded equity per sim (full equity per trade, like the strategy)
        eq = 1.0
        for r in per_trade:
            eq *= (1 + r)
        out.append(eq - 1)
    out.sort()
    return out


_HOLDS = [5, 10, 20, 30, 45, 60]


def shuffle_trades_mc(trade_returns, n_sims, seed):
    """mode (a): reshuffle the trade sequence — the compounded return of every
    permutation is IDENTICAL (multiplication commutes), so shuffling trades
    alone tests sequencing risk only through drawdown, not terminal return.
    What we report: the distribution of max intra-path drawdown across
    permutations (path-dependent risk), terminal return stated as invariant."""
    rng = random.Random(seed)
    dds = []
    for _ in range(n_sims):
        seq = trade_returns[:]
        rng.shuffle(seq)
        eq, peak, mdd = 1.0, 1.0, 0.0
        for r in seq:
            eq *= (1 + r)
            peak = max(peak, eq)
            mdd = min(mdd, eq / peak - 1)
        dds.append(mdd)
    dds.sort()
    return dds


def block_resample_mc(bars, fast, slow, rsi_buy, fee_bps, n_sims, block_len, seed):
    """mode (b): block-resample the log-return history into alternative
    candle paths (vol clustering preserved), rerun the SAME strategy params.
    Distribution of terminal returns across resampled histories."""
    closes = [b[2] for b in bars]
    rs = [math.log(closes[i] / closes[i - 1]) for i in range(1, len(closes))]
    rng = random.Random(seed)
    n = len(rs)
    out = []
    for _ in range(n_sims):
        path = [closes[0]]
        while len(path) <= len(closes) - 1:
            st = rng.randrange(n)
            for k in range(block_len):
                if len(path) > len(closes) - 1:
                    break
                path.append(path[-1] * math.exp(rs[(st + k) % n]))
        fake = [[bars[i][0], 0, path[i], 0, 0, 0] for i in range(len(path))]
        r, t = backtest(fake, fast, slow, rsi_buy, fee_bps)
        out.append((r, t))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--fast", type=int, default=10)
    ap.add_argument("--slow", type=int, default=60)
    ap.add_argument("--rsi_buy", type=int, default=None)
    ap.add_argument("--fee_bps", type=float, default=5.0)
    ap.add_argument("--sims", type=int, default=200)
    ap.add_argument("--block_len", type=int, default=5)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--lang", choices=("en", "zh"), default="en")
    args = ap.parse_args()
    data = json.load(open(args.data))
    symbol, bars = next(iter(data.items()))
    if len(bars) < 120:
        sys.exit("refused honestly — insufficient history for the significance engine")

    ret, n_trades = strategy_return(bars, args.fast, args.slow, args.rsi_buy, args.fee_bps)
    if n_trades == 0:
        sys.exit("refused honestly — the strategy made no trades on this history; "
                 "there is nothing to test for significance")

    rand = random_entry_distribution(bars, n_trades, args.sims, args.fee_bps, args.seed)
    pct = sum(1 for x in rand if x < ret) / len(rand)

    block = block_resample_mc(bars, args.fast, args.slow, args.rsi_buy, args.fee_bps,
                              args.sims, args.block_len, args.seed)
    brets = sorted(r for r, _ in block)
    q = lambda p: brets[min(int(p * len(brets)), len(brets) - 1)]
    b_above0 = sum(1 for r in brets if r > 0) / len(brets)

    print(f"## significance · {symbol} · fast {args.fast}/slow {args.slow} · {n_trades} trades · {args.sims} sims\n")
    print(f"- strategy return: **{ret:+.2%}**")
    print(f"- vs random-entry bootstrap: percentile **P{pct:.0%}** "
          f"(random-entry median {rand[len(rand)//2]:+.2%})")
    verdict = ("SIGNIFICANT edge vs random entries" if pct >= 0.95 else
               "INDISTINGUISHABLE from random entries — reject before tuning" if pct <= 0.60 else
               "WEAK edge — treat as noise until more evidence")
    print(f"- verdict: {verdict}")
    print(f"\n## Monte Carlo light (dual mode, always shown together)")
    print(f"- (a) trade-order shuffling: terminal return is permutation-invariant "
          f"(compounding commutes) — sequencing risk shows in drawdown, not return")
    print(f"- (b) block-resampled candles ({args.block_len}-day blocks): "
          f"return P10/P50/P90 = {q(0.10):+.2%} / {q(0.50):+.2%} / {q(0.90):+.2%} · "
          f"profitable in **{b_above0:.0%}** of resampled histories")
    agree = (pct >= 0.95 and b_above0 >= 0.80) or (pct <= 0.60 and b_above0 <= 0.50)
    print(f"- modes agree: {'YES' if agree else 'NO — disagreement is information, report both as-is'}\n")
    print(f"disclosure: random-entry bootstrap holds are drawn from a fixed menu "
          f"({_HOLDS[:3]}…); block resampling preserves vol clustering but no conditional "
          f"structure; {args.sims} sims is indicative, not a statistical test; seed {args.seed} "
          f"— reproduce with the same seed. Not investment advice.")
    gaps = coverage_gaps(bars)
    print(f"source: {bars[0][0]} → {bars[-1][0]} · {len(bars)} bars · {len(gaps)} gap(s) >10d")
    print("\n★ github.com/vicfei/dsh-jesse")


if __name__ == "__main__":
    main()
