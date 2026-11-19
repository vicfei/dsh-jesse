# ROADMAP — dsh-jesse

North star: the family's parameter-optimization seat, riding the Jesse 8.8k★
gravity, 100–300★ in 30 days. Naming on all surfaces: GitHub = dsh-jesse
(mirrors the upstream lowercase name) / npm = dsh-jesse. Family division:
dsh-nautilus_trader = backtest-engine depth; this repo = the optimization
loop and anti-overfitting discipline.

## Positioning discipline (this repo's own)

Upstream [Jesse](https://github.com/jesse-ai/jesse) is an 8-year, actively
maintained, commercially backed platform that has already productized
**bootstrap rule-significance testing**, **dual-mode Monte Carlo**, and a
**local MCP server** for AI assistants. Head-on feature competition is
unwinnable and unnecessary. This repo is the **zero-dependency auditable
lightweight**: stdlib-only, honest-by-construction reports, family-artifact
interop (dsh-Kronos objective files as fitness), upstream in the README as a
**complement** (the heavy full-platform), never a competitor.

**Competitive read (2026-11-20 deep-dive, issue #1)**: their "reject noisy
ideas early" language and dual-mode MC validate the family's G3 lineage — we
ship the slim stdlib edition of the same discipline, plus the family bridge
upstream cannot have.

## Milestones

### M0 ✅ (2026-11-17)
Grid optimizer (fee-aware backtest evaluation + train/test split + overfit
gap column + multiple-testing warning + test-only-once rule). Real smoke:
BTC 365d, 18 parameter sets — train leader -1.21% (train market -30.6%)
with the +2.96% gap shown as-is.

### V1 · Hardening + release train ✅ (2026-11-20)
- [x] V1.1 EN-first: engine output via i18n table (en default, `--lang zh`
      fallback); README pure EN + `README.zh-CN.md`; the comparison table
      places upstream jesse as the complement
- [x] V1.2 honesty systematization: report envelope {protocol, split,
      grid_size N → multiple-testing note, test-only-once stated in the
      output itself}; unavailable-with-reason on insufficient windows
- [x] V1.3 source metadata rides: data origin/date-range/bars/coverage gaps
- [x] V1.4 **walk-forward validation**: rolling multi-segment split replaces
      the single 70/30; per-segment stability column (best-param drift);
      walk-forward efficiency reported honestly
- [x] V1.5 release train: root package (bin, dsh.bundle + skill, hermetic
      tests + CI, `scripts/*.py` glob); owner publish; awesome-dsh submission

### V2 · The significance engine ✅ (2026-11-20 → npm 0.2.0)
- [x] V2.1 **rule significance testing, stdlib edition**: random-entry
      bootstrap distribution vs the strategy on the same history — "reject
      noisy ideas early" (G3 / factor-auth lineage)
- [x] V2.2 **Monte Carlo light, dual mode**: trade-order shuffling +
      block-resampled candles (slim inline block bootstrap; no external deps)
- [x] V2.3 **the family objective bridge**: consume dsh-Kronos
      `--objective-out` files as fitness targets (optimize P_above / fan
      width — distribution metrics, not point values) — the interop upstream
      cannot have

### V3 · Search depth + strategy DSL (0.3.x)
- [ ] V3.1 budgeted random search with adaptive narrowing (stdlib; honest
      framing: Optuna-grade tuning belongs to upstream jesse)
- [ ] V3.2 strategy lifecycle DSL (config-defined hooks) + nautilus template
      export (one-directional, no sibling repo changes)
- [ ] V3.3 optional evaluation backend bridge (subprocess/file protocol to
      dsh-nautilus_trader; bar-level default stays stdlib)

### V4 · Ecosystem (0.4.x)
- [ ] OPT-REPORT spec (family format; joins IC-MEMO / RESEARCH-TRAIL /
      SCENARIO-REPORT)
- [ ] parameter prior library grouped by market regime (disclosed priors)
- [ ] monthly incumbent digest (an active incumbent must be watched, not
      assumed static)

## Star strategy

1. Name = traffic (`jesse`); topics carry dsh/dsh-plugin (auto-curated lists).
2. Hook: **"reject noisy parameters before they cost you — walk-forward +
   significance, zero dependencies"**; the Kronos objective bridge is hook #2.
3. The overfit-gap table is post-ready; the significance verdict doubles it.
4. awesome-dsh submission after npm 0.1.0; family same-day combo discipline.

## Discipline (non-negotiable)

- The overfit gap and multiple-testing warning never detach from the report.
- The test-only-once rule is written into the output itself.
- In-sample results are never phrased as predictions; no investment advice.
