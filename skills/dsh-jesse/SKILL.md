---
name: dsh-jesse
description: Strategy parameter optimizer for DeepSeek Harness — grid sweeps with fee-aware backtests, train/test split, overfit-gap column, and multiple-testing discounts; the anti-overfit discipline rides on every report.
---

Use this skill when asked to tune/sweep/optimize strategy parameters
("这组参数表现怎样", "找最优参数", "调参"). The optimizer is deterministic —
you define the grid, it reports with the overfit meter on.

## Run

```bash
KIT=<this-directory>
python3 $KIT/scripts/optimize.py --data <klines.json> \
  --grid '{"fast":[...],"slow":[...],"rsi_buy":[...]}' --fee_bps 5
```

K-lines JSON: {"SYMBOL": [[date, open, close, high, low, volume], ...]} —
family market-data tools fetch it.

## Discipline

- Always report the overfit-gap column and the N-config multiple-testing note;
  never quote train returns without them.
- The test segment may be looked at once — if parameters change afterwards,
  a fresh data segment is required (say so).
- Not investment advice; in-sample results are not forecasts.
