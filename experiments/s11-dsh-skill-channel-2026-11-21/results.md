# S11 skill 通道对照 · 结果（2026-11-22 运行，2026-11-21 预注册）

> 状态：A1 已执行并 checker 7/7；按预注册停止条件在 A1 后停止，B/A2 未运行。**已收口（2026-11-22 用户裁定接受环境负向结论，不再在隔离容器内做组件筛查）**。终裁（行为分/证据等级）待人工。

## 结论（一句话）

**假设 H 被拒绝**：在已过读取隔离的 Linux 隔离容器内把 skill 通道从「关」切到「开」，`skill` 工具确实出现，但交付仍为 7/7——skill 通道不是 S11 交付遗漏的必要原因。

## 实际运行的臂

| 臂 | run | skill | 观察工具 | checker | 说明 |
|---|---|---|---|---|---|
| A1 | 19 | 开启（`skills_state=enabled`） | 24（含 `skill`，`skill_tool_observed=true`） | **7/7** | 未复现 Windows 0/7 |
| B | — | 关闭 | — | — | 未运行（A1 已证伪） |
| A2 | — | 开启 | — | — | 未运行（A1 已证伪） |

## 关键证据

- run19 `execution_context_observed.tools` 含 `skill`（24 工具），`skills_state=enabled`，`configuration_evidence` 为 skill-on patch（无三行禁用）。证明 skill 通道**确实开启**，不是空工具。
- [checker_output.txt](../../Log-analyse/S-batch/S11-corrupt-recovery/dsh/run19/checker_output.txt)：7/7（result.md + error_report.md 均存在，保留 id=A1/A3/A5 无编造，指到 2 处损坏全命中）。
- 与 run16（skill 关，23 工具，7/7）对比：skill 开/关在隔离容器内**均 7/7**，切换无差别。
- 费用：`balance-before.json`=8.05 CNY，`balance-after.json`=8.05 CNY，单场 17s，无可见扣费（<0.01 元），远低于 ≤$5 上限。

## 归因边界（不越界表述）

- 本实验只排除了「skill 通道」这一个候选组件；不能由此推断 Windows 0/7 的具体原因。
- run11（Windows，24 工具含 skill，0/7）与 run19（Linux 容器，24 工具含 skill，7/7）**工具数相同、skill 都开启**，唯一差异仍在环境本身：OS（Windows pwsh vs Linux bash）、`context_policy`（headless_new_agent vs isolated_container）、宿主文件系统。
- 下一候选应按同一「固定模型+单组件干预」纪律在隔离容器内继续筛查，或单独研究 Windows headless 环境差异；不再回头用非隔离 Windows 场做付费对照。

## 现场登记

- 预注册：[preregistration.md](preregistration.md)（2026-11-21 冻结）
- 运行记录：[execution-01/results.json](execution-01/results.json)、[execution-01/manifest.json](execution-01/manifest.json)
- 归档：[run19](../../Log-analyse/S-batch/S11-corrupt-recovery/dsh/run19/)（artifact 7/7，adjudication=pending）
- 独立复核/行为分/终裁：待执行
