# 执行与覆盖快照

> 生成时间：2026-11-04T17:33:23+08:00。仅统计 S11/S06 两题；每格目标为一款产品的一次新制式运行。旧场不追认。

目标格 **10**；已有现场记录 **12** 条；正式准入 **1** 条，覆盖 **1/10** 格。记录数不等于独立有效样本数。

| 题 | 产品 | 已归档 run | 正式准入 | 最新终裁 | 最新产物/行为 | 下一步 |
|---|---|---:|---:|---|---|---|
| S06-artifact-deep-path | codex | 1 | 0 | pending | 1.0/unknown | 新场先 prepare，再核验 cwd/证据并终裁 |
| S06-artifact-deep-path | dsh | 1 | 0 | pending | 1.0/unknown | 新场先 prepare，再核验 cwd/证据并终裁 |
| S06-artifact-deep-path | workbuddy | 1 | 0 | pending | 1.0/unknown | 新场先 prepare，再核验 cwd/证据并终裁 |
| S06-artifact-deep-path | yuanbao | 1 | 0 | pending | 1.0/unknown | 新场先 prepare，再核验 cwd/证据并终裁 |
| S06-artifact-deep-path | doubao | 1 | 0 | pending | 1.0/unknown | 新场先 prepare，再核验 cwd/证据并终裁 |
| S11-corrupt-recovery | codex | 1 | 0 | pending | 1.0/unknown | 新场先 prepare，再核验 cwd/证据并终裁 |
| S11-corrupt-recovery | dsh | 3 | 1 | pass | 1.0/1.0 | 关键发现预注册重复 |
| S11-corrupt-recovery | workbuddy | 1 | 0 | pending | 1.0/unknown | 新场先 prepare，再核验 cwd/证据并终裁 |
| S11-corrupt-recovery | yuanbao | 1 | 0 | pending | 0.8571/unknown | 新场先 prepare，再核验 cwd/证据并终裁 |
| S11-corrupt-recovery | doubao | 1 | 0 | pending | 1.0/unknown | 新场先 prepare，再核验 cwd/证据并终裁 |

## 运行身份与排除原因

- `S06__codex__r1` · S06-artifact-deep-path/codex · pending · 规则未冻结；题面无效或未核验；证据无效或未核验；运行受污染或未核验；终裁=pending，不可进入正式比较；legacy 运行缺 v2 全量上下文，不可追认正式样本；缺单题 task_revision；缺产品版本快照；接口预检未通过或未登记；Codex Memory 未证实关闭；Codex Skills 未证实关闭 · `F:/for-project-new/harness-competitor-eval/Log-analyse/S-batch/S06-artifact-deep-path/codex/run1/run.json`
- `S06__dsh__r1` · S06-artifact-deep-path/dsh · pending · 规则未冻结；题面无效或未核验；证据无效或未核验；运行受污染或未核验；终裁=pending，不可进入正式比较；legacy 运行缺 v2 全量上下文，不可追认正式样本；缺单题 task_revision；缺产品版本快照；接口预检未通过或未登记 · `F:/for-project-new/harness-competitor-eval/Log-analyse/S-batch/S06-artifact-deep-path/dsh/run1/run.json`
- `S06__workbuddy__r1` · S06-artifact-deep-path/workbuddy · pending · 规则未冻结；题面无效或未核验；证据无效或未核验；运行受污染或未核验；终裁=pending，不可进入正式比较；legacy 运行缺 v2 全量上下文，不可追认正式样本；缺单题 task_revision；缺产品版本快照；接口预检未通过或未登记 · `F:/for-project-new/harness-competitor-eval/Log-analyse/S-batch/S06-artifact-deep-path/workbuddy/run1/run.json`
- `S06__yuanbao__r1` · S06-artifact-deep-path/yuanbao · pending · 规则未冻结；题面无效或未核验；证据无效或未核验；运行受污染或未核验；终裁=pending，不可进入正式比较；legacy 运行缺 v2 全量上下文，不可追认正式样本；缺单题 task_revision；缺产品版本快照；接口预检未通过或未登记 · `F:/for-project-new/harness-competitor-eval/Log-analyse/S-batch/S06-artifact-deep-path/yuanbao/run1/run.json`
- `S06__doubao__r1` · S06-artifact-deep-path/doubao · pending · 规则未冻结；题面无效或未核验；证据无效或未核验；运行受污染或未核验；终裁=pending，不可进入正式比较；legacy 运行缺 v2 全量上下文，不可追认正式样本；缺单题 task_revision；缺产品版本快照；接口预检未通过或未登记 · `F:/for-project-new/harness-competitor-eval/Log-analyse/S-batch/S06-artifact-deep-path/doubao/run1/run.json`
- `S11__codex__r1` · S11-corrupt-recovery/codex · pending · 规则未冻结；题面无效或未核验；证据无效或未核验；运行受污染或未核验；终裁=pending，不可进入正式比较；证据等级未登记为 A/B/C；legacy 运行缺 v2 全量上下文，不可追认正式样本；缺单题 task_revision；缺产品版本快照；接口预检未通过或未登记；Codex Memory 未证实关闭；Codex Skills 未证实关闭 · `F:/for-project-new/harness-competitor-eval/Log-analyse/S-batch/S11-corrupt-recovery/codex/run1/run.json`
- `S11__dsh__r1` · S11-corrupt-recovery/dsh · pending · 规则未冻结；题面无效或未核验；证据无效或未核验；运行受污染或未核验；终裁=pending，不可进入正式比较；证据等级未登记为 A/B/C；legacy 运行缺 v2 全量上下文，不可追认正式样本；缺单题 task_revision；缺产品版本快照；接口预检未通过或未登记 · `F:/for-project-new/harness-competitor-eval/Log-analyse/S-batch/S11-corrupt-recovery/dsh/run1/run.json`
- `hev-20261101T014857+0800-S11-dsh-r3-f31eec6c` · S11-corrupt-recovery/dsh · invalid · 证据无效或未核验；运行受污染或未核验；终裁=invalid，不可进入正式比较；证据等级未登记为 A/B/C · `F:/for-project-new/harness-competitor-eval/Log-analyse/S-batch/S11-corrupt-recovery/dsh/run3/run.json`
- `hev-20261101T015900+0800-S11-dsh-r4-fb43b7cd` · S11-corrupt-recovery/dsh · pass · 已准入 · `F:/for-project-new/harness-competitor-eval/Log-analyse/S-batch/S11-corrupt-recovery/dsh/run4/run.json`
- `S11__workbuddy__r1` · S11-corrupt-recovery/workbuddy · pending · 规则未冻结；题面无效或未核验；证据无效或未核验；运行受污染或未核验；终裁=pending，不可进入正式比较；证据等级未登记为 A/B/C；legacy 运行缺 v2 全量上下文，不可追认正式样本；缺单题 task_revision；缺产品版本快照；接口预检未通过或未登记 · `F:/for-project-new/harness-competitor-eval/Log-analyse/S-batch/S11-corrupt-recovery/workbuddy/run1/run.json`
- `S11__yuanbao__r1` · S11-corrupt-recovery/yuanbao · pending · 规则未冻结；题面无效或未核验；证据无效或未核验；运行受污染或未核验；终裁=pending，不可进入正式比较；证据等级未登记为 A/B/C；legacy 运行缺 v2 全量上下文，不可追认正式样本；缺单题 task_revision；缺产品版本快照；接口预检未通过或未登记 · `F:/for-project-new/harness-competitor-eval/Log-analyse/S-batch/S11-corrupt-recovery/yuanbao/run1/run.json`
- `S11__doubao__r1` · S11-corrupt-recovery/doubao · pending · 规则未冻结；题面无效或未核验；证据无效或未核验；运行受污染或未核验；终裁=pending，不可进入正式比较；证据等级未登记为 A/B/C；legacy 运行缺 v2 全量上下文，不可追认正式样本；缺单题 task_revision；缺产品版本快照；接口预检未通过或未登记 · `F:/for-project-new/harness-competitor-eval/Log-analyse/S-batch/S11-corrupt-recovery/doubao/run1/run.json`

**解释边界**：不同模型/产品形态分轨；n=1 只作该配置下观察。产物分与行为分分列，unknown 不折算为失败或满分。
