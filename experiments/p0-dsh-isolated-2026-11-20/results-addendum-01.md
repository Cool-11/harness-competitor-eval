# P0 追加 C1 结果：同题回归观察（2026-11-20）

> 后续用户签认与终裁见[结果包](adjudication-01/results.md)。本页的 `pending` 和准入计数只对应签认前快照。

本页接续[原筛查结果](results.md)，执行的是用户随后选择的[同题追加路径](preregistration-addendum-01.md)。原预注册与 run16 停止决定保持原样；本场不是在原实验中补填未运行臂。

| 配置 | 运行身份 | 首次交付 | 外部 gate | checker | 人工终裁 |
|---|---|---|---|---|---|
| 既有 C0，run16 | `hev-20261120T214236+0800-S11-dsh-r16-36035514` | 两份文件齐全 | 未启用 | 7/7 | pending |
| 追加 C1，run17 | `hev-20261120T221915+0800-S11-dsh-r17-b058e4a8` | 两份文件齐全 | 已启用但**未触发**，无同会话续接 | 7/7 | pending |

run17 用独立 `prepare → 产品调用 → collect`，DSH 实际 `deepseek-official/deepseek-flash/high/provider_default`，原生 cwd 为 `/work`，单场约 16.26 秒；运行时配置快照与 run16 的 merged config **字节一致**。C1 的差异是 DSH 外部交付检查的启用状态，不在 DSH patch 内。两场都是 Linux 新容器、空工作区和空 DSH_HOME，不能与旧 Windows 场视为同环境反事实。

[run17 原始归档](../../Log-analyse/S-batch/S11-corrupt-recovery/dsh/run17/)保存产物、checker、运行身份和[原生会话](../../Log-analyse/S-batch/S11-corrupt-recovery/dsh/run17/evidence/session_export/session.v4.jsonl.zstd)。[补充现场](execution-02/evidence/run17/)保存隔离检查、merged config、stdout/stderr 和原生 session；[逐文件哈希](execution-02/runtime-evidence-manifest.json)列出 7 份文件。工具事件见[索引](execution-02/tool-trace.json)。人工行为与终裁请用[run16 卡](run16-human-review-card.md)和[run17 卡](run17-human-review-card.md)核看原件后签署，当前不得声称签署已完成。

## 预算、统计单位与日志限制

两场独立产品运行，共 18 次 provider messages 请求。run16 的保守预留 `¥1.57044` 被带入新代理；run17 新增预留 `¥1.396282`，累计上界 **`¥2.966722` < 用户限额 `¥5`**。run17 结束用量事件汇总为输入 1,922、缓存读 51,584、输出 1,885 tokens，按冻结高峰费率估计约 `¥0.02098736`；两场估计合计 `¥0.06916632`，均不是结算账单。run17 调用前后查询余额均为 `¥8.07`，不据此宣布免费或精确扣费。详见[用量与终点](execution-02/usage-and-outcome.json)及[预算原始日志](execution-02/budget.jsonl)。

预算代理对转发前预留使用全局累计数，限额仍有效。run17 开头两个并发请求在**响应/用量日志**里共用了 `call=2` 标签，故这两条的逐请求用量归属不可唯一还原；9 个预留事件和 9 个结束用量事件仍可分别计数，汇总按结束用量事件计算。此限制不应被隐去或误报为逐请求精确账单。

## 结论与剩余验收

本配置下两场均机械完成，追加 C1 **没有观察到交付回归**。由于 run16 未失败、run17 的 gate 未触发，处理变量没有进入 Agent 决策，不能估计交付检查的修复效应，也不能完成“失败→改件成功→恢复失败”闭环。每臂 n=1，不能宣称稳定性。原 Windows P2 阴性结果和旧受污染场保持原判。

人工复核可以决定各场语义/行为分和正式准入，但即便两场都签为 pass，也不把未激活的 gate 变成有效干预。独立 20 格评委复评、S06/S11 语义校准签署与真正可触发故障的三臂机制案例仍需另行完成。当前正式比较快照 **16 纳入、27 排除或待裁**；核心观察 37 场、正式 16 场、10/10 产品格，pending 12。见[正式表](execution-02/report/formal-results.json)与[覆盖快照](execution-02/report/coverage.json)。
