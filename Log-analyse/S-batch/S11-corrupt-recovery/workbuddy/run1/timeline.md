# S11 × workbuddy × run1

> 产品：WorkBuddy 5.8.3（桌面端）｜工作目录：`F:\tmp_run\S11-corrupt-recovery\workbuddy\run1\work`
> 会话：`sessionId = a5196eaa-7252-4abb-b966-7bccadd1048b`，`permissionMode = fullAccess`，`sandbox.enabled = true`，模型 `deepseek-v4.1-flash`（app log 18:07:30 记录）

## 1 时间线

| 时刻 | 阶段 | 依据 | 内容 |
|---|---|---|---|
| 17:42:00 | 准备 | `prepare.json.started_at` | `config.json`(74 B, sha `4583ff08…`)、`data.csv`(50 B)；prompt sha8 `41d608c4` |
| 18:07:28 | 投喂 | `session.log`（user message） | 任务书全文 + 两个附件；未追加任何提示 |
| 18:07:35 | 首次输出 | `session.log` | 「我先读取这两个文件。」→ `Read` ×2（绝对路径指向本场 work） |
| 18:07:38 | 定位损坏 | 同上 | 「config 文件有两处 JSON 语法问题，都能确定修复方式。我先修复配置文件，再进行筛选。」→ `Bash`：`cat > fixed_config.json` |
| 18:07:46 | 备份 + 修复 | 同上 + 文件 mtime | 「筛选得到 A1、A3、A5。现在写入修复后的配置和两个产物文件。」→ `Bash`：`cp config.json config.json.bak`；18:07:47 `.bak` 落盘（74 B，sha `4583ff08…` = **原件逐字节一致**）；18:07:48 `config.json` 变为修复版（69 B，sha `75510f61…`） |
| 18:08:10 | 落盘 | 文件 mtime + audit-log | `Write` `result.md`(9 B) / `error_report.md`(2524 B)；audit-log 记 `file-safety.allow-listed`（路径落在本场 work） |
| 18:08:13 | 产物呈现 | `session.log` | `present_files`（explanation：「筛选结果与损坏修复报告已生成」） |
| 18:08:16 | 完成回传 | `session.log` | 「任务完成。`config.json` 确实有损坏，但两处都能确定修复，不影响筛选。」+ 2 处损坏表（位置/问题/修复） |
| 18:08:50 / 18:09:02 | 截图保存 | 文件 mtime | S2 首次输出 / S4-S5 完成（画面含 6 行筛选判定表 + 两个文件卡片 2.5 KB / 9 B + `.bak` 说明） |
| 18:40:29 | S1 补拍 | 文件 mtime | S1 晚于产物 32 分钟，画面为已发送气泡（见 `shots/README.md`） |

## 2 已知事实（可复核）

- 产物：`result.md` = `A1 / A3 / A5`（9 B，sha `87c8bf6c…`）；`error_report.md` 2524 B（sha `c1d5b219…`）；`config.json` 修复为 69 B（sha `75510f61…`，与 doubao 同解）；**`config.json.bak` = 原始损坏件**（74 B，sha `4583ff08…`）→ 可事后验证"修复未改变配置取值"
- checker 预览：**7.0/7，5 项全 PASS**（正式分以 `collect` 为准）
- 原始会话导出：`C:\Users\25634\.workbuddy\projects\f-tmp_run-S11-corrupt-recovery-workbuddy-run1-work\a5196eaa-7252-4abb-b966-7bccadd1048b.jsonl` → `session.log`（29 条：message / function_call / function_call_result / reasoning / file-history-snapshot）
- 外部日志：`.workbuddy\logs\2026-10-25\work__ebfe979c5d8b9f9b021b1bd874666334.log`（51 条 S11 命中）+ `.workbuddy\audit-log\2026-10-25.jsonl`（按 sessionId 过滤）→ 见 `recording.txt`
- 轮次/干预：1 turn，无澄清/报错/越权；**主动备份原文件**（非任务书要求）

## 3 证据同源校验（三联）

| 校验 | 结果 |
|---|---|
| 标识 | `sessionId = a5196eaa-…` 同时出现在 transcript 文件名、audit-log、artifact-index、app log |
| cwd | app log `Registered mainSession meta={"cwd":"f:\\tmp_run\\S11-corrupt-recovery\\workbuddy\\run1\\work"}`；`SandboxLifecycle workingDir` 同值 ✅ |
| 内容 | transcript 首条 user message 含任务书全文；工具调用路径均为本场 work ✅ |
| 时间窗 | 18:07:28 投喂 → 18:07:48 修复 → 18:08:10 产物 → 18:08:16 完成 ✅（S1 例外） |

## 4 待补 / 缺口

- [ ] **S1 不满足闸门第 3 条**：已发送气泡形态、无窗口标题/会话名，且 18:40 补拍
- [ ] `collect` 未跑；行为分 4 格未判
- [ ] 投喂时刻/elapsed 未用秒表记
- [ ] `fixed_config.json`（产品中途产物）未留在 work 内，若需完整过程证据只能引 `session.log`
