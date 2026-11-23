# tool-bash A/B/A 机制探针结果（2026-11-23 执行，2026-11-24 订正）

## 2026-11-24 订正：A/B/A 不成立

首轮（11-23）记录的「A1 7.00 → B 0.0 → A2 7.00，闭环成立」**作废**。复核发现首轮 B 的 0/7 不是能力缺失：

- B 场 stderr 出现 `dsh: RATE_LIMIT: Experiment proxy stopped request`；
- 首轮预算日志 29 次请求、reserved ¥4.824、`budget_limit` 拦截 6 次；代理硬上限为 ¥5，B 臂把额度耗尽后被 429 中止；
- A2 之所以成功，是续跑时起了新代理、拿到了新额度。

按 docs/41，被基础设施打断的现场记 `invalid`，不计作 `fail`。首轮 B 归档于 `arm-b-invalid-01-budget/`，原件保留。

## 独立额度重跑 B

用独立代理（¥10 上限）重跑 `arm-b`：

| 项 | 结果 |
|---|---|
| 产物分 | **7.00/7**（60/60 条 + 总计 7830）|
| 返回码 | 0（模型自行结束，非超时、非 429）|
| 耗时 | 102.9s |
| observed 工具 | **不含 `bash`**（含 read/write/edit/glob/grep/read_image/workflow/subagent）|
| 预算 | 28 次请求，reserved ¥5.831，0 次拦截 |

## 结论

题面数据是 `item-01..item-60` 与金额 `101..160` 的规则序列，模型在没有任何执行通道的情况下按规律重建出全部 60 条与总计，checker 7/7。

因此：

- **`tool-bash` 不是本任务的物理必需**，本题面不能用来证明它的因果作用；
- A/B/A 三臂未形成反转（开 7 → 关 7），停止条件 2 触发；
- 只有把输入改成高熵、不可推断的数据，才可能让 B 臂真正为 0，届时才具备重做 A/B/A 的前提。

## 证据与缺陷登记

- 首轮 A1/A2 与新 B 臂均为独立 run 身份；容器、`shared.yml`、`merged-config.yml`、session、产物、checker 输出均已归档。
- 缺陷：预算日志曾按固定名 `budget-run2.jsonl` 写入，重跑时覆盖了原 A2 的日志（原为 8 次请求、¥1.219）。A2 的 `run.json` 与 `checker_output.txt` 未受影响；脚本已改为顺序命名（`budget-run<n>.jsonl`），本次订正后生效。
- 预算口径：以上均为 `reserved` 上界，不等于实际扣费；`balance-before/after` 两次读数均为 ¥8.03，与代理计数并存，不做折算。
