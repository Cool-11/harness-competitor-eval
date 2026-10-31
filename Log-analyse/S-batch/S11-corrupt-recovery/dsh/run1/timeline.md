# S11 × dsh × run1

> 产品：DeepSeek Harness 0.2.0-rc.2（桌面端/本地源码）｜工作目录：`F:\tmp_run\S11-corrupt-recovery\dsh\run1\work`
> **本场特殊**：跑在 F: 盘（`docs/18 U-10`）；但会话以 `danger-full-access` 预设启动，`pwsh` 两次调用**均成功**（见 §2），故本题未被环境降级。

## 1 时间线

| 时刻 | 阶段 | 依据 | 内容 |
|---|---|---|---|
| 17:42:00 | 准备 | `prepare.json.started_at` | work 内 `config.json`(74 B, sha `4583ff08…`)、`data.csv`(50 B)；prompt sha8 `41d608c4` |
| 18:23:54 | 会话开始 | `session.log` 首行 `createdAt`/`cwd` | `cwd` = 本场 work；`permission/preset = danger-full-access`、`sandbox/mode = danger-full-access`、`approval/policy = never` |
| 18:24:10 | 首次输出 | `session.log` assistant | 「I'll start by inspecting the two input files.」→ `read` ×2（config.json / data.csv） |
| 18:24:12 | 定位损坏 | 同上 | 「Both input files read. `config.json` has two clear JSON syntax errors. Let me fix them minimally and verify with a parser.」→ `edit` |
| 18:24:13 | 校验修复 | `tool/call` | `pwsh`：`python -c "json.load(...)"` → **成功**返回 `{'threshold': 10, 'columns': ['id','amount'], 'mode': 'gt'}` 与 `['A1','A3','A5']` |
| 18:24:19 | 落盘 | 文件 mtime | `write` ×2 → `result.md`(9 B)、`error_report.md`(2008 B)；`config.json` 已修复（74 B，sha `53bf0176…`） |
| 18:24:20 | 自查 | `tool/call` | `pwsh`：回读 config / `Get-Content result.md` / `Get-ChildItem` → 成功 |
| 18:24:22–18:24:25 | 完成回传 | `session.log` | `present` 两张产物；「任务完成。」+ 损坏与修复对照表（2 处、含行号/字段） |

## 2 已知事实（可复核）

- 产物：`result.md` = `A1 / A3 / A5`（9 B，sha `87c8bf6c…`）、`error_report.md` 2008 B（sha `47c63fe2…`）、`config.json` 已修复（sha `53bf0176…`）
- checker 预览：**7.0/7，5 项全 PASS**（正式分以 `collect` 为准）
- 原始会话：`%USERPROFILE%\.dsh\sessions\--F-tmp_run-S11-corrupt-recovery-dsh-run1-work--\session-956a7b07-87c1-4c66-a8cb-b11516637a97\session.v4.jsonl.zstd` → `session.log`（64 条原生事件，`zstd -d` 解压）
- 外部日志：**未提供**（无独立 app log）→ 见 `recording.txt`
- **F: 盘与 U-10 的关系**：本场 `pwsh` 通道可用（两次调用均返回正常结果），说明 U-10 的 `grantWrite` 失败发生在**沙箱模式**下，`danger-full-access` 不经过该 ACL 授权 → 本题不受影响；结论不外推到沙箱模式的场次

## 3 证据同源校验（三联）

| 校验 | 结果 |
|---|---|
| 标识 | `session-956a7b07-…`；会话目录名即 cwd 转义 `--F-tmp_run-S11-corrupt-recovery-dsh-run1-work--` |
| cwd | 首行 `cwd` = 本场 work ✅ |
| 内容 | 首条 user 消息 = 任务书全文（sha8 `41d608c4`）✅ |
| 时间窗 | 18:23:54 → 产物 18:24:19 → 完成 18:24:25 ✅ |

## 4 待补 / 缺口

- [ ] **现场修正记录**：`run1/work` 曾被挪进 `shots/work`，2026-10-25 由评测者移回 `dsh/run1/work`（文件 mtime 未变，内容 sha 未变）
- [ ] **S1 不满足闸门第 3 条**：画面为已发送气泡（18:24）+ 附件 chip，无窗口标题/会话名
- [ ] `collect` 未跑；行为分 4 格未判
- [ ] 投喂时刻/elapsed 未用秒表记
