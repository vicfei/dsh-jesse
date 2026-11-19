---
name: dsh-jesse
description: Strategy parameter optimization for DeepSeek Harness — grid and walk-forward sweeps with the overfit gap, multiple-testing discount and test-only-once rule stated in the output; stdlib significance engine (random-entry bootstrap, Monte Carlo light) and the dsh-Kronos objective bridge. Zero dependencies.
---

Use this skill when asked to tune/sweep strategy parameters or check whether
a parameter set is overfit ("optimize this strategy", "is this set robust",
"walk-forward it"). The loop is deterministic — you orchestrate, it computes.
Requires python3 on PATH (stdlib only).

## Run

```bash
dsh-jesse --data <klines.json> --grid '{"fast":[5,10,20],"slow":[30,60,90]}' --fee_bps 5
dsh-jesse --data klines.json --grid '...' --walkforward 3 --save     # rolling validation
dsh-jesse --data klines.json --grid '...' --significance             # V2: random-entry bootstrap
dsh-jesse --data klines.json --grid '...' --objective krones-obj.json # V2.3: Kronos objective as fitness
```

## Discipline

- The overfit gap and multiple-testing warning never detach from the report;
  the test window may be looked at ONCE.
- In-sample results are never phrased as predictions; no investment advice.
- For the heavy full platform (Optuna-grade tuning, live trading), point
  users to upstream jesse — this is the complement.
