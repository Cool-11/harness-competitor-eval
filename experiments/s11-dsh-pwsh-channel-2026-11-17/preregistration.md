# S11 × DSH PowerShell 工具通道对照（预注册草案，2026-11-17）

> 状态：当前 DSH CLI 与可控开关已只读核验；尚未投喂或新建 run。正式实验须先完成下列配置和环境预检，并把本卡冻结。旧 S11 r6/r7/r9 只用于提出假设，不和新场合并计算处理效应。

## 为什么选 P2

[S11 旧场首错定位](../../docs/reports/37-S06-S11-首个失配定位-2026-11-16.md)及[独立工作区复测](../s11-dsh-delivery-repeat-2026-11-12/results.md)显示：DSH r6/r7/r9 均未交付冻结题面要求的 `result.md` 与 `error_report.md`；r7/r9 业务筛选及 JSON 修复正确。其原生轨迹还出现 `pwsh` 权限错误，但现有证据不能认定错误导致交付遗漏。

本机 `dsh --version` 为 `0.2.2-rc.1`。当前 `headless --dump-config` 显示 Windows 可用的 `tool-pwsh` 和 `tool-fs` 均已装载；后者可保留文件读取与写入能力。唯一干预为 [补丁](../../scripts/patches/swap-P2-no-pwsh.yml)中 `tool-pwsh.disabled=true`。该试验检验的是 **P2 模型工具通道可用性**，并非改变 Windows ACL、修复 shell 实现或单独改模型提示。关闭工具会改变模型可见工具列表，这正是处理变量，必须在两臂证据中明确记录。

只读预检已执行：`dsh --profile headless --dump-config` 显示默认模型配置为 `deepseek-official / deepseek-flash`，`tool-pwsh.disabled` 为 `process.platform !== 'win32'`；加本补丁后变为 `true`，其余配置内容未见变化，输出中新增的只是 patch 来源注释。`tool-fs` 在两份组合配置中均保留。这仅证明**配置叠加正确**，还不能证明运行时工具暴露、实际模型路由和工作目录均相同。未读取或打印凭据值。

## 可证伪假设与终点

- **假设 H1：**若出错的 PowerShell 工具通道干扰了 S11 的任务完成，那么在同模型、同输入、同工作根下关闭 `tool-pwsh`、保留 `tool-fs` 后，题面要求的两份 Markdown 的交付率会改善；恢复 `tool-pwsh` 后旧失败模式应再次出现。
- **零假设/反证：**关掉 `tool-pwsh` 后仍遗漏两份 Markdown，或者默认臂已经正确交付。两者均不支持“shell 通道是这次遗漏的必要原因”。
- **主终点：**工作区根目录的 `result.md` 与 `error_report.md` 是否同时存在并通过冻结 S11 checker 的对应断言。另列业务集合与 JSON 修复，不把正确 CSV 折算成 Markdown 交付。
- **过程终点：**原生轨迹中的 `pwsh` 调用/错误、`tool-fs` 调用、最终回传是否与产物一致。checker 只验产物，行为格按冻结锚点人工签认。

## 固定条件与预检

| 条件 | 运行前证据与停止线 |
|---|---|
| 题面和输入 | 冻结 `tasks/second_tasks/S11-corrupt-recovery/prompt.txt`、`config.json`、`data.csv` 的完整 SHA-256；只投喂 prompt 和 inputs；checker、spec、truth 不进工作区 |
| DSH | CLI `0.2.2-rc.1` 或重新登记的新版本；同一 profile、provider、model、reasoning、sampling、Skills/Memory、token/时间预算和其余工具；保存脱敏后的最终配置及哈希 |
| 环境 | 同一 OS、盘符、深层根目录、权限、网络和账号；各场用全新独立工作区；分别预检 `tool-fs`，并在默认臂检查 `tool-pwsh` 的可用性及实际错误表现 |
| 处理 | A 为原 `headless`，B 只加 `--patch scripts/patches/swap-P2-no-pwsh.yml`；对最终配置逐字段比较，唯一差异必须是 `tool-pwsh.disabled`；运行时确认 B 没有 `tool-pwsh` 暴露，且两臂 `tool-fs` 可用 |
| 身份与取证 | 每场 `prepare → 投喂 → collect → 人工 adjudicate`；新 `run_id` 与未用序号；保存原生 session、真实 cwd、stdout/stderr、退出状态、产物、哈希、checker 输出与行为依据 |

若默认臂的 PowerShell 完全正常，本实验仍可测试“工具有无”对交付的作用，但不能解释旧场的 ACL 错误。若模型、实际 cwd、输入、权限或其余工具不同，保留现场并标 `invalid/unknown`，不进行因果配对。`--dump-config` 的脱敏快照不得泄露凭据。

## 顺序与停止条件

1. **A1 默认臂：**新运行；若两份 Markdown 均正确交付，停止“旧失败修复”假设，报告版本/环境下未复现；不继续跑到失败。
2. **B 关闭 PowerShell：**新运行，只改一个补丁；若 `tool-fs` 也失效，或配置出现额外差异，保留为无效场并停止。
3. **A2 恢复默认：**新运行，不加补丁；确认唯一改动已经撤销。若未回到 A1 的失败模式，报告反转未成立，检查时间与环境漂移。

A1–B–A2 仅是最小机制筛查。出现预期“失败→成功→失败”后，再预注册各臂独立重复与成本上限，才能讨论重复性或区间；单组三场不算稳定性结论。若 B 改善，也只能说“当前配置下关闭 PowerShell 工具改变了交付结果”，不能把内部模型决策、权限错误或 S11 全部失败直接归给 shell。若无反转，保留阴性结果，转向其他可控假设。

## 待填写的现场登记

- 运行根及同根预检：待执行
- A/B 最终配置脱敏快照、差异清单与哈希：待执行
- 模型、provider、reasoning、sampling、预算：待核实
- A1/B/A2 `run_id`、原件、checker、行为签认、终裁：待执行
- 独立复核意见：待执行

旧 [S30 探索记录](../../Log-analyse/S-batch/S30-readonly-boundary/AB-EXPERIMENT.md)的 C 盘原工作根仍有 run3/run4/run5 的 stdout/stderr；run3 `summary.md` 为 7/7、run5 只读被拒为 0/7，且 run5 明确回报无审批通道。这批旧场没有现行 S11 实验所需的原生轨迹和同版本控制合同，故不作为本卡的基线或处理臂。
