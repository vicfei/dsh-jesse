# PR body（提交 awesome-dsh-plugin 用——owner 发布 npm 0.2.0 后执行）

**Adds vicfei/dsh-jesse — strategy optimization with the overfit meter on (tools)**

One file added: `data/plugins/vicfei__dsh-jesse--npm.yml`.

- Install: `dsh plugin add dsh-jesse` (npm 0.2.0; dsh.bundle + skill + CLI
  spawning the stdlib-only Python engine)
- What it does: grid and walk-forward parameter sweeps with fee-aware
  backtests where **the overfit gap, multiple-testing discount and
  test-only-once rule are stated in the output itself**; a stdlib
  significance engine — random-entry bootstrap verdicts ("reject noisy
  parameters before they cost you") and dual-mode Monte Carlo light with
  mode disagreement reported as-is; and **the family objective bridge**:
  consume dsh-Kronos scenario artifacts as fitness, ranking parameter sets
  by worst-of-bracket across P10/P50/P90 — an interop upstream cannot have.
- Positioning: the zero-dependency complement to upstream jesse (the heavy
  full platform); the README table says so explicitly.
- Real working code: 21 hermetic checks + CI green; live smokes on real BTC
  data throughout. Concept seat of jesse-ai/jesse (MIT upstream, no upstream
  code). Not investment advice. Family: dsh-TradingAgents · dsh-Kronos ·
  dsh-nautilus_trader …

PR 执行命令（owner 在 npm 0.2.0 发布后跑）：

```bash
cd /tmp && git clone --depth 1 git@ssh.github.com:vicfei/awesome-dsh-plugin.git && cd awesome-dsh-plugin
git checkout -b add-dsh-jesse
cp ~/dsh-jesse/docs/marketplace-submission/vicfei__dsh-jesse--npm.yml data/plugins/
git add data/plugins/vicfei__dsh-jesse--npm.yml
git commit -m "Add vicfei/dsh-jesse (strategy optimization with the overfit meter)"
git push -f origin add-dsh-jesse
# 开 PR：base awesome-dsh-plugin/awesome-dsh-plugin ← vicfei:add-dsh-jesse，body 用上文
```
