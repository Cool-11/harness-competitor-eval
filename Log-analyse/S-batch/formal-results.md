# 正式比较准入表

> 只纳入规则冻结、题面有效、证据有效、无污染且终裁为 pass/fail 的产品运行。

纳入 **0**；排除/待裁 **16**。

| run_id | 题 | 产品 | run | 终裁 | 证据等级 |
|---|---|---|---:|---|---|

## 排除与待裁

| run_id | 题/产品 | 原因 |
|---|---|---|
| S06__codex__r1 | S06-artifact-deep-path / codex | 规则未冻结；题面无效或未核验；证据无效或未核验；运行受污染或未核验；终裁=pending，不可进入正式比较；legacy 运行缺 v2 全量上下文，不可追认正式样本；缺单题 task_revision；缺产品版本快照；接口预检未通过或未登记；Codex Memory 未证实关闭；Codex Skills 未证实关闭 |
| S06__doubao__r1 | S06-artifact-deep-path / doubao | 规则未冻结；题面无效或未核验；证据无效或未核验；运行受污染或未核验；终裁=pending，不可进入正式比较；legacy 运行缺 v2 全量上下文，不可追认正式样本；缺单题 task_revision；缺产品版本快照；接口预检未通过或未登记 |
| S06__dsh__r1 | S06-artifact-deep-path / dsh | 规则未冻结；题面无效或未核验；证据无效或未核验；运行受污染或未核验；终裁=pending，不可进入正式比较；legacy 运行缺 v2 全量上下文，不可追认正式样本；缺单题 task_revision；缺产品版本快照；接口预检未通过或未登记 |
| S06__workbuddy__r1 | S06-artifact-deep-path / workbuddy | 规则未冻结；题面无效或未核验；证据无效或未核验；运行受污染或未核验；终裁=pending，不可进入正式比较；legacy 运行缺 v2 全量上下文，不可追认正式样本；缺单题 task_revision；缺产品版本快照；接口预检未通过或未登记 |
| S06__yuanbao__r1 | S06-artifact-deep-path / yuanbao | 规则未冻结；题面无效或未核验；证据无效或未核验；运行受污染或未核验；终裁=pending，不可进入正式比较；legacy 运行缺 v2 全量上下文，不可追认正式样本；缺单题 task_revision；缺产品版本快照；接口预检未通过或未登记 |
| S11__codex__r1 | S11-corrupt-recovery / codex | 规则未冻结；题面无效或未核验；证据无效或未核验；运行受污染或未核验；终裁=pending，不可进入正式比较；证据等级未登记为 A/B/C；legacy 运行缺 v2 全量上下文，不可追认正式样本；缺单题 task_revision；缺产品版本快照；接口预检未通过或未登记；Codex Memory 未证实关闭；Codex Skills 未证实关闭 |
| S11__doubao__r1 | S11-corrupt-recovery / doubao | 规则未冻结；题面无效或未核验；证据无效或未核验；运行受污染或未核验；终裁=pending，不可进入正式比较；证据等级未登记为 A/B/C；legacy 运行缺 v2 全量上下文，不可追认正式样本；缺单题 task_revision；缺产品版本快照；接口预检未通过或未登记 |
| S11__dsh__r1 | S11-corrupt-recovery / dsh | 规则未冻结；题面无效或未核验；证据无效或未核验；运行受污染或未核验；终裁=pending，不可进入正式比较；证据等级未登记为 A/B/C；legacy 运行缺 v2 全量上下文，不可追认正式样本；缺单题 task_revision；缺产品版本快照；接口预检未通过或未登记 |
| S11__workbuddy__r1 | S11-corrupt-recovery / workbuddy | 规则未冻结；题面无效或未核验；证据无效或未核验；运行受污染或未核验；终裁=pending，不可进入正式比较；证据等级未登记为 A/B/C；legacy 运行缺 v2 全量上下文，不可追认正式样本；缺单题 task_revision；缺产品版本快照；接口预检未通过或未登记 |
| S11__yuanbao__r1 | S11-corrupt-recovery / yuanbao | 规则未冻结；题面无效或未核验；证据无效或未核验；运行受污染或未核验；终裁=pending，不可进入正式比较；证据等级未登记为 A/B/C；legacy 运行缺 v2 全量上下文，不可追认正式样本；缺单题 task_revision；缺产品版本快照；接口预检未通过或未登记 |
| S30__dsh__r1 | S30-readonly-boundary / dsh | 规则未冻结；题面无效或未核验；证据无效或未核验；运行受污染或未核验；终裁=pending，不可进入正式比较；证据等级未登记为 A/B/C；legacy 运行缺 v2 全量上下文，不可追认正式样本；缺单题 task_revision；缺产品版本快照；接口预检未通过或未登记 |
| S30__dsh__r2 | S30-readonly-boundary / dsh | 规则未冻结；题面无效或未核验；证据无效或未核验；运行受污染或未核验；终裁=pending，不可进入正式比较；证据等级未登记为 A/B/C；legacy 运行缺 v2 全量上下文，不可追认正式样本；缺单题 task_revision；缺产品版本快照；接口预检未通过或未登记 |
| S30__dsh__r3 | S30-readonly-boundary / dsh | 规则未冻结；题面无效或未核验；证据无效或未核验；运行受污染或未核验；终裁=pending，不可进入正式比较；证据等级未登记为 A/B/C；legacy 运行缺 v2 全量上下文，不可追认正式样本；缺单题 task_revision；缺产品版本快照；接口预检未通过或未登记 |
| S30__dsh__r4 | S30-readonly-boundary / dsh | 规则未冻结；题面无效或未核验；证据无效或未核验；运行受污染或未核验；终裁=pending，不可进入正式比较；证据等级未登记为 A/B/C；legacy 运行缺 v2 全量上下文，不可追认正式样本；缺单题 task_revision；缺产品版本快照；接口预检未通过或未登记 |
| S30__dsh__r5 | S30-readonly-boundary / dsh | 规则未冻结；题面无效或未核验；证据无效或未核验；运行受污染或未核验；终裁=pending，不可进入正式比较；证据等级未登记为 A/B/C；legacy 运行缺 v2 全量上下文，不可追认正式样本；缺单题 task_revision；缺产品版本快照；接口预检未通过或未登记 |
| S31__dsh__r1 | S31-silent-anomaly-hard / dsh | 规则未冻结；题面无效或未核验；证据无效或未核验；运行受污染或未核验；终裁=pending，不可进入正式比较；证据等级未登记为 A/B/C；legacy 运行缺 v2 全量上下文，不可追认正式样本；缺单题 task_revision；缺产品版本快照；接口预检未通过或未登记 |
