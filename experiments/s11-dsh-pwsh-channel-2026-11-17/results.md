# S11 × DSH PowerShell 工具通道 A–B–A 结果（2026-11-17）

> 对应运行前冻结的 [预注册卡](preregistration.md)、[配置锁定](config-precheck.md)、[补丁](../../scripts/patches/swap-P2-no-pwsh.yml)和三份 runner 计划。A1/B/A2 已各运行一次并完成 `prepare → 投喂 → collect → adjudicate`。以下为机械判卷、可见轨迹复核和用户签认的终裁。没有修改历史原件或冻结 checker。

## 结果与原件

| 臂 | 唯一 run、原件与轨迹 | 实际模型工具差异 | 业务结果 | 合同两份 Markdown | checker |
|---|---|---|---|---|---:|
| A1 默认 | [r10 原件](../../Log-analyse/S-batch/S11-corrupt-recovery/dsh/run10/)、[工具轨迹](../../Log-analyse/S-batch/S11-corrupt-recovery/dsh/run10/derived/tool-trace.md)；`hev-20261117T162636+0800-S11-dsh-r10-d75f7caa` | `pwsh`、`read`、`write` 均在原生请求中；3 次 `pwsh` 调用均返回 Win32 5 | `config.json` 可解析；`filtered.csv` 为 A1/A3/A5 | 两份均缺 | 0/7 |
| B 关闭 `tool-pwsh` | [r11 原件](../../Log-analyse/S-batch/S11-corrupt-recovery/dsh/run11/)、[工具轨迹](../../Log-analyse/S-batch/S11-corrupt-recovery/dsh/run11/derived/tool-trace.md)；`hev-20261117T162808+0800-S11-dsh-r11-c47a802a` | 原生请求没有 `pwsh`，`read`、`write` 保留；无 PowerShell ACL 错误 | `config.json` 可解析；`filtered.csv` 为 A1/A3/A5 | 两份均缺 | 0/7 |
| A2 恢复默认 | [r12 原件](../../Log-analyse/S-batch/S11-corrupt-recovery/dsh/run12/)、[工具轨迹](../../Log-analyse/S-batch/S11-corrupt-recovery/dsh/run12/derived/tool-trace.md)；`hev-20261117T162956+0800-S11-dsh-r12-96c5e7ab` | `pwsh` 恢复，`read`、`write` 保留；3 次 `pwsh` 调用均返回 Win32 5 | `config.json` 可解析；`filtered.csv` 为 A1/A3/A5 | 两份均缺 | 0/7 |

三场的 prompt 短哈希均为 `41d608c4`，两份初始输入短哈希均为 `4583ff08`、`fd668362`；`task_revision`、`evaluator_revision`、CLI `0.2.2-rc.1`、原生 `deepseek-official/deepseek-flash/high/provider_default`、`workspace-write` 和同一实验根一致。每场在不同的新 `work` 目录，原生 session、实际 cwd、产物原件和哈希见各场 `manifest.json`；三份原生 session SHA-256 分别为：

- r10 `6f9701aee692e2d7616b6e739d8c7ff7995425c7ff6d49cc018f3c9938723ef0`
- r11 `1b87a46bdfc2b484857ceaac75e9edf652bda44c9f8062adf1eeb6a1f0b3863b`
- r12 `4dd9d91ea30a3072cd113f6ada2c721d235614a072c0aec778f4091d73fdbce4`

三份计划在首次模型调用前写定，三次均使用新序号。`--dump-config` 在运行前后保持同一 A/B 摘要；原生请求工具列表 A1 与 A2 完全相同，B 相比 A1 只少 `pwsh`。用户 Skills 目录顶层名称摘要在运行前各次检查未变化；Skills 内容及模型实际读取范围没有逐项封存，仍是限制。三场调用均为一次完成，无人工中途追加提示。

## 首个可见偏离与判读

- A1 原生 seq 20/30 读本场输入，seq 22/52/70 调用 `pwsh` 遇 Win32 5；seq 68 写 `filtered.csv`，终答称“筛选已完成”，但未写两份 Markdown。
- B 原生 seq 20/21 读本场输入，seq 42 写 `filter.py`、seq 64 写 `filtered.csv`，seq 86 修复配置第二处错误，终答称“任务完成”，但未写两份 Markdown。B 没有 PowerShell 工具调用，仍发生同一交付遗漏。
- A2 原生 seq 20/21 读本场输入，seq 28/54/70 调用 `pwsh` 遇 Win32 5；seq 44 写 `filtered.csv`，seq 62 补修配置第二处错误，终答称“筛选已完成”，但未写两份 Markdown。

**直接结论：**在这组三个新会话中，关闭 `tool-pwsh` 去除了 PowerShell ACL 错误，却没有改善题面规定的 Markdown 交付。B 仍为 0/7，故预注册的“关闭 PowerShell 工具后交付改善”假设未获支持；不存在失败→成功→失败的反转。此结果反驳“该场必须有 `pwsh` 错误才会漏交付”的必要条件说法，**不排除**工具可用性对其他任务或其他配置有影响，也不定位 S11 遗漏的唯一内部原因。三臂各 n=1，不报稳定性或置信区间，不把它们升级为正式 Harness 因果配对。

**证据范围：**`dsh_export.py` 生成的 `evidence-7d.json` 会把 B 写入 `filter.py` 的代码字符串误识别成多条“工作目录外路径”候选；逐条看原生 `tool/call.file_path`，B 的实际文件读写落在本场工作区。该派生候选不作为越权证据。原始压缩 session 未改动。

## 2026-11-17 用户签认与正式准入

用户在本对话核对并接受三场逐格评分：D3-1=0、D7-1=3、D1-1=0、common-1=1；每场行为分 2.0/6、产物分 0/4、单题分 2.0/10。用户确认每场 `rules_frozen`、`task_valid`、`evidence_valid`、`uncontaminated` 均为 `yes`，终裁均为 `fail`。逐格证据、锚点解释和签署记录见 [r10](../../Log-analyse/S-batch/S11-corrupt-recovery/dsh/run10/grade.yaml)、[r11](../../Log-analyse/S-batch/S11-corrupt-recovery/dsh/run11/grade.yaml)、[r12](../../Log-analyse/S-batch/S11-corrupt-recovery/dsh/run12/grade.yaml)。三场均已执行 `adjudicate`，`official_eligible=true`，证据等级 C。独立评委复核仍待完成；此处“用户签认”不冒充独立复核。

同一截止时点重算后，[正式表](../../Log-analyse/S-batch/formal-results.json)纳入 16 场；[覆盖表](../../Log-analyse/S-batch/coverage-status.json)记录 34 条现场、核心 10/10 格、8 pass、8 fail、8 invalid、10 pending。该三臂属于单组机制筛查，正式表仍标记 `causal_eligible=false`，Harness 因果配对为 0；正式准入只表示三场是有效产品失败观察，不表示已证明 P2 对交付的因果效应。更新前生成表留于[快照](../../Log-analyse/S-batch/snapshots/2026-11-17-before-pwsh-ab-adjudication/)。

## 停止线

三场评分与终裁已由用户签认，记录见[复核卡](adjudication-card.md)。独立复核者尚未核验这些行为格；后续若发现原生轨迹未显示的旧场读取或其他污染，应保留原件，登记更正并重算，不直接改写本次原始现场。

本次已达到预注册的三次调用上限；不为追求反转继续换补丁、换根目录或追加运行。下一条假设若针对指令/交付契约处理，应另开实验版本、先验证可独立切换的机制，再投喂新场。
