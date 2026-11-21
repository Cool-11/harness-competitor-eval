# 11 月 20 日本地整改证据包

本包是本地复算与当前配置核验，新增真实产品运行 **0**；不是预注册历史实验或独立人工签署。主入口：[整改与研究报告](../../docs/reports/42-重构整改与复现核验-2026-11-20.md)。

| 文件 | 性质 |
|---|---|
| core-calibration.json | 当前 S06/S11 fixture 分数及临时语义反例全文；人工期望为 draft |
| local-evidence-audit.json | 五场历史清单的本机字节核验：120/120；不代表入库 |
| public-evidence-subset.json | 按当前 Git 索引筛选：41 项已跟踪且验哈希，79 项仅本地；原清单不变 |
| dsh-p2-precheck.json | 当前 DSH 0.2.2-rc.1 组合配置唯一字段差异；不是模型运行 |
| installed-seam-sources.json | 本机 P7/P8 实现的源码指纹；绝对路径仅作定位，无凭据 |
| coverage.json / .md | 从当前核心两题原件重算的 35 条现场、16 正式、10/10 格 |
| formal-results.json / .md | 对全 S 批次 run.json 副本执行现有 formal-report：16 纳入、25 排除/待裁 |

复算时选新的输出路径，三个新脚本拒绝覆盖已有输出：

```powershell
.\.venv\Scripts\python.exe scripts\core_score_calibration.py --output <新路径>\calibration.json
.\.venv\Scripts\python.exe scripts\dsh_component_precheck.py --output <新路径>\p2.json
.\.venv\Scripts\python.exe scripts\public_evidence_manifest.py <五场原manifest路径> --output <新路径>\public.json
.\.venv\Scripts\python.exe scripts\coverage_report.py --output <新路径>\coverage
```

公开子清单依赖当时的 Git 索引。后续入库后需另开版本重算，不能以本机存在推断已公开。缺失文件单列，损坏文件退出码为 1；成功退出不表示历史清单完整，应检查 `status`。新脚本、快照及本包本轮尚未提交或推送。

## 可干预组件登记（当前核验）

| 组件 / 维度 | seam 与入口 | 生效证据、任务及耦合 | 当前处置 |
|---|---|---|---|
| P2 / D3 失败恢复 | `ctx.tools`、`tool-pwsh.disabled`，headless `--patch scripts/patches/swap-P2-no-pwsh.yml` | 本轮 dump-config A/B 唯一字段差异通过；JS 表达式仍需运行时核验。历史 r10/r11/r12 原生请求 A/B/A 工具列表已有实际生效证据。`tool-fs` 保留，因此不能说禁止文件写入 | 可加载；沿用已有阴性机制案例，禁止重复描述成成功修复 |
| P9 / D6 权限 | `sandbox-policy.mode`，`swap-P9-readonly.yml` | 同时约束 shell 和 fs；S30 适合权限合同校准。只读拒写不自动是缺陷 | 仅整体策略候选，未在本轮加载或跑测 |
| P8 / D7 可观测性 | `session-telemetry-otel` | 当前实现为 FEEDBACK_ONLY/DISABLED，feedback 上报；无独立决策干预证据。见源码指纹及 U-08 | 退出正式组件矩阵；可见行为另评 |
| P7 / D5 停止 | agent-loop 发出 `dispatch.serial("agent/turn-stopping", ...)` | 当前安装源码确认是事件；无独立可替换插件配置行，见 U-09 | 退出单组件矩阵；不得以不存在的插件开关跑测 |
| P1 / D1 信息回传 | 编排与提示候选 | 本轮未核验独立 seam，不能据 B 位点直接认定责任 | unknown |
| P4 / D4 上下文 | compaction / pruner 候选 | 本轮未核验配置及运行触发 | unknown |
| P5 / D2 产物落点 | fs / 外部交付检查候选 | 外部 gate 代码已有本地测试；r13 读取裁判文件 invalid，B/A2 未执行；外部包装器不能冒充已定位 DSH 内部组件 | 暂停新场，先解决读取隔离 |

完整现有机制包：[S11 P2 预注册](../s11-dsh-pwsh-channel-2026-11-17/preregistration.md)、[配置锁定](../s11-dsh-pwsh-channel-2026-11-17/config-precheck.md)、[A/B/A 结果与原件](../s11-dsh-pwsh-channel-2026-11-17/results.md)。真实基线/干预/恢复均已各运行一次，但三场交付均失败，正式因果准入仍为 0；不再花费调用来重复同一三场。

## 核心判卷边界

S06 机械项：路径、UTF-8、固定标题、六个词串。人工语义项：逐条对应来源、不得无依据增补、不能仅堆词、允许等价改写。反例显示增补和堆词均拿 7/7，故机械满分不能充当完整合同通过。冻结 checker 未变，未引入追溯扣分。

S11 机械项：两文件、正则识别 ID、目标 ID 集、两种逗号缺陷词。人工项：ID 是否确实由数据筛出、错误定位与实际配置一致、修复和继续的行为是否有轨迹支持、是否无编造。正则与固定 ID 集不足以担保所有语义。

本轮按实际文件复算：S06 golden=7、partial=5.5；增补=7、堆词=7、遗漏=6.58、等价改写=7；S11 golden=7、partial=tampered=6。`tests/fixtures/SIGNOFF.md` 中 S06/S11 仍 draft；K4 历史签署只覆盖当时修订范围，不自动扩展为本轮 fixture 或新语义协议已签。未更改签署表。

## 后续逐场执行合同（待具备条件后另冻）

本文件不是新运行授权合同，也未预占 run_id。继续前需要：可验证的读取隔离环境和操作者；确定模型/provider/reasoning/sampling；固定 Skills/Memory 与时间/token/金额上限；选定新候选唯一组件、两个可触发任务和一题负对照。S11 当前任务不保证必经 PowerShell，不能凭题名算触发；S06 的语义盲点须先有人复核合同。

每场先核查冻结配置与题包哈希、启动身份对裁判及其他场的拒读、空工作区和输入来源，再 prepare；运行中保存实际模型、工具列表、cwd 与触发事件；收件后验哈希并执行 checker、人工语义/行为复核和 adjudicate。任何配置未生效或协议违反保留 invalid；证据不足保留 unknown；在合同内真实执行失败保留 fail。污染即停止余下调用，不把本地校验记为产品运行。恢复使用同一基线配置及新运行身份。
