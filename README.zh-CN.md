# dsh-jesse — DeepSeek Harness 的策略优化，带过拟合仪表

**在真实数据上扫策略参数——然后读出多数优化器不给你看的数字：train→test
过拟合缺口，附多重检验折减警示。会告诉你"我什么时候在骗你"的优化器。**

[English](README.md) | [简体中文](README.zh-CN.md)

[![DeepSeek Harness](https://img.shields.io/badge/DSH-plugin-4E6DD4)](https://github.com/deepseek-ai) [![License: MIT](https://img.shields.io/badge/license-MIT-3da639)](LICENSE) [![Jesse MIT](https://img.shields.io/badge/concept-Jesse%20MIT-3a6cda)](https://github.com/jesse-ai/jesse)

> 原生实现 [Jesse](https://github.com/jesse-ai/jesse)（8.8k★）的核心概念——
> 优化循环——并叠加因子研究界的防过拟合纪律。无隶属。
> 家族：[dsh-TradingAgents](https://github.com/vicfei/dsh-TradingAgents) ·
> [dsh-nautilus_trader](https://github.com/vicfei/dsh-nautilus_trader)（引擎）·
> [dsh-hummingbot](https://github.com/vicfei/dsh-hummingbot)（做市）·
> [dsh-Vibe-Trading](https://github.com/vicfei/dsh-Vibe-Trading)。

## 定位（上游 jesse 是互补，不是对手）

上游 Jesse 是成熟的 8 年平台（Rust 指标/Optuna+Ray 调参/显著性检验/
Monte Carlo/实盘/自带 MCP）。**需要完整平台时请用 jesse。** dsh-jesse 是
DSH 会话里的**零依赖可审计轻量版**：纯标准库、诚实构造的报告、家族工件互通。

| | 上游 jesse（互补） | dsh-nautilus_trader（兄弟仓） | **dsh-jesse** |
|---|---|---|---|
| 焦点 | 完整平台：Optuna 调参/实盘/ML | 事件驱动引擎深度 | **调参循环+防过拟合纪律** |
| 依赖 | Rust+Ray+Optuna+Docker | 中等 | **零（纯标准库）** |
| 运行处 | Python 实验室/自带面板 | DSH tools | **DSH 会话内**——agent 扫参读判词 |
| 防过拟合 | 显著性检验+MC（已产品化） | — | **train/test 切分+过拟合缺口+Bonferroni 折减+test-only-once，写在输出里** |

## 快速开始

```bash
git clone https://github.com/vicfei/dsh-jesse && cd dsh-jesse
python3 scripts/optimize.py --data <klines.json> \
  --grid '{"fast":[5,10,20],"slow":[30,60,90],"rsi_buy":[25,35]}' --fee_bps 5
```

真实冒烟（binance BTC/USDT 365 天，2026-11-17）：train 最优 -1.21%，发生在
**train 市场 -30.6%** 里——但表格同时给出它的 **+2.96% 过拟合缺口**与 18 组
参数的多重检验折减。买入持有亏三分之一的年份里趋势跟随砍掉了亏损；诚实的
读法就在页面上。

## 许可与免责

MIT；概念致谢 MIT 上游——零上游代码。**非投资建议。**
优化结果在证明之前都算样本内。
