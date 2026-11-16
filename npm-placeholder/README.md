# dsh-jesse

> Strategy parameter optimization, natively on DeepSeek Harness: grid-sweep on
> real data, then read what most optimizers hide — **the train→test overfit gap
> with a multiple-testing discount attached. The optimizer that tells you when
> it's lying to you.**
>
> Implements the core concept of [Jesse](https://github.com/jesse-ai/jesse);
> independent community project, not affiliated.

**Status: name reserved — first release in development.**

Engine and docs: https://github.com/vicfei/dsh-jesse

- Fee-aware grid sweeps (SMA-cross + RSI-filter strategies, more in M1)
- Anti-overfit trio: train/test split, overfit-gap column, test-only-once rule
- M1: Optuna Bayesian search + walk-forward; M2: Jesse-style strategy DSL
- Not investment advice.

---

**发布记录**：2026-11-17 owner 手动 `npm publish` 成功，latest=0.0.1，官方+镜像双验证。0.0.0-stage 为 staged-publishing 工件。
