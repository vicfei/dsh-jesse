#!/usr/bin/env python3
"""Strategy parameter optimizer (the Jesse concept seat, native implementation)

Upstream Jesse (8.8k★, MIT) is a mature full platform — accurate crypto
backtests, Optuna optimization, Rust indicators, significance testing, Monte
Carlo, and its own MCP server. This plugin is the **zero-dependency
auditable lightweight** of the same discipline: a stdlib-only grid optimizer
with fee-aware backtest evaluation and the anti-overfitting trio stated IN
the output itself:
1. train/test temporal split (default 70/30): pick on train, report test
2. an overfit-gap column (train-test return difference) in the table
3. a multiple-testing lens: scanning N parameter sets = N attempts, with a
   Bonferroni-style warning (factor-authentication G3 lineage — the
   significance of the picked-best must be discounted by the search size)

Strategy v0: SMA crossover + optional RSI filter (parameterized, fully
deterministic evaluation). For the heavy full platform (Optuna-grade tuning,
live trading), use upstream jesse — this is the complement, not a competitor.

Usage:
  python3 scripts/optimize.py --data /tmp/btc_365.json \
      --grid '{"fast":[5,10,20],"slow":[30,60,90],"rsi_buy":[25,35]}' --fee_bps 5
"""
import argparse, datetime as dt, itertools, json, sys

# English is the first language (family rule); Chinese is the --lang zh fallback.
LANG = "en"
STR = {
    "en": {
        "header": "## Parameter optimization · {symbol} · {bars} bars (train {ntr}/{nte} split {frac:.0%})",
        "bench": "benchmarks: train buy&hold {bht:+.2%} · test buy&hold {bhtest:+.2%}",
        "table_head": "| fast | slow | rsi_buy | train_ret | test_ret | overfit_gap | trades |",
        "mt_title": "## Multiple-testing warning (family discipline, factor-auth G3 lineage)",
        "mt_lines": [
            "- Scanned **{n}** parameter sets = {n} attempts. The train leader ({ret:+.2%}) must be read through a multiple-testing discount (Bonferroni intuition: alpha/{n}).",
            "- Overfit gap: the leader's train-test difference is **{gap:+.2%}** — the larger the gap, the more it fit train noise instead of structure.",
            "- The test window may be looked at ONCE: re-tuning after seeing it contaminates it; get a new data segment.",
        ],
        "footer": "engine: grid-optimizer v0 · fee {fee}bps · bar-level execution · span {a} → {b} · not investment advice",
        "ran_at": "ran at {ts}",
        "method": "grid scan with train/test split + overfit gap + multiple-testing lens",
    },
    "zh": {
        "header": "## 参数优化 · {symbol} · {bars} bars（train {ntr}/{nte} 切分 {frac:.0%}）",
        "bench": "基准：train 买入持有 {bht:+.2%} · test 买入持有 {bhtest:+.2%}",
        "table_head": "| fast | slow | rsi_buy | train_ret | test_ret | overfit_gap | trades |",
        "mt_title": "## 多重检验警示（家族纪律，因子鉴真 G3 同源）",
        "mt_lines": [
            "- 共扫描 **{n}** 组参数=做了 {n} 次尝试。train 榜首（{ret:+.2%}）的显著性须按多重检验折减看待（Bonferroni 直觉：α/{n}）。",
            "- 过拟合缺口：榜首 train-test 差 **{gap:+.2%}**——缺口越大，越像在拟合 train 的噪声而非结构。",
            "- test 段只许看一次：若据此回头调参再验，test 已被污染，需换新数据段。",
        ],
        "footer": "engine: grid-optimizer v0 · 费率 {fee}bps · bar 级执行 · span {a} → {b} · 非投资建议",
        "ran_at": "运行于 {ts}",
        "method": "网格扫描 + train/test 切分 + 过拟合缺口 + 多重检验视角",
    },
}


def t(key, **kw):
    s0 = STR[LANG].get(key, key)
    if isinstance(s0, list):
        return [x.format(**kw) for x in s0]
    return s0.format(**kw) if kw else s0


def sma(xs, n):
    out, s = [], 0.0
    for i, x in enumerate(xs):
        s += x
        if i >= n: s -= xs[i - n]
        out.append(s / n if i >= n - 1 else None)
    return out


def rsi(closes, n=14):
    out, g, l = [], 0.0, 0.0
    for i in range(1, len(closes)):
        ch = closes[i] - closes[i - 1]
        g = (g * (n - 1) + max(ch, 0)) / n
        l = (l * (n - 1) + max(-ch, 0)) / n
        out.append(100 - 100 / (1 + g / (l + 1e-12)) if i >= n else None)
    return [None] + out


def coverage_gaps(bars, threshold=10):
    gaps = []
    for i in range(1, len(bars)):
        try:
            a = dt.date.fromisoformat(str(bars[i - 1][0])[:10])
            b = dt.date.fromisoformat(str(bars[i][0])[:10])
        except ValueError:
            continue
        if (b - a).days > threshold:
            gaps.append({"from": str(bars[i - 1][0])[:10], "to": str(bars[i][0])[:10],
                         "calendar_days": (b - a).days})
    return gaps


def check_preconditions(bars, grid):
    problems = []
    if len(bars) < 120:
        problems.append(f"insufficient history: {len(bars)} bars, need >= 120 for a train/test split")
    if any(not isinstance(b[2], (int, float)) or b[2] <= 0 for b in bars):
        problems.append("non-positive or non-numeric close in input bars")
    combos = list(itertools.product(*[grid[k] for k in grid])) if grid else []
    if not combos:
        problems.append("degenerate grid: no parameter combinations")
    return problems


def scenario_paths(bars, obj, horizon_pad=20):
    """build deterministic scenario bar paths from a dsh-Kronos objective file:
    log-linear ramps from the last close to each terminal quantile (P10/P50/P90).
    The distribution lives in the terminal, not the path shape — a disclosed
    simplification."""
    last = obj.get("_anchor_close") or bars[-1][2]
    H = max(int(obj.get("horizon", 30)), 5)
    paths = {}
    for tag, key in (("P10", "terminal_P10"), ("P50", "terminal_P50"), ("P90", "terminal_P90")):
        term = obj.get(key)
        if not term or term <= 0:
            continue
        ratio = (term / last) ** (1 / H)
        p, path = None, []
        d0 = dt.date(2026, 1, 1)
        for i in range(H + horizon_pad + 1):
            p = last if i == 0 else (p * ratio if i <= H else term)  # anchor → ramp → flat
            iso = (d0 + dt.timedelta(days=i)).isoformat()
            path.append([iso, p * 0.995, p, p * 1.005, p * 0.995, 1000.0])
        paths[tag] = path
    return paths


def run_objective(grid, fee_bps, obj, bars):
    """rank parameter sets on the Kronos scenario bracket instead of the
    historical train window: each combo is backtested on the P10/P50/P90
    scenario paths; rank by the WORST bracket return (optimize the
    distribution, not the point)."""
    paths = scenario_paths(bars, obj)
    if not paths:
        sys.exit("refused honestly — the objective file lacks usable terminal quantiles")
    keys = list(grid)
    combos = list(itertools.product(*[grid[k] for k in keys]))
    rows = []
    for combo in combos:
        p = dict(zip(keys, combo))
        rs = {}
        for tag, path in paths.items():
            r, n = backtest(path, p.get("fast", 20), p.get("slow", 60), p.get("rsi_buy"), fee_bps)
            rs[tag] = round(r, 4)
        worst = min(rs.values())
        rows.append({**p, **{f"ret_{k}": v for k, v in rs.items()},
                     "worst_bracket": round(worst, 4)})
    rows.sort(key=lambda r: -r["worst_bracket"])
    return rows, combos, paths


def walk_forward(bars, grid, fee_bps, n_segments, seg_train):
    """rolling multi-segment validation: each segment's train picks the params,
    its own test scores them; chained across the tail. Returns per-segment rows."""
    closes_total = len(bars)
    seg_len = max(60, (closes_total - int(closes_total * seg_train)) // max(n_segments, 1))
    max_lookback = max([max(v) for v in grid.values() if isinstance(max(v), (int, float))] or [0])
    rows = []
    start = closes_total - seg_len * n_segments
    while start < closes_total - seg_len + 1:
        train = bars[max(0, start - int(seg_len * seg_train / (1 - seg_train) or seg_len)):start] or bars[:start]
        train = bars[:start] if not train else train
        test = bars[start:start + seg_len]
        if len(test) < 10 or len(train) < 30:
            break
        best, best_r = None, -1e18
        keys = list(grid)
        for combo in itertools.product(*[grid[k] for k in keys]):
            p = dict(zip(keys, combo))
            r_tr, _ = backtest(train, p.get("fast", 20), p.get("slow", 60), p.get("rsi_buy"), fee_bps)
            if r_tr > best_r:
                best_r, best = r_tr, p
        r_te, n_te = backtest(test, best.get("fast", 20), best.get("slow", 60), best.get("rsi_buy"), fee_bps)
        bh = test[-1][2] / test[0][2] - 1
        rows.append({"from": str(test[0][0])[:10], "to": str(test[-1][0])[:10],
                     "best": best, "train_ret": round(best_r, 4), "test_ret": round(r_te, 4),
                     "buy_hold": round(bh, 4), "test_trades": n_te})
        start += seg_len
    return rows, seg_len


def backtest(bars, fast, slow, rsi_buy, fee_bps, initial=100000.0):
    closes = [b[2] for b in bars]
    f, s, r = sma(closes, fast), sma(closes, slow), rsi(closes)
    fee = fee_bps / 10000
    pos, entry, cash, trades = 0, None, initial, 0
    for i in range(1, len(closes)):
        if f[i] is None or s[i] is None: continue
        long_ok = f[i] > s[i] and (rsi_buy is None or (r[i] is not None and r[i] < rsi_buy + 50))
        if pos == 0 and long_ok:
            pos, entry, trades = 1, closes[i] * (1 + fee), trades + 1
            cash -= entry
        elif pos == 1 and f[i] < s[i]:
            cash += closes[i] * (1 - fee); pos = 0
    final = cash + (closes[-1] * (1 - fee) if pos == 1 else 0)
    return final / initial - 1, trades


def run(grid, fee_bps, train_frac, bars, symbol):
    cut = int(len(bars) * train_frac)
    train, test = bars[:cut], bars[cut:]
    bh_train = train[-1][2] / train[0][2] - 1
    bh_test = test[-1][2] / test[0][2] - 1
    keys = list(grid)
    combos = list(itertools.product(*[grid[k] for k in keys]))
    rows = []
    for combo in combos:
        p = dict(zip(keys, combo))
        r_tr, n_tr = backtest(train, p.get("fast", 20), p.get("slow", 60), p.get("rsi_buy"), fee_bps)
        r_te, _ = backtest(test, p.get("fast", 20), p.get("slow", 60), p.get("rsi_buy"), fee_bps)
        rows.append({**p, "train_ret": round(r_tr, 4), "test_ret": round(r_te, 4),
                     "overfit_gap": round(r_tr - r_te, 4), "train_trades": n_tr})
    rows.sort(key=lambda r: -r["train_ret"])
    return rows, combos, (train, test, bh_train, bh_test)


def render(rows, combos, bench, symbol, bars, fee_bps, train_frac):
    train, test, bh_train, bh_test = bench
    print(t("header", symbol=symbol, bars=len(bars), ntr=len(train), nte=len(test), frac=train_frac))
    print(t("bench", bht=bh_train, bhtest=bh_test) + "\n")
    print(t("table_head"))
    print("|---|---|---|---|---|---|---|")
    for r in rows[:8]:
        print(f"| {r['fast']} | {r['slow']} | {r.get('rsi_buy', '—')} | "
              f"{r['train_ret']:+.2%} | {r['test_ret']:+.2%} | {r['overfit_gap']:+.2%} | {r['train_trades']} |")
    best = rows[0]
    n = len(combos)
    print("\n" + t("mt_title"))
    for line in t("mt_lines", n=n, ret=best["train_ret"], gap=best["overfit_gap"]):
        print(line)
    print(f"\n---\n*{t('footer', fee=fee_bps, a=bars[0][0], b=bars[-1][0])}*\n*{t('ran_at', ts=dt.datetime.now().isoformat(timespec='seconds'))}*")


def main():
    global LANG
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--grid", required=True)
    ap.add_argument("--fee_bps", type=float, default=5.0)
    ap.add_argument("--train_frac", type=float, default=0.7)
    ap.add_argument("--objective", metavar="FILE",
                    help="rank params on a dsh-Kronos --objective-out scenario bracket (P10/P50/P90) instead of the historical train window")
    ap.add_argument("--walkforward", type=int, default=0, metavar="N",
                    help="rolling multi-segment validation with N test segments (0 = single split)")
    ap.add_argument("--save", action="store_true", help="write the audit JSON artifact")
    ap.add_argument("--lang", choices=("en", "zh"), default="en",
                    help="output language (default en; zh is the fallback)")
    args = ap.parse_args()
    LANG = args.lang
    data = json.load(open(args.data))
    symbol, bars = next(iter(data.items()))
    grid = json.loads(args.grid)
    problems = check_preconditions(bars, grid)
    if problems:
        sys.exit("refused honestly — " + "; ".join(problems))
    gaps = coverage_gaps(bars)
    source = {"origin": "user-provided klines JSON", "symbol": symbol, "bars": len(bars),
              "date_range": [str(bars[0][0])[:10], str(bars[-1][0])[:10]], "coverage_gaps": gaps}
    if args.objective:
        obj = json.load(open(args.objective))
        rows, combos, paths = run_objective(grid, args.fee_bps, obj, bars)
        print(f"## objective optimization · {symbol} · scenario bracket from {args.objective}")
        print(f"- scenario: horizon {obj.get('horizon')} · P_above_current {obj.get('P_above_current', 0):.0%} · "
              f"fan width {obj.get('fan_width_80_rel', 0):.1%} (dsh-Kronos objective)")
        print(f"- ranking: worst-of-bracket (P10/P50/P90 scenario paths) — optimize the distribution, not the point\n")
        print("| fast | slow | ret_P10 | ret_P50 | ret_P90 | worst_bracket |")
        print("|---|---|---|---|---|---|")
        for r in rows[:8]:
            print(f"| {r['fast']} | {r['slow']} | {r.get('ret_P10', float('nan')):+.2%} "
                  f"| {r.get('ret_P50', float('nan')):+.2%} | {r.get('ret_P90', float('nan')):+.2%} "
                  f"| {r['worst_bracket']:+.2%} |")
        print("\n- honest notes: scenarios are NOT predictions (the Kronos disclosure rides in the "
              "objective file); scenario path shape is a log-linear ramp to each terminal quantile — "
              "the distribution lives in the terminal, not the path; params chosen here were NEVER "
              "scored on future data, only on the disclosed scenario bracket.")
        if args.save:
            import os
            os.makedirs("opts", exist_ok=True)
            artifact = {"schema": "opt-report/0", "symbol": symbol,
                        "envelope": {"protocol": "kronos-objective bracket",
                                     "grid_size": len(combos), "fee_bps": args.fee_bps,
                                     "objective_file": args.objective,
                                     "test_only_once": True, "method": "worst-of-bracket ranking"},
                        "source": source, "rows": rows,
                        "disclosure": "ranked on scenario brackets, not future data; scenarios are not predictions"}
            path = f"opts/{symbol.replace('/', '_')}-objective.json"
            json.dump(artifact, open(path, "w"), ensure_ascii=False, indent=1, default=str)
            print(f"→ {path}", file=sys.stderr)
        return
    if args.walkforward:
        wf_rows, seg_len = walk_forward(bars, grid, args.fee_bps, args.walkforward, args.train_frac)
        max_lookback = max([max(v) for v in grid.values() if isinstance(max(v), (int, float))] or [0])
        agg = 1.0
        for r in wf_rows:
            agg *= (1 + r["test_ret"])
        agg -= 1
        bh_all = bars[-1][2] / bars[wf_rows and (len(bars) - seg_len * len(wf_rows)) or 0][2] - 1
        print(f"## walk-forward · {symbol} · {len(wf_rows)} segments × {seg_len} bars (train frac {args.train_frac:.0%})")
        if seg_len < max_lookback:
            print(f"⚠ honest note: test segments ({seg_len} bars) are shorter than the grid's longest "
                  f"lookback ({max_lookback}) — long-lookback params cannot trade inside test segments; "
                  f"prefer fewer segments or a shorter-lookback grid")
        print(f"- chained walk-forward return: **{agg:+.2%}** · same-window buy&hold: {bh_all:+.2%}")
        drift = {f"{r['best'].get('fast')}x{r['best'].get('slow')}": 1 for r in wf_rows}
        print(f"- distinct best-param sets across segments: {len(drift)} of {len(wf_rows)} — drift is information, not noise to tune away\n")
        print("| from | to | best fast×slow | train_ret | test_ret | buy&hold | trades |")
        print("|---|---|---|---|---|---|---|")
        for r in wf_rows:
            print(f"| {r['from']} | {r['to']} | {r['best'].get('fast')}×{r['best'].get('slow')} "
                  f"| {r['train_ret']:+.2%} | {r['test_ret']:+.2%} | {r['buy_hold']:+.2%} | {r['test_trades']} |")
        print("\n- walk-forward honesty: each segment's params were chosen on ITS OWN train window only; "
              "the chained return is the realistic estimate, the single-split table is the optimistic one.")
        if args.save:
            import os
            os.makedirs("opts", exist_ok=True)
            artifact = {"schema": "opt-report/0", "symbol": symbol,
                        "envelope": {"protocol": "walk-forward", "segments": len(wf_rows),
                                     "segment_bars": seg_len, "train_frac": args.train_frac,
                                     "grid_size": None, "fee_bps": args.fee_bps,
                                     "test_only_once": True, "method": t("method")},
                        "source": source, "walk_forward": wf_rows,
                        "chained_return": round(agg, 4),
                        "disclosure": "walk-forward chained return is the realistic estimate; "
                                      "parameters drift across segments by design"}
            path = f"opts/{symbol.replace('/', '_')}-wf.json"
            json.dump(artifact, open(path, "w"), ensure_ascii=False, indent=1, default=str)
            print(f"→ {path}", file=sys.stderr)
        return
    rows, combos, bench = run(grid, args.fee_bps, args.train_frac, bars, symbol)
    render(rows, combos, bench, symbol, bars, args.fee_bps, args.train_frac)
    if args.save:
        import os
        best = rows[0]
        artifact = {"schema": "opt-report/0", "symbol": symbol,
                    "envelope": {"protocol": "single train/test split",
                                 "train_frac": args.train_frac,
                                 "grid_size": len(combos), "fee_bps": args.fee_bps,
                                 "test_only_once": True, "method": t("method")},
                    "source": source,
                    "rows": rows,
                    "leader": {k: best[k] for k in ("train_ret", "test_ret", "overfit_gap")},
                    "disclosure": "in-sample until proven otherwise; test window may be consulted once"}
        os.makedirs("opts", exist_ok=True)
        path = f"opts/{symbol.replace('/', '_')}-opt.json"
        json.dump(artifact, open(path, "w"), ensure_ascii=False, indent=1, default=str)
        print(f"→ {path}", file=sys.stderr)


if __name__ == "__main__":
    main()
