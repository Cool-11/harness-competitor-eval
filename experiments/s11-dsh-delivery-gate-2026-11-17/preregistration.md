# S11 × DSH 外部交付前检查：机制筛查预注册（2026-11-17）

## 研究问题与边界

旧 S11 × `tool-pwsh` A1/B/A2 三臂均缺 `result.md`、`error_report.md`，关闭 PowerShell 工具未修复交付。此次改测完成前的文件落点检查。处理是**外部监督包装器**：截留 DSH headless 首次终答，只按冻结题面检查工作区根目录的两个文件是否存在且非空；若缺失，使用该场的 `--session-id` 向同一会话反馈缺失文件名，最多续接一轮；最后收集原生 session 和产物。它不属于 DSH 官方内置插件，也不代写文件。

本试验只筛查“检查 + 指明缺失文件 + 一次修复机会”这整个 Harness 组件。若处理臂改善，不能单独归因于文件名反馈、额外模型轮次或某个内部决策；若要拆开，下一版应加等预算的通用续接臂。三场各一次，不估计稳定成功率、置信区间，也不升级仓库的 `A_same_model_cli` 正式因果配对。

## 运行前冻结的处理与判据

| 项 | A1 默认 r13 | B 检查 r14 | A2 默认 r15 |
|---|---|---|---|
| DSH 首次调用 | `headless`，原版 S11 prompt 和 inputs | 完全相同 | 完全相同 |
| 包装器 | 同一 `cli_batch.py` | 同一 `cli_batch.py` | 同一 `cli_batch.py` |
| 唯一处理 | 不启用 `delivery_gate` | `required_files=[result.md,error_report.md]`；缺失或空文件时反馈一次 | 不启用 `delivery_gate` |
| 后续调用 | 无 | 仅缺失、首轮正常完成且原生 session 身份唯一时，`--session-id` 同会话续接一次 | 无 |

主终点为**最终**工作区根目录的 `result.md`、`error_report.md` 均存在且通过冻结 S11 checker；另报 0–7 原始分、初次文件状态、修复后状态、额外轮次和最终声明。检查本身仅查文件名、根目录和非空，**不运行 checker，不读 `spec.md`、`truth.json`，不把这些裁判文件投喂给产品**。若 B 只是写出非空错误文件而 checker 仍失败，记失败。

固定 DSH CLI `0.2.2-rc.1`、`headless`、`deepseek-official/deepseek-flash/high/provider_default`、`workspace-write`、`approval-policy never`、默认 `tool-pwsh` 与 `tool-fs`、同一账号、同一 Windows 环境、600 秒单轮上限。当前进程无 `DEEPSEEK_API_KEY` 环境变量，A/B/A2 均加同一[凭据补丁](../../scripts/patches/s11-gate-shared-headless-auth.yml)恢复 DSH 已保存的凭据服务；不读取或归档凭据值。此共同条件与上一轮 S11 现场的凭据来源不同，旧场不并入本次处理效应。每场独立新工作区，输入仅来自 `tasks/second_tasks/S11-corrupt-recovery/inputs/`；首轮题面逐字不改。Skills 顶层名称固定检查，内容和模型实际读取范围仍是限制；Memory 状态记录为 unknown。三份计划在首次调用前写定，使用新 run13/14/15，禁止覆盖旧场。

## 顺序、无效与停止

1. 先运行 A1。若 A1 已通过主终点，停止，不把此前失败当作当前反事实。
2. A1 失败再运行 B。若 B 首轮就通过，记录无检查触发，不能归因于 gate；若 session 无法唯一定位、cwd/模型/工具列表变化、续接成为新会话或 checker/真值进入工作区，保留现场并标 `invalid/unknown`，停止。
3. 只有 B 在 gate 触发后通过主终点，才运行 A2 检查恢复臂；若 B 未改善，停止并记录阴性结果，不为追求成功追加提示或改规则。

每场均 `prepare → 产品调用 → collect → 人工 adjudicate`。包装器留存首次终答、续接反馈、续接答复、原生 session、调用返回码、cwd、工具/模型请求、产物和哈希。A1/B/A2 若呈失败→成功→失败，只支持这组三次机制线索；需另开预注册独立重复和等预算对照才能估计效果。B 若最终失败，优先转向其他交付契约机制，不回写旧场或冻结 checker。
