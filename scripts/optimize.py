#!/usr/bin/env python3
"""策略参数优化器（jesse 核心概念的原生实现，M0）

上游 Jesse（8.8k★，MIT）的招牌是"极准确的加密回测 + Optuna 参数优化"。
本插件 v0 原生实现其**优化循环**：参数网格扫描 + 费感知回测评价 +
**防过拟合三件套**（家族纪律，比原版更严）：
1. train/test 时序切分（默认 70/30）：train 选参，test 出真成绩
2. 过拟合缺口列（train-test 收益差）随表输出
3. 多重检验视角：扫了 N 组参数=做了 N 次尝试，附 Bonferroni 式警示
   （因子鉴真 G3 同源思想——挑出来的最优参数，其显著性要打折看）

策略 v0：SMA 交叉 + 可选 RSI 过滤（参数化，纯确定性评价）。

用法：
  python3 scripts/optimize.py --data /tmp/btc_365.json \
      --grid '{"fast":[5,10,20],"slow":[30,60,90],"rsi_buy":[25,35]}' --fee_bps 5
"""
import argparse, datetime as dt, itertools, json, sys


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
    for i in range(1, len(bars)):
        if f[i] is None or s[i] is None: continue
        long_ok = f[i] > s[i] and (rsi_buy is None or (r[i] is not None and r[i] < rsi_buy + 50))
        if pos == 0 and long_ok:
            pos, entry, trades = 1, closes[i] * (1 + fee), trades + 1
            cash -= entry
        elif pos == 1 and f[i] < s[i]:
            cash += closes[i] * (1 - fee); pos = 0
    final = cash + (closes[-1] * (1 - fee) if pos == 1 else 0)
    return final / initial - 1, trades


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--grid", required=True)
    ap.add_argument("--fee_bps", type=float, default=5.0)
    ap.add_argument("--train_frac", type=float, default=0.7)
    args = ap.parse_args()
    data = json.load(open(args.data))
    symbol, bars = next(iter(data.items()))
    grid = json.loads(args.grid)
    cut = int(len(bars) * args.train_frac)
    train, test = bars[:cut], bars[cut:]
    bh_train = train[-1][2] / train[0][2] - 1
    bh_test = test[-1][2] / test[0][2] - 1

    keys = list(grid)
    combos = list(itertools.product(*[grid[k] for k in keys]))
    rows = []
    for combo in combos:
        p = dict(zip(keys, combo))
        r_tr, n_tr = backtest(train, p.get("fast", 20), p.get("slow", 60), p.get("rsi_buy"), args.fee_bps)
        r_te, _ = backtest(test, p.get("fast", 20), p.get("slow", 60), p.get("rsi_buy"), args.fee_bps)
        rows.append({**p, "train_ret": round(r_tr, 4), "test_ret": round(r_te, 4),
                     "overfit_gap": round(r_tr - r_te, 4), "train_trades": n_tr})
    rows.sort(key=lambda r: -r["train_ret"])

    print(f"## 参数优化 · {symbol} · {len(bars)} bars（train {len(train)}/{len(test)} 切分 {args.train_frac:.0%}）")
    print(f"基准：train 买入持有 {bh_train:+.2%} · test 买入持有 {bh_test:+.2%}\n")
    print("| fast | slow | rsi_buy | train_ret | test_ret | overfit_gap | trades |")
    print("|---|---|---|---|---|---|---|")
    for r in rows[:8]:
        print(f"| {r['fast']} | {r['slow']} | {r.get('rsi_buy', '—')} | "
              f"{r['train_ret']:+.2%} | {r['test_ret']:+.2%} | {r['overfit_gap']:+.2%} | {r['train_trades']} |")
    best = rows[0]
    n = len(combos)
    print(f"""
## 多重检验警示（家族纪律，因子鉴真 G3 同源）
- 共扫描 **{n}** 组参数=做了 {n} 次尝试。train 榜首 {best['train_ret']:+.2%} 的显著性
  须按多重检验折减看待（Bonferroni 直觉：α/{n}）。
- 过拟合缺口：榜首 train-test 差 **{best['overfit_gap']:+.2%}**——缺口越大，越像
  在拟合 train 的噪声而非结构。
- test 段只许看一次：若据此回头调参再验，test 已被污染，需换新数据段。

---
*engine: grid-optimizer v0 · fee {args.fee_bps}bps · bar 级执行 · span {bars[0][0]} → {bars[-1][0]} · 非投资建议*
*ran at {dt.datetime.now().isoformat(timespec='seconds')}*""")


if __name__ == "__main__":
    main()
