# S11/DSH/run16 与 run17 人工签认记录（2026-11-20）

本文件记录用户在本对话对[AI 参考初评](ai-review-draft/README.md)的明确确认。用户原话：

> run16和run17 分数为3/3/3/1 3/3/3/1 门槛均为yes 证据等级为B 并且裁定为pass

依照签认前已经列明的顺序，两个 `3/3/3/1` 均对应 `D3-1 / D7-1 / D1-1 / common-1`。四项门槛均为 `rules_frozen=yes`、`task_valid=yes`、`evidence_valid=yes`、`uncontaminated=yes`。两个运行的证据等级均登记为用户确认的 **B**，终裁均为 `pass`。AI 初评中的档位和证据理由未被用户改动；证据位置见各场新 `grade.yaml`。按 S11 四格各 1.5 分的冻结口径，行为分各 5.0/6，机械 7/7 折为产物 4.0/4，单题各 9.0/10。

签认身份登记为“用户本人（本对话逐格确认）”。用户未在本条消息披露是否参与原题、checker、rubric 或旧评分制作，也未提供独立评委关系声明，因此**不能把本次作者签认计入独立 20 格复评**。`B` 是本次用户确认的运行证据等级，不能读成旧版“裸模型探针成功所以 Harness 负责”的推断；[现行归因规则](../../docs/41-归因与研究轨道现行规则-2026-11-20.md)要求实际生效的受控对照。run17 的 gate 未触发，本签认不补成组件修复效果或因果反转。

原[空白 run16 卡](run16-human-review-card.md)、[空白 run17 卡](run17-human-review-card.md)、[AI 初评](ai-review-draft/README.md)、运行前登记和产品原始现场均保留。执行终裁前的 `run.json`、`score.json` 快照另存到 `adjudication-01/prestate/`；正式终裁在各场现行 `run.json` / `score.json` 中登记，由独立派生目录生成新报告，不改旧快照。
