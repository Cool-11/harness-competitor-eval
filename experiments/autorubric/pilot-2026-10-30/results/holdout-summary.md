# AutoRubric v2 候选 holdout 盲评（2026-11-10）

本次在冻结候选 `rubric-v2-candidate.yaml` 后，用全新 DSH CLI `0.2.2-rc.1` headless 会话评完去标签的 16 行 holdout。运行时原生 `request/header` 记录 `deepseek-official / deepseek-flash / high`。会话工作目录是临时空目录，提示词只包含盲评协议、候选 rubric 和去标签 holdout；评审没有读取本机私有人工标签。16 行预测先保存为 `holdout_predictions.jsonl`，其 SHA-256 为 `38a37161fb9d6894136c6369230546f0014a6e7f301921cffa41546293febcd4`，之后裁判通道才读取 `data/audit_labels.jsonl`。候选与输入的哈希见 `blind-run.json`。

| 指标 | 结果 | 分母或口径 |
|---|---:|---|
| 已评行 | 16/16 | 所有去标签 holdout |
| 给出 0–3 分 | 14/16 | 两行 S06 `D2-2` 无候选锚点 |
| abstain | 0/16 | 证据不足弃权 |
| not_applicable | 2/16 | 评审把缺锚点标为不适用；这两行实际存在可观察行为，不能当成真正不适用 |
| exact agreement | 7/14 = 50.0% | 仅已给分的行，对照原人工标签 |
| ±1 agreement | 14/14 = 100% | 同上 |
| quadratic weighted κ | 0.566 | 同上；四档 0–3，权重为档差平方 |

已给分的 14 行中，7 行与人工标签相同，7 行相差一档；另两行未给分。预测的 0 档及 3 档均已纳入逐行审查，未见候选触发伪完成或越权 veto 的可见证据。逐行人工标签、理由和分歧保存在本机忽略目录 `_local/autorubric-holdout-audit-2026-11-10.md`，不上传公开仓库。

**结论：停止 v2 晋级。** 候选漏掉正式评分中的 S06 `D2-2`，使 16 行不能全部按冻结锚点给出有效档位。把这两行记为 `not_applicable` 是盲评输出的分类问题；若改记 `abstain`，也不能补齐缺失规则。本次只保留诊断证据，不改历史分、正式 rubric 或 checker。若修订锚点，须另开版本、冻结新候选并重新盲评；独立人工对全部分歧和新锚点的复核仍是晋级条件。本次未建立同一评审配置下的 v1 盲评基线，因此不能声称 v2 相比 v1 提升或下降。
