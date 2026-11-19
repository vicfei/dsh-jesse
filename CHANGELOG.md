# Changelog

## 0.2.0 (2026-11-20) — first release: hardening + the significance engine

The V1–V2 line ships as one release (registry jumps placeholder → 0.2.0).

### Hardening (V1)
- English-first with `--lang zh` fallback; the comparison table places
  upstream jesse as the complement, not a competitor.
- Honesty envelope: `--save` audit artifacts (schema opt-report/0) carry
  {protocol, split/segments, grid_size, fee_bps, test_only_once, method};
  pre-flight refusals with reasons; source metadata (coverage gaps) rides.
- **Walk-forward validation** (`--walkforward N`): each segment's train picks
  params, its own test scores them; chained return vs buy&hold; drift framed
  as information; honest lookback note when segments are shorter than the
  grid's longest lookback.

### The significance engine (V2)
- **Rule significance, stdlib edition**: strategy return vs random-entry
  bootstrap on the same history (same trade count; disclosed hold menu);
  one-sided percentile + three-way honest verdict.
- **Monte Carlo light, dual mode (always together)**: trade-order shuffling
  (states the permutation-invariance honestly — sequencing risk is drawdown)
  + block-resampled candles (P10/P50/P90, profitable fraction); mode
  disagreement reported as-is.
- **The family objective bridge** (`--objective`): consume dsh-Kronos
  `--objective-out` artifacts — terminal quantiles become scenario paths,
  every combo is ranked by worst-of-bracket. The interop upstream cannot
  have; scenarios are not predictions, disclosed throughout.

### Packaging
- npm bin + DSH bundle + skill; 21 hermetic checks + CI.

## 0.0.1
Name placeholder.
