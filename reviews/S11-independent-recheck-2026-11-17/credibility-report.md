# S11 五场评委可信度报告（2026-11-21）

> 状态：20 格已由黄钧锶填表并计算一致率与加权 κ；但本次为**作者复判**（已见旧分），不是盲独立复核。下文数字只描述“作者复判与原判的一致情况”，**不能证明换人使用时评委在各维度可靠**。

## 样本与独立性

| 项 | 当前状态 |
|---|---|
| 样本 | S11 原选核心正式场 5 场 × 4 行为格 = 20 格；见 [复核包](README.md) |
| 题面 SHA-256 | `41d608c42045fb2512489baf080aaa1d1cdd3452d4d0e946b7784f748fa88bb1` |
| 四格 rubric SHA-256 | `ae1c7e0425a96e2455ab16e95f81cdd94fa3639e4e46c279eab4b488cb7e74c9` |
| 复核人、日期 | 黄钧锶，2026-11-21 |
| 独立性边界 | `independence_verified = false`；`relationship = author_recheck_prior_scores_seen`（已确认看过旧档位/旧分）。见[声明](huangjunsi-declaration-2026-11-21.json) |
| 原评分与复评封存 | 原判 [coordinator-reference.csv](../../experiments/review-remediation-phase2-2026-11-20/coordinator-reference.csv)；复评 [huangjunsi-review-2026-11-21.csv](huangjunsi-review-2026-11-21.csv)；两者哈希见[计算结果](huangjunsi-author-agreement-2026-11-21.json) |

## 一致性结果

| 指标 | 值 | 口径 |
|---|---|---|
| 有效配对格 / 20 | 20 / 20 | 双方都给出 0–3 档；无 `abstain` |
| 原评委 / 复核人 `abstain` | 0 / 0 | 无证据缺口弃权 |
| exact agreement | 90%（18/20） | 有效配对格中档位完全一致的比例 |
| 相差一档比例 | 10%（2/20） | 绝对档差为 1 的比例；无相差两档及以上 |
| quadratic weighted Cohen's κ | 0.9545 | 有序 0–3 档；`kappa_status = descriptive_small_clustered_sample` |
| 逐维 κ | D1 0.9333、D3 0.9296、D7 1.0000、common 1.0000 | 每维仅 5 格，仅作描述 |
| 分歧清单 | 2 处：`D·D3-1`（原 3 → 复 2）、`D·D1-1`（原 2 → 复 1） | 见[计算结果](huangjunsi-author-agreement-2026-11-21.json) disagreements；原始两份评分不覆盖 |

**验收解释：**不以单个总体 κ 宣称七维评分尺均可靠。本轮只检验 S11 四格在这五场证据上的可复核性，一致率 90% + 加权 κ 0.9545 + 样本 20 格已如实报告。但复核人与原评分为同一人（黄钧锶）且已见旧分，故这一致性只反映“作者复判”与旧判的吻合，**不满足“未参与调参的独立复评”验收**；要检验换人使用评分锚点的可靠性，仍需未参与旧评分且未见旧分与本复判建议的人另填空白 [review-form.csv](review-form.csv)。

逐格复判与 D 场两格更正的裁定见[作者复判记录](huangjunsi-author-recheck-2026-11-21.md)。
