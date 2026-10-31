# S11 × doubao × run1

> 产品：豆包 2.28.13（桌面端·办公入口）｜工作目录：`F:\tmp_run\S11-corrupt-recovery\doubao\run1\work`
> **证据等级偏低**：本产品不导出会话、无本地日志（已查 `%APPDATA%\Doubao`、`~/.doubao`），时间线主要由**文件 mtime + 截图画面时间**构成，标「待补」处不可推断。

## 1 时间线

| 时刻 | 阶段 | 依据 | 内容 |
|---|---|---|---|
| 17:42:01 | 准备 | `prepare.json.started_at` | `config.json`(74 B, sha `4583ff08…`)、`data.csv`(50 B)；prompt sha8 `41d608c4` |
| 17:51 | 首次输出 | `shots/S2.png` 画面时间「今天 17:51」 | 「梳理任务执行逻辑」→「我先读取这两个文件，了解配置与数据内容。」 |
| 17:52:33 | 修复 + 落盘 | 文件 mtime | `config.json` 修复为 69 B（sha `75510f61…`，与 workbuddy 同解）；`result.md` 9 B（sha `87c8bf6c…`） |
| 17:52:54 | 报告落盘 | 文件 mtime | `error_report.md` 747 B（sha `1fc80e09…`） |
| 17:53 | 完成回传 | `shots/S4-S5.png` 画面时间「今天 17:53」 | 「任务完成，全部产物已生成并通过回读校验。」+ 处理过程 3 步 + **产物路径 `F:\tmp_run\S11-corrupt-recovery\doubao\run1\work\`** + 3 张文件卡片（result.md 9 B / error_report.md 747 B / config.json 69 B）+ 验证方式 |
| 18:02:50 / 18:03:04 / 18:03:24 | 截图保存 | 文件 mtime | S1 / S2 / S4-S5（截图晚于产物约 10 分钟） |

## 2 已知事实（可复核）

- 产物：`result.md` = `A1 / A3 / A5`（9 B，sha `87c8bf6c…`）、`error_report.md` 747 B（sha `1fc80e09…`）、`config.json` 修复为 69 B（sha `75510f61…`）
- 报告内容（截图中可见）：逐处列出第 3 行缺逗号（`Expected ',' delimiter`）、第 4 行 `mode` 尾逗号，并说明"删除该行尾逗号，`mode` 保持 `"gt"`"；声明 `threshold=10 / mode=gt` 原值不变
- checker 预览：**7.0/7，5 项全 PASS**（正式分以 `collect` 为准）
- 原始会话导出：**不可得**（`%APPDATA%\Doubao` 仅 `public_config.json`；无 `~/.doubao` 目录）→ `session.log` 写 `未提供原始会话导出（豆包桌面端无导出入口）`
- 外部日志：**未提供** → 见 `recording.txt`
- 轮次/干预：可见 1 turn，无澄清/报错/越权/权限请求

## 3 证据同源校验（三联）

| 校验 | 结果 |
|---|---|
| 标识 | ❌ 无 session id 可取（产品不暴露） |
| cwd | ✅ `S4-S5.png` 画面自带绝对路径 `F:\tmp_run\S11-corrupt-recovery\doubao\run1\work\` |
| 内容 | ✅ 画面处理过程与产物内容一致（A1/A3/A5、两处损坏） |
| 时间窗 | ✅ 17:51 首次输出 → 17:52:33/54 产物 → 17:53 完成（画面时间）；截图 mtime 18:02–18:03 |

## 4 待补 / 缺口

- [ ] **无原始会话/外部分日志**：只能靠截图 + mtime，证据等级记为 **C（单次、无原生日志）**
- [ ] **S1 不满足闸门第 3 条**：已发送气泡、无窗口标题/会话名
- [ ] `collect` 未跑；行为分 4 格未判
- [ ] 投喂时刻/elapsed 未用秒表记（首个可证时刻是 17:51 的首次输出）
