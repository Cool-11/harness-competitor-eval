# S11 × DSH 交付契约工具通道（skill）对照（预注册，2026-11-21）

> 状态：**已冻结**（2026-11-21 用户确认预算与处理定义后冻结）。未投喂、未新建 run 前完成本卡。继承 P2 通道试验（`experiments/s11-dsh-pwsh-channel-2026-11-17`）的固定条件纪律与 P0 隔离实验（`experiments/p0-dsh-isolated-2026-11-20`）的隔离容器基础设施。

## 为什么选 skill（根因与线索）

[S11 交付遗漏根因](../s11-dsh-pwsh-channel-2026-11-17/results.md)已定位：DSH 在 Windows `headless` 下（run10/run11/run12 三臂）都完成了业务筛选（`filtered.csv` 为 A1/A3/A5）和 `config.json` 两处修复，但把「损坏与修复说明」写在**终答文本**里（run11 step15 终答自述 1083 字），未写题面要求的 `result.md` 与 `error_report.md`；`termination.reason = product_declared_done`；`write` 工具可用（写了 `filter.py`/`filtered.csv`/`config.json.bak`）。根因是交付载体错误，不是写工具失效。

对比线索：

| 场 | 环境 | skills_state | 实际工具 | checker |
|---|---|---|---|---|
| run11（P2 B 臂） | Windows 本机 headless | enabled_unchanged | 24（含 skill） | 0/7 |
| run16（P0 隔离） | Linux 隔离容器 | disabled | 23（无 skill） | 7/7 |

**假设 H：**`tool-skill` + `skill`/`skill-filesystem` 通道让模型走 skill 编排路径，把结果放进终答而非直接写交付文件；关闭该通道后交付改善。

**本实验的修正**：不回到 Windows 非隔离环境（r13 已暴露真实泄露，读取隔离红线在 Windows headless 未验证）。改为**在同一已过读取隔离的 Linux 隔离容器内**，只把 skill 通道从「关」切到「开」，做干净单变量对照。已核查（2026-11-21）该容器可开 skill：三个 skill 插件是 `@deepseek-ai/dsh-base` 内置、仅被 PATCH 三行 `disabled: true` 关闭；镜像捆绑 DSH 默认 skill 内容（`dsh-agent-preset/skills` 下 4 个 + `dsh-skill-office` + badge bundle）；`context_policy=isolated_container` 只作元数据标签、不单独关 skill。

## 可证伪假设与终点

- **H1：**固定 Linux 隔离容器、同镜像、同模型、同题面、同输入，仅把 skill 通道从「关」切到「开」（去掉 PATCH 三行 `skill`/`skill-filesystem`/`tool-skill` 禁用，skills_state→enabled），`result.md` 与 `error_report.md` 交付遗漏复现（checker 0/7）；恢复关闭后（B）交付改善（7/7），再次开启（A2）遗漏再现。
- **反证（零假设）：**skill 开启后仍 7/7，说明 skill 通道不是该遗漏的必要原因（run16 的 7/7 更可能来自 Linux 隔离环境/工具差异，而非 skill 关闭）。
- **主终点：**工作区根目录 `result.md` 与 `error_report.md` 是否同时存在并通过冻结 S11 checker（0/7 或 7/7 为主判定）。
- **过程终点：**原生轨迹中观察到的工具列表是否含 `skill`（A1/A2 应含、B 应不含）；最终回传是否与产物一致。checker 只验产物，行为格按冻结锚点人工签认。

## 固定条件与预检

| 条件 | 运行前证据与停止线 |
|---|---|
| 题面和输入 | 冻结 `tasks/second_tasks/S11-corrupt-recovery/` 的 `prompt.txt`、`config.json`、`data.csv` 完整 SHA-256；只投喂 prompt 与 inputs；checker、spec、truth 不进工作区 |
| 镜像与隔离 | `harness-p0-dsh:20261120`（sha256:dc919cc1…）；每场 `--cap-drop ALL`、`--security-opt no-new-privileges`、`--pids-limit 128`、`--memory 2g`、`--cpus 1`、无宿主挂载、无 docker.sock；容器内探针确认 `/tests`、`/app`、裁判仓库路径均不存在、`/work` 为空 |
| DSH | CLI `0.2.2-rc.1`；`deepseek-official/deepseek-flash`、`reasoning high`、`sampling provider_default`；headless、`workspace-write`、`approval never`；唯一出网为内部预算代理 |
| 处理 | A1/A2 = skill 开启（PATCH 仅 llm-deepseek + 遥测关闭，无 skill 禁用）；B = skill 关闭（PATCH 在 A1 基础上追加三行 skill 禁用，与 run16 `shared.yml` 逐字节一致）。逐字段比较，唯一差异必须是 skill 通道 |
| 身份与取证 | 每场 `prepare → 投喂 → collect → 人工 adjudicate`；新 `run_id` 与未用序号（19/20/21 起）；保存原生 session、真实 cwd、stdout/stderr、退出状态、产物、哈希、checker 输出与行为依据 |

## 顺序与停止条件

1. **A1（skill 开启）：**若 `result.md`+`error_report.md` 均正确交付（7/7），停止「skill 修复」假设——skill 通道不是该遗漏的必要原因；若 0/7（复现遗漏），继续。
2. **B（skill 关闭）：**若 7/7，继续 A2 反转；若仍 0/7，保留为异常场并停止（说明除 skill 外另有因素）。
3. **A2（skill 开启恢复）：**若回到 0/7，反转成立；若 7/7，报告反转未成立并检查漂移。

A1–B–A2 仅是最小机制筛查。出现预期「失败→成功→失败」后，再预注册各臂独立重复与成本上限；单组三场不算稳定性结论。三臂各 n=1，只报告此配置下的观察。

## 预算与授权

- 三次调用，每臂 ≤600 秒、单次完成，无人工中途追加提示（本实验无 P0 的交付门追加反馈）。
- 累计费用不超过 **5 元人民币**（在用户授权的 ≤$5 上限之内）；实际以运行前余额检查与运行后余额变动为准。预估 S11 简单任务 token 极小（run16 单场约 28 秒）。
- 用户已确认：预算上限、处理定义（skill 通道作为唯一改动）、发射口令（2026-11-21）。

## 现场登记（待执行）

- 运行根及同根预检：待执行
- A1/B/A2 最终配置脱敏快照、差异清单与哈希：待执行
- A1/B/A2 `run_id`、原件、checker、行为签认、终裁：待执行
- 独立复核意见：待执行
