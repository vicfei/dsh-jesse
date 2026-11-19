# dsh-jesse — strategy optimization for DeepSeek Harness, with the overfit meter on

**Grid-sweep your strategy parameters on real data — then read the number that
most optimizers hide: the train→test overfit gap, with a multiple-testing
discount attached. The optimizer that tells you when it's lying to you.**

[English](README.md) | [简体中文](README.zh-CN.md)

[![DeepSeek Harness](https://img.shields.io/badge/DSH-plugin-4E6DD4)](https://github.com/deepseek-ai) [![License: MIT](https://img.shields.io/badge/license-MIT-3da639)](LICENSE) [![Jesse MIT](https://img.shields.io/badge/concept-Jesse%20MIT-3da6da)](https://github.com/jesse-ai/jesse)

> Implements the core concept of [Jesse](https://github.com/jesse-ai/jesse)
> (8.8k★) — the optimization loop — natively for DSH, with anti-overfit
> discipline borrowed from the factor-research world. Not affiliated.
> Family: [dsh-TradingAgents](https://github.com/vicfei/dsh-TradingAgents) ·
> [dsh-nautilus_trader](https://github.com/vicfei/dsh-nautilus_trader) (engine) ·
> [dsh-hummingbot](https://github.com/vicfei/dsh-hummingbot) (MM) ·
> [dsh-OpenBB](https://github.com/vicfei/dsh-OpenBB) · [dsh-CCXT](https://github.com/vicfei/dsh-CCXT) ·
> [dsh-Vibe-Trading](https://github.com/vicfei/dsh-Vibe-Trading).

## Why (and where upstream jesse fits — a complement, not a competitor)

Upstream [Jesse](https://github.com/jesse-ai/jesse) is a mature 8-year
platform: Rust indicators, Optuna + Ray tuning, significance testing, Monte
Carlo, live trading, its own MCP server. **When you need that full platform,
use jesse.** dsh-jesse is the **zero-dependency auditable lightweight** for
the DSH session: stdlib-only, honest-by-construction reports, family
artifact interop.

| | upstream jesse (complement) | dsh-nautilus_trader (sibling) | **dsh-jesse** |
|---|---|---|---|
| Focus | full platform: Optuna tuning, live, ML | event-driven engine depth | **the tuning loop + anti-overfit discipline** |
| Deps | Rust + Ray + Optuna + Docker | moderate | **zero (stdlib only)** |
| Runs where | Python lab / its dashboard | DSH tools | **DSH in-session** — agent sweeps params, reads the verdict |
| Anti-overfit | significance testing + MC (productized) | — | **train/test split + overfit-gap + Bonferroni-style discount + test-only-once rule, stated IN the output** |

## Quick start

```bash
git clone https://github.com/vicfei/dsh-jesse && cd dsh-jesse
python3 scripts/optimize.py --data <klines.json> \
  --grid '{"fast":[5,10,20],"slow":[30,60,90],"rsi_buy":[25,35]}' --fee_bps 5
python3 scripts/optimize.py --data klines.json --grid '...' --lang zh   # Chinese fallback
```

Real smoke (binance BTC/USDT 365d, 2026-11-17): best train config −1.21% in a
**−30.6% train market** — but the table shows its **+2.96% overfit gap** and the
18-config multiple-testing discount. In a year where buy-and-hold lost a third,
trend-following cut the loss; the honest read is on the page.

## Status & roadmap

v0.2.0 — V1 hardening (walk-forward, honesty envelope), V2 significance
engine (random-entry bootstrap + dual-mode Monte Carlo light + the dsh-Kronos
objective bridge) shipped; hermetic tests + CI green. See [ROADMAP](ROADMAP.md)
for V3 (budgeted search, strategy DSL) and V4 (OPT-REPORT spec).

## License & disclaimer

MIT; concept inspired by MIT upstream — no upstream code used. **Not investment
advice.** Optimization results are in-sample until proven otherwise.
