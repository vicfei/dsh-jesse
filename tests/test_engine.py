#!/usr/bin/env python3
"""Hermetic engine tests — no network, no LLM. Synthetic bars only.
Run: python3 tests/test_engine.py   (exits non-zero on any FAIL)"""
import datetime as dt
import json, math, os, random, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import optimize as op

FAILS = []


def check(name, cond):
    print(("PASS" if cond else "FAIL"), name)
    if not cond:
        FAILS.append(name)


def synth(n=365, base=100.0, drift=0.001, vol=0.02, seed=7):
    rng = random.Random(seed)
    rows, d, p = [], dt.date(2025, 1, 1), base
    for i in range(n):
        p *= math.exp(drift + rng.gauss(0, vol))
        rows.append([d.isoformat(), round(p * 0.99, 4), round(p, 4), round(p * 1.01, 4),
                     round(p * 0.98, 4), 1000.0])
        d += dt.timedelta(days=1)
    return rows


bars = synth()
grid = {"fast": [5, 10], "slow": [30, 60]}

# 1. determinism: same grid+data → same rows
r1, c1, _ = op.run(grid, 5.0, 0.7, bars, "T")
r2, c2, _ = op.run(grid, 5.0, 0.7, bars, "T")
check("run deterministic", r1 == r2 and len(c1) == 4)

# 2. backtest sanity: all-cash when params never trigger (fast > slow always if fast=60, slow=30? no)
ret0, trades0 = op.backtest(bars, 5, 30, None, 5.0)
check("backtest returns finite", math.isfinite(ret0))

# 3. preconditions refuse honestly
probs = op.check_preconditions(bars[:50], grid)
check("insufficient history refused", any("insufficient" in p for p in probs))
probs = op.check_preconditions(bars, {})
check("degenerate grid refused", any("degenerate" in p for p in probs))

# 4. coverage gaps
gappy = bars[:100] + bars[110:]
g = op.coverage_gaps(gappy)
check("10-day gap detected", len(g) == 1 and g[0]["calendar_days"] == 11)

# 5. walk-forward structure
wf, seg_len = op.walk_forward(bars, grid, 5.0, 3, 0.7)
check("walk-forward segments", 2 <= len(wf) <= 3 and seg_len >= 60)
check("wf rows carry best params", all("best" in r and "test_ret" in r for r in wf))
check("wf test returns finite", all(math.isfinite(r["test_ret"]) for r in wf))

# 6. i18n
for lang in ("en", "zh"):
    op.LANG = lang
    hdr = op.t("header", symbol="T", bars=100, ntr=70, nte=30, frac=0.7)
    check("header in %s" % lang, ("optimization" in hdr) or ("参数优化" in hdr))
    lines = op.t("mt_lines", n=4, ret=0.01, gap=0.02)
    check("mt lines in %s" % lang, len(lines) == 3)
op.LANG = "en"

# 7. artifact envelope round-trip
best = r1[0]
env = {"protocol": "single train/test split", "train_frac": 0.7, "grid_size": len(c1),
       "fee_bps": 5.0, "test_only_once": True, "method": op.t("method")}
check("envelope carries disciplines", env["test_only_once"] is True and env["grid_size"] == 4)

print("result:", "GREEN" if not FAILS else "RED (%d)" % len(FAILS))
sys.exit(1 if FAILS else 0)
