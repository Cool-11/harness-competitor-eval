# S11 × DSH 交付遗漏独立复测预注册（2026-11-12，运行前）

## 问题与边界

检验 DSH S11 run6 中“业务筛选结果 A1/A3/A5 已出现，但未按契约交付 `result.md`、`error_report.md`”在相同产品配置下的两次新会话中是否再出现。本实验是 `B_native_product` 的重复观察，**不**把 run4（旧版本 0.2.1-rc.5）与 run6（0.2.2-rc.1）当受控 Harness 对照，也不把 ACL 工具错误直接解释为交付遗漏的原因。

## 冻结条件

- 唯一题包：`tasks/second_tasks/S11-corrupt-recovery/` 当前冻结的 `prompt.txt` 和 `inputs/config.json`、`inputs/data.csv`。仅这三件进入各自新工作区；checker、spec、truth、历史现场及本文件留在裁判侧。以每场 `prepare.json.task_revision` 和输入哈希为最终身份。
- 产品与环境：DSH CLI `0.2.2-rc.1`，`headless` profile，`--permission-mode workspace-write --approval-policy never`，默认模型配置；只通过本地忽略文件注入 `DEEPSEEK_API_KEY` 环境变量，值不写入计划或日志。运行前 `dsh --profile headless --dump-config` 输出 SHA-256 为 `4cda676ca86986f4404dc76724074946fb9cb47b811cb8eece6b26f543af5b5d`（仅登记摘要，不保存可能含凭证的明文）。两次调用前后重新核对该摘要与 CLI 版本；若不同，停止并标记配置漂移。
- 执行计划：[`runner-plans/s11-dsh-delivery-repeat-20261112-v1.json`](../../runner-plans/s11-dsh-delivery-repeat-20261112-v1.json)。两次各自 `prepare`、独立 `run_id`、独立 `C:/tmp_run/<题>/<产品>/run<n>/work` 与新原生会话；每场上限 600 秒，不对产品失败自动重试，也不向会话发送纠偏提示。runner 只送 `prompt.txt` 正文，随后 `collect` 保存原生日志、实际 cwd、输入及产物哈希。
- 评分器与合同：原冻结 checker 不改。主终点为工作区根目录同时存在两份要求的 Markdown，且 checker 产物契约通过；副终点为业务筛选集合是否为 A1/A3/A5，须从落盘文件核查，聊天自述仅作交叉证据。两项分别列结果；行为按 `spec.md` 的 D3/D7/D1/common 锚点复核，无法观察的格保留 unknown。

## 事先约定的判读与停止

- 两场均缺两份 Markdown，才报告“本配置下两次新场重复观察到交付遗漏”；仍不推出跨配置稳定性或 ACL 因果。只要有一场完整交付，就报告结果不一致，不把 run6 描述为稳定失败。
- `prepare` 前预检失败：不创建产品运行。准备后发生 cwd 错位、输入来源不符、原生轨迹无法定位或配置漂移：保留该场并标 invalid/unknown，不以 checker 分数冒充有效结果；如果仍需补足两场有效观察，必须先另行登记新批次与停止条件。
- 两次独立调用或总上限 20 分钟先到即停止。不根据第一次结果调整第二次题面、提示或评分器。终裁仍需证据复核与签认；脚本结果不自动变成正式准入。

## 运行后补充预注册：隔离根目录补跑（在新调用前登记）

首批两次已调用完毕；第二场 r8 的原生轨迹 seq 56–81 读取了旧 r6 的 `filtered.csv`、`final-response.txt`、`config.json`，故 r8 判为 `invalid`，不是有效的第二次重复。为补足两场独立观察，另立 [v2 单槽计划](../../runner-plans/s11-dsh-delivery-repeat-20261112-v2.json)：仅新增一个独立 `C:/tmp_s11_dsh_isolated_20261112` 根目录；题面、输入、DSH profile、版本、模型默认配置、权限、600 秒上限及上述两个终点均不变。新根目录不放旧 run 或裁判文件；仍逐事件检查是否读取外部旧场。若再次污染、配置漂移或原生轨迹不足，停止补跑并报告有效样本不足；不继续追跑到期望结果。因工作目录路径改变，最终两场也只报告各自配置条件下的观察，不表述稳定性或路径单因素效应。

## 再次补充预注册：run 序号修正（在新调用前登记）

v2 的 `auto` 在新根目录中选到了 `run2`；旧 S11 DSH run2 已见历史执行卡，虽不在正式收件槽中，却不能复用该序号。v2 场保留并标 `invalid`，不算独立补样。已修正 runner 的自动编号为“高于已归档最大 run”，并加回归测试。最后只补一次 [v3 显式 run9 计划](../../runner-plans/s11-dsh-delivery-repeat-20261112-v3.json)，使用另一空白根目录；其余冻结条件和判读规则不变。若 r9 再次无效，则停止，报告有效复测不足，不继续开新场。
