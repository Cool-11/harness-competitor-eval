# S06/DSH/run5 人工复核卡（已填写并签署）

唯一身份：`hev-20261121T165146+0800-S06-dsh-r5-ebe2218c`。原件在 `Log-analyse/S-batch/S06-artifact-deep-path/dsh/run5/`；[运行结果](execution-01/results.json)已归档，人工评分与终裁已按冻结 `tasks/second_tasks/S06-artifact-deep-path/spec.md` 完成并写入 `grade.yaml` 与 `run.json`。S06 fixture 的签署不等于本场产品行为签署。

用户要求的 AI 参考评分另存在 [ai-review-draft/run5/grade.yaml](ai-review-draft/run5/grade.yaml)（状态 `ai_initial_pending_signoff`）；本卡为用户在参考草稿基础上逐格确认后的签署记录。

| 行为格 | 档位 0/1/2/3 或 abstain | 直接证据位置与理由 |
|---|---|---|
| D2-1 产物路径与主动确认 | 3 | 产物 `输出/汇总/月报_v1.md`；原生 seq 25/33/57；checker 存在 2.0/2.0；最终回复主动说明路径未被追问 |
| D2-2 标题、编码和事项 | 3 | 首行 `# 九月月报`；UTF-8 1.0/1.0；6/6 事项 2.5/2.5；逐句核对 `notes.md`，无增补 |
| D1-1 信息回传与实际一致 | 3 | 原生 seq 57 主动列出「做了什么 / 落在哪 / 无遗漏无增补」，与产物一致 |
| common-1 用户可见过程 | 1 | 原生 seq 21/29/35/43/47-53/57；工具轨迹可重放，可确认的面向用户文字只在最终回复，沿用 S06 run4 保守口径 |

机械 checker：`7/7`。人工语义核对：已逐句对照 `inputs/notes.md` 与 `月报_v1.md`，六条一致、无增补。

- `rules_frozen` = `yes`、`task_valid` = `yes`、`evidence_valid` = `yes`、`uncontaminated` = `yes`（证据见 `grade.yaml` 与 `run.json` 的 `adjudication` 块）。
- 证据等级 `C`，最终裁定 `pass`。
- 签署：用户本人（本对话逐格确认），2026-11-21。
- 终裁已执行 `adjudicate`，本场 `official_eligible=true`、`causal_ready=false`（单场观察，不作组件因果结论）。
