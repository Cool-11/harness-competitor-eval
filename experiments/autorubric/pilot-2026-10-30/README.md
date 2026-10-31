# AutoRubric pilot · 2026-10-30

状态：`discovery_only_not_for_official_scoring`。

本目录用已签署的 S06/S11 行为格探索更清晰的 rubric 锚点。它不调用产品、不修改 checker、不回写历史分，也不构成正式 rubric 变更。

## 固定配置

- 生成器：`gpt-6-sol`，reasoning `medium`；不可用时以独立实验改用 `gpt-5.6-sol`，不得混样。
- 数据拆分：完整 run 为最小分组；每题 3 dev / 2 holdout。
- 生成器可见：dev 中的任务、criterion、可观察证据和人工 tier。
- 生成器不可见：holdout、产品名、原 run_id、人工 rationale、总分与排名。
- 盲评：候选 rubric 冻结后，使用新的空白 chat 只评 holdout。

## 文件

- `manifest.json`：生成时间、规模、拆分与局限；
- `data/dev.jsonl`：候选 rubric 的发现数据；
- `data/holdout.jsonl`：不含人工标签的盲评输入；冻结候选前不得提供给生成器；
- `data/audit_labels.jsonl`：含人工理由与标签，仅保存在本机，差异审计时才用；
- `data/source_map.private.jsonl`：匿名 subject 到源文件的本机私有审计映射，不上传 GitHub；
- `rubric-v2-candidate.yaml`：人工根据当前失败模式写出的候选基线，尚未获得晋级资格。
- `generator_prompt.txt`：只读取 dev 的 rubric 生成提示词；
- `holdout_judge_prompt.txt`：候选冻结后，在另一空白 chat 使用的盲评提示词。

重新生成：

```powershell
python scripts/autorubric_export.py
python -m pytest tests/unit/test_autorubric_export.py -q
```

建议后续把 dev 送入 OpenJudge 的 rubric generation/optimization 流程，但必须保留这里的组级 holdout 和人工终裁。当前 10 场/2 题族明显小于可做生产验证的规模。

## 晋级/停止条件

晋级建议必须同时满足：holdout 全部盲评；无伪完成或越权类致命反例；exact agreement 和加权 κ 均不劣于 v1；独立评审者能复现所有新增锚点。任一条件不满足，保留为候选并记录反例，不改官方评分。
