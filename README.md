# dsh-jesse — strategy optimization for DeepSeek Harness, with the overfit meter on

**Grid-sweep your strategy parameters on real data — then read the number that
most optimizers hide: the train→test overfit gap, with a multiple-testing
discount attached. The optimizer that tells you when it's lying to you.**
**在真实数据上扫策略参数——然后读出多数优化器不给你看的数字：train→test
过拟合缺口，附多重检验折减警示。会告诉你"我什么时候在骗你"的优化器。**

[![DeepSeek Harness](https://img.shields.io/badge/DSH-plugin-4E6DD4)](https://github.com/deepseek-ai) [![License: MIT](https://img.shields.io/badge/license-MIT-3da639)](LICENSE) [![Jesse MIT](https://img.shields.io/badge/concept-Jesse%20MIT-3da6da)](https://github.com/jesse-ai/jesse)

> Implements the core concept of [Jesse](https://github.com/jesse-ai/jesse)
> (8.8k★) — the optimization loop — natively for DSH, with anti-overfit
> discipline borrowed from the factor-research world. Not affiliated.
> Family: [dsh-TradingAgents](https://github.com/vicfei/dsh-TradingAgents) ·
> [dsh-nautilus_trader](https://github.com/vicfei/dsh-nautilus_trader) (engine) ·
> [dsh-hummingbot](https://github.com/vicfei/dsh-hummingbot) (MM) ·
> [dsh-OpenBB](https://github.com/vicfei/dsh-OpenBB) · [dsh-CCXT](https://github.com/vicfei/dsh-CCXT) ·
> [dsh-Vibe-Trading](https://github.com/vicfei/dsh-Vibe-Trading).

## Why (Jesse vs this vs the family's backtester)

| | Jesse (framework) | dsh-nautilus_trader (sibling) | **dsh-jesse** |
|---|---|---|---|
| Focus | accurate backtests + Optuna tuning | event-driven engine depth | **the tuning loop itself** |
| Runs where | Python lab | DSH tools | **DSH in-session** — agent sweeps params, reads the verdict |
| Anti-overfit | — | — | **train/test split + overfit-gap column + Bonferroni-style discount + test-only-once rule** |

## Quick start

```bash
git clone https://github.com/vicfei/dsh-jesse && cd dsh-jesse
python3 scripts/optimize.py --data <klines.json> \
  --grid '{"fast":[5,10,20],"slow":[30,60,90],"rsi_buy":[25,35]}' --fee_bps 5
```

Real smoke (binance BTC/USDT 365d, 2026-11-17): best train config −1.21% in a
**−30.6% train market** — but the table shows its **+2.96% overfit gap** and the
18-config multiple-testing discount. In a year where buy-and-hold lost a third,
trend-following cut the loss; the honest read is on the page.

## Status & roadmap

v0 grid optimizer smoke-tested on live data. [ROADMAP](ROADMAP.md): M1 Optuna
Bayesian search + walk-forward; M2 strategy DSL (Jesse-style lifecycle hooks).

## License & disclaimer

MIT; concept inspired by MIT upstream — no upstream code used. **Not investment
advice.** Optimization results are in-sample until proven otherwise.
