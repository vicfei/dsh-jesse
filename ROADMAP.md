# ROADMAP — dsh-jesse

北极星：八仓家族的调参引擎，吃 Jesse 8.8k★ 流量，30 天 100–300★。
命名全表面：GitHub=dsh-jesse（镜像上游小写仓名 `jesse`）、npm=dsh-jesse（同名）。
家族分工：nautilus_trader=回测引擎深度，本仓=优化循环与防过拟合纪律。

## 里程碑

### M0 ✅（2026-11-17）
网格优化器（费感知回测评价 + train/test 切分 + 过拟合缺口列 + 多重检验
警示 + test-only-once 规则）。真实冒烟：BTC 365d 18 组参数——train 榜首
-1.21%（train 市场 -30.6%）但缺口 +2.96% 如实呈现。

### M0.5 · 发布包
- [ ] README 打磨 + 冒烟表截图 + npm 0.0.1 占位（owner 手动）
- [ ] 公开仓 topics + 八仓互链 + marketplace + 渠道

### M1 · 搜索深度（第 2-3 周）
- [ ] Optuna 贝叶斯搜索（早停+预算护栏）
- [ ] walk-forward 滚动验证（多段切分，替代单次 70/30）
- [ ] 评价后端可选接 dsh-nautilus_trader 桥（事件驱动撮合升级 bar 级评价）

### M2 · 策略 DSL（第 4-6 周）
- [ ] Jesse 式策略生命周期 DSL（should_long/on_update 钩子，配置化）
- [ ] 与家族互通：优化产物一键生成 nautilus 策略模板 / 议院数据卡

### M3 · 生态（第 2 月起）
- [ ] 优化报告标准化（OPT-REPORT spec，与 IC-MEMO/RESEARCH-TRAIL 会师）
- [ ] 公共参数库（按市场状态分组的先验区间）

## 纪律（不可让话）

- 过拟合缺口与多重检验警示不可从报告剥离；
- test 段只许看一次的规则写进输出本身；
- in-sample 结果不得当作预测表述；不做投资建议。
