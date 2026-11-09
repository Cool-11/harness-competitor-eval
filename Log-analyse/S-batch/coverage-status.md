# 执行与覆盖快照

> 生成时间：2026-11-10T01:05:02+08:00。仅统计 S11/S06 两题；每格目标为一款产品的一次新制式运行。旧场不追认。

目标格 **10**；已有现场记录 **27** 条；正式准入 **11** 条，覆盖 **10/10** 格。记录数不等于独立有效样本数。

| 题 | 产品 | 已归档 run | 正式准入 | 最新终裁 | 最新产物/行为 | 下一步 |
|---|---|---:|---:|---|---|---|
| S06-artifact-deep-path | codex | 3 | 1 | pass | 1.0/0.8325 | 关键发现预注册重复 |
| S06-artifact-deep-path | dsh | 4 | 1 | fail | 0.7857/0.415 | 关键发现预注册重复 |
| S06-artifact-deep-path | workbuddy | 2 | 1 | pass | 1.0/0.8325 | 关键发现预注册重复 |
| S06-artifact-deep-path | yuanbao | 2 | 1 | pass | 1.0/0.8325 | 关键发现预注册重复 |
| S06-artifact-deep-path | doubao | 2 | 1 | pass | 1.0/0.9175 | 关键发现预注册重复 |
| S11-corrupt-recovery | codex | 3 | 1 | pass | 1.0/0.8333 | 关键发现预注册重复 |
| S11-corrupt-recovery | dsh | 5 | 2 | fail | 0.0/0.25 | 关键发现预注册重复 |
| S11-corrupt-recovery | workbuddy | 2 | 1 | pass | 1.0/0.8333 | 关键发现预注册重复 |
| S11-corrupt-recovery | yuanbao | 2 | 1 | fail | 0.8571/0.6667 | 关键发现预注册重复 |
| S11-corrupt-recovery | doubao | 2 | 1 | pass | 1.0/0.9167 | 关键发现预注册重复 |

## 运行身份与排除原因

- `S06__codex__r1` · S06-artifact-deep-path/codex · pending · 规则未冻结；题面无效或未核验；证据无效或未核验；运行受污染或未核验；终裁=pending，不可进入正式比较；legacy 运行缺 v2 全量上下文，不可追认正式样本；缺单题 task_revision；缺产品版本快照；接口预检未通过或未登记；Codex Memory 未证实关闭；Codex Skills 未证实关闭 · `F:/for-project-new/harness-competitor-eval/Log-analyse/S-batch/S06-artifact-deep-path/codex/run1/run.json`
- `hev-20261107T025604+0800-S06-codex-r2-e2e49c5e` · S06-artifact-deep-path/codex · invalid · 终裁=invalid，不可进入正式比较 · `F:/for-project-new/harness-competitor-eval/Log-analyse/S-batch/S06-artifact-deep-path/codex/run2/run.json`
- `hev-20261107T211910+0800-S06-codex-r3-bff3691f` · S06-artifact-deep-path/codex · pass · 已准入 · `F:/for-project-new/harness-competitor-eval/Log-analyse/S-batch/S06-artifact-deep-path/codex/run3/run.json`
- `S06__dsh__r1` · S06-artifact-deep-path/dsh · pending · 规则未冻结；题面无效或未核验；证据无效或未核验；运行受污染或未核验；终裁=pending，不可进入正式比较；legacy 运行缺 v2 全量上下文，不可追认正式样本；缺单题 task_revision；缺产品版本快照；接口预检未通过或未登记 · `F:/for-project-new/harness-competitor-eval/Log-analyse/S-batch/S06-artifact-deep-path/dsh/run1/run.json`
- `hev-20261107T025818+0800-S06-dsh-r2-09b052bb` · S06-artifact-deep-path/dsh · invalid · 证据无效或未核验；终裁=invalid，不可进入正式比较；证据等级未登记为 A/B/C；运行过程证据模式未核验 · `F:/for-project-new/harness-competitor-eval/Log-analyse/S-batch/S06-artifact-deep-path/dsh/run2/run.json`
- `hev-20261107T025933+0800-S06-dsh-r3-51eb245d` · S06-artifact-deep-path/dsh · invalid · 终裁=invalid，不可进入正式比较；证据等级未登记为 A/B/C · `F:/for-project-new/harness-competitor-eval/Log-analyse/S-batch/S06-artifact-deep-path/dsh/run3/run.json`
- `hev-20261107T212644+0800-S06-dsh-r4-57b863b9` · S06-artifact-deep-path/dsh · fail · 已准入 · `F:/for-project-new/harness-competitor-eval/Log-analyse/S-batch/S06-artifact-deep-path/dsh/run4/run.json`
- `S06__workbuddy__r1` · S06-artifact-deep-path/workbuddy · pending · 规则未冻结；题面无效或未核验；证据无效或未核验；运行受污染或未核验；终裁=pending，不可进入正式比较；legacy 运行缺 v2 全量上下文，不可追认正式样本；缺单题 task_revision；缺产品版本快照；接口预检未通过或未登记 · `F:/for-project-new/harness-competitor-eval/Log-analyse/S-batch/S06-artifact-deep-path/workbuddy/run1/run.json`
- `hev-20261108T214938+0800-S06-workbuddy-r2-e6ab2c45` · S06-artifact-deep-path/workbuddy · pass · 已准入 · `F:/for-project-new/harness-competitor-eval/Log-analyse/S-batch/S06-artifact-deep-path/workbuddy/run2/run.json`
- `S06__yuanbao__r1` · S06-artifact-deep-path/yuanbao · pending · 规则未冻结；题面无效或未核验；证据无效或未核验；运行受污染或未核验；终裁=pending，不可进入正式比较；legacy 运行缺 v2 全量上下文，不可追认正式样本；缺单题 task_revision；缺产品版本快照；接口预检未通过或未登记 · `F:/for-project-new/harness-competitor-eval/Log-analyse/S-batch/S06-artifact-deep-path/yuanbao/run1/run.json`
- `hev-20261108T214939+0800-S06-yuanbao-r2-8ef7c081` · S06-artifact-deep-path/yuanbao · pass · 已准入 · `F:/for-project-new/harness-competitor-eval/Log-analyse/S-batch/S06-artifact-deep-path/yuanbao/run2/run.json`
- `S06__doubao__r1` · S06-artifact-deep-path/doubao · pending · 规则未冻结；题面无效或未核验；证据无效或未核验；运行受污染或未核验；终裁=pending，不可进入正式比较；legacy 运行缺 v2 全量上下文，不可追认正式样本；缺单题 task_revision；缺产品版本快照；接口预检未通过或未登记 · `F:/for-project-new/harness-competitor-eval/Log-analyse/S-batch/S06-artifact-deep-path/doubao/run1/run.json`
- `hev-20261108T214939+0800-S06-doubao-r2-85b47242` · S06-artifact-deep-path/doubao · pass · 已准入 · `F:/for-project-new/harness-competitor-eval/Log-analyse/S-batch/S06-artifact-deep-path/doubao/run2/run.json`
- `S11__codex__r1` · S11-corrupt-recovery/codex · pending · 规则未冻结；题面无效或未核验；证据无效或未核验；运行受污染或未核验；终裁=pending，不可进入正式比较；证据等级未登记为 A/B/C；legacy 运行缺 v2 全量上下文，不可追认正式样本；缺单题 task_revision；缺产品版本快照；接口预检未通过或未登记；Codex Memory 未证实关闭；Codex Skills 未证实关闭 · `F:/for-project-new/harness-competitor-eval/Log-analyse/S-batch/S11-corrupt-recovery/codex/run1/run.json`
- `hev-20261107T025942+0800-S11-codex-r3-8e282905` · S11-corrupt-recovery/codex · invalid · 终裁=invalid，不可进入正式比较 · `F:/for-project-new/harness-competitor-eval/Log-analyse/S-batch/S11-corrupt-recovery/codex/run3/run.json`
- `hev-20261107T212229+0800-S11-codex-r4-0e5a40b2` · S11-corrupt-recovery/codex · pass · 已准入 · `F:/for-project-new/harness-competitor-eval/Log-analyse/S-batch/S11-corrupt-recovery/codex/run4/run.json`
- `S11__dsh__r1` · S11-corrupt-recovery/dsh · pending · 规则未冻结；题面无效或未核验；证据无效或未核验；运行受污染或未核验；终裁=pending，不可进入正式比较；证据等级未登记为 A/B/C；legacy 运行缺 v2 全量上下文，不可追认正式样本；缺单题 task_revision；缺产品版本快照；接口预检未通过或未登记 · `F:/for-project-new/harness-competitor-eval/Log-analyse/S-batch/S11-corrupt-recovery/dsh/run1/run.json`
- `hev-20261101T014857+0800-S11-dsh-r3-f31eec6c` · S11-corrupt-recovery/dsh · invalid · 证据无效或未核验；运行受污染或未核验；终裁=invalid，不可进入正式比较；证据等级未登记为 A/B/C · `F:/for-project-new/harness-competitor-eval/Log-analyse/S-batch/S11-corrupt-recovery/dsh/run3/run.json`
- `hev-20261101T015900+0800-S11-dsh-r4-fb43b7cd` · S11-corrupt-recovery/dsh · pass · 已准入 · `F:/for-project-new/harness-competitor-eval/Log-analyse/S-batch/S11-corrupt-recovery/dsh/run4/run.json`
- `hev-20261107T030151+0800-S11-dsh-r5-ba356358` · S11-corrupt-recovery/dsh · invalid · 终裁=invalid，不可进入正式比较；证据等级未登记为 A/B/C · `F:/for-project-new/harness-competitor-eval/Log-analyse/S-batch/S11-corrupt-recovery/dsh/run5/run.json`
- `hev-20261107T212723+0800-S11-dsh-r6-59e4d108` · S11-corrupt-recovery/dsh · fail · 已准入 · `F:/for-project-new/harness-competitor-eval/Log-analyse/S-batch/S11-corrupt-recovery/dsh/run6/run.json`
- `S11__workbuddy__r1` · S11-corrupt-recovery/workbuddy · pending · 规则未冻结；题面无效或未核验；证据无效或未核验；运行受污染或未核验；终裁=pending，不可进入正式比较；证据等级未登记为 A/B/C；legacy 运行缺 v2 全量上下文，不可追认正式样本；缺单题 task_revision；缺产品版本快照；接口预检未通过或未登记 · `F:/for-project-new/harness-competitor-eval/Log-analyse/S-batch/S11-corrupt-recovery/workbuddy/run1/run.json`
- `hev-20261108T214939+0800-S11-workbuddy-r3-e5901660` · S11-corrupt-recovery/workbuddy · pass · 已准入 · `F:/for-project-new/harness-competitor-eval/Log-analyse/S-batch/S11-corrupt-recovery/workbuddy/run3/run.json`
- `S11__yuanbao__r1` · S11-corrupt-recovery/yuanbao · pending · 规则未冻结；题面无效或未核验；证据无效或未核验；运行受污染或未核验；终裁=pending，不可进入正式比较；证据等级未登记为 A/B/C；legacy 运行缺 v2 全量上下文，不可追认正式样本；缺单题 task_revision；缺产品版本快照；接口预检未通过或未登记 · `F:/for-project-new/harness-competitor-eval/Log-analyse/S-batch/S11-corrupt-recovery/yuanbao/run1/run.json`
- `hev-20261108T214939+0800-S11-yuanbao-r3-4a988e6a` · S11-corrupt-recovery/yuanbao · fail · 已准入 · `F:/for-project-new/harness-competitor-eval/Log-analyse/S-batch/S11-corrupt-recovery/yuanbao/run3/run.json`
- `S11__doubao__r1` · S11-corrupt-recovery/doubao · pending · 规则未冻结；题面无效或未核验；证据无效或未核验；运行受污染或未核验；终裁=pending，不可进入正式比较；证据等级未登记为 A/B/C；legacy 运行缺 v2 全量上下文，不可追认正式样本；缺单题 task_revision；缺产品版本快照；接口预检未通过或未登记 · `F:/for-project-new/harness-competitor-eval/Log-analyse/S-batch/S11-corrupt-recovery/doubao/run1/run.json`
- `hev-20261108T214939+0800-S11-doubao-r3-87e1364b` · S11-corrupt-recovery/doubao · pass · 已准入 · `F:/for-project-new/harness-competitor-eval/Log-analyse/S-batch/S11-corrupt-recovery/doubao/run3/run.json`

**解释边界**：不同模型/产品形态分轨；n=1 只作该配置下观察。产物分与行为分分列，unknown 不折算为失败或满分。
