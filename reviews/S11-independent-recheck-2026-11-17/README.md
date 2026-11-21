# S11 五场独立人工复核包（待复核）

本包把 [S11 冻结题面](../../tasks/second_tasks/S11-corrupt-recovery/prompt.txt)、[题目规格](../../tasks/second_tasks/S11-corrupt-recovery/spec.md)、[四格行为复核锚点](../S11-round1-2026-11-06/reviewer/rubric.md)和五个**原选核心正式场**交给未参与对应裁判文件制作的复核人。对象固定为下表五场、每场四格，共 20 格；DSH 后续 r7/r9 不混入本轮。此处是复核任务，不是已有的独立签署。

本轮锁定 `prompt.txt` SHA-256 `41d608c42045fb2512489baf080aaa1d1cdd3452d4d0e946b7784f748fa88bb1`，四格 rubric SHA-256 `ae1c7e0425a96e2455ab16e95f81cdd94fa3639e4e46c279eab4b488cb7e74c9`。若复核前内容变化，另开复核版本，不在本轮静默替换。

| Subject | 原始现场入口 | 证据模式 |
|---|---|---|
| A | [Codex r4](../../Log-analyse/S-batch/S11-corrupt-recovery/codex/run4/) | `native_trace` |
| B | [DSH r6](../../Log-analyse/S-batch/S11-corrupt-recovery/dsh/run6/) | `native_trace` |
| C | [WorkBuddy r3](../../Log-analyse/S-batch/S11-corrupt-recovery/workbuddy/run3/) | `native_trace`；可见范围按来源记录 |
| D | [元宝 r3](../../Log-analyse/S-batch/S11-corrupt-recovery/yuanbao/run3/) | `desktop_export` |
| E | [豆包 r3](../../Log-analyse/S-batch/S11-corrupt-recovery/doubao/run3/) | `desktop_export` |

复核人先读 prompt、spec 和四格复核锚点，再查看各场 `prepare.json`、`manifest.json`、`evidence/`、`artifacts/` 与原生会话或可见导出。**不要先读** `grade.yaml`、`score.json`、`checker_output.txt`、正式比较报告、旧评分或其他复核人的表。日志与路径可能暴露产品身份，因此本包只隔离旧判分，**不宣称完全盲评**。桌面导出不能证明未显示的内部读取、工具调用或恢复步骤。

在 [review-form.csv](review-form.csv) 每格填 `0/1/2/3/abstain`、直接证据位置和简短理由。证据缺失、冲突或观察范围不支持判断时填 `abstain` 并说明缺口；不得填 0 代替未知。`D3-1`、`D7-1`、`D1-1`、`common-1` 的逐档锚点以本包链接的四格行为复核锚点为准。完成后另附署名、日期、是否参与过题目/checker/原评分制作、是否提前见过旧分及产品身份暴露情况。

**比较方法：**协调者先封存复核表，再读取原 `grade.yaml`，按相同 subject/格位对齐。报告 20 格中双方都给出有效档位的分母、`abstain` 数、exact agreement、相差一档比例、0–3 有序档位的 quadratic weighted Cohen's κ，以及逐格分歧。κ 仅作描述，不把 20 格视为 20 次独立产品运行；样本过小或档位分布退化时如实标不可稳健估计。逐项分歧由第三方或双方回看原件仲裁，仲裁结果与原始两份评分分开保存；任何锚点修订须另开版本，不覆盖历史分数。

当前没有独立复核者签名或已填表，因此**评委可信度尚未验收**。

复核与仲裁后填写 [评委可信度报告](credibility-report.md)；当前模板中的指标保持“待计算”。


## 2026-11-20 计算入口补充

新增 `agreement-protocol-v1.json` 只冻结本轮计算口径及既有题面/锚点指纹，不冒充历史预注册。使用 `scripts/reviewer_agreement.py` 计算一致率、四档加权 κ、逐维覆盖、弃权与分歧。协调者原判已从现有 signed_off grade 提取到 `experiments/review-remediation-phase2-2026-11-20/coordinator-reference.csv`，来源哈希另存；复核人仍不得提前查看。当前计算为20格未复评，overall=null；没有新增独立签名。命令和边界见[第二批证据包](../../experiments/review-remediation-phase2-2026-11-20/README.md)。
