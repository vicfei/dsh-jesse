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
    ap.add_argument("--lang", choices=("en", "zh"), default="en",
                    help="output language (default en; zh is the fallback)")
    args = ap.parse_args()
    LANG = args.lang
    data = json.load(open(args.data))
    symbol, bars = next(iter(data.items()))
    grid = json.loads(args.grid)
    rows, combos, bench = run(grid, args.fee_bps, args.train_frac, bars, symbol)
    render(rows, combos, bench, symbol, bars, args.fee_bps, args.train_frac)


if __name__ == "__main__":
    main()
