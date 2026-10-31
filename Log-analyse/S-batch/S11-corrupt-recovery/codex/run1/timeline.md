# S11 × codex × run1

> 产品：OpenAI Codex 桌面端 26.1016.8622.0（`products/products.json`）
> 题：S11-corrupt-recovery（主 D3 失败恢复 / 副 D7 可观测性）｜工作目录：`F:\tmp_run\S11-corrupt-recovery\codex\run1\work`
> 本文件按 `docs/19 §5` 生成：**只有文件 mtime / 会话日志 / 截图能证的才写，其余标「待补」，不推断**。

## 1 时间线

| 时刻 | 阶段 | 依据 | 内容 |
|---|---|---|---|
| 17:42:00 | 准备 | `prepare.json.started_at` | 建 work，投入 `config.json`(74 B, sha `4583ff08…`)、`data.csv`(50 B, sha `fd668362…`)；prompt sha8 `41d608c4` |
| 18:18:52 | 会话开始 | `session.log` 首行 `session_meta.payload.timestamp` | 新会话，`cwd` = 本场 work；未追加任何路径/提示 |
| 18:18:56 | 首次输出 | `session.log` assistant | 「我会先检查配置文件的原始内容和语法位置，再修复能确定的损坏点，随后按 `amount > threshold` 筛选并核对输出。」 |
| 18:19:01 | 定位损坏 | 同上 | 「已定位到 `config.json` 的两处确定语法问题：`columns` 数组后缺少逗号，`mode` 值后存在多余的尾逗号。」 |
| 18:19:02 | 修复落盘 | 文件 mtime | `config.json` 就地修复（74 B → 74 B，sha `53bf0176…`：加逗号 + 删尾逗号净长度不变）；写出 `result.md`(9 B)、`error_report.md`(285 B) |
| 18:19:13 | 自查 | `session.log` | 「筛选结果已通过程序化比对验证…现在做最后的文件内容核对。」 |
| 18:19:18 | 完成回传 | `session.log` | 「任务已完成。」+ 两个产物的**绝对路径链接**（`F:/tmp_run/.../result.md`、`error_report.md`），说明保留 `amount > 10` 的 3 行 |
| 18:25:19 / 18:25:32 | 截图保存 | 文件 mtime | S2 首次输出 / S4-S5 完成 |
| 18:40:05 | S1 补拍 | 文件 mtime | S1 保存时间晚于产物 21 分钟，画面为**已发送气泡**（见 §4） |

## 2 已知事实（可复核）

- 产物：`result.md` = `A1 / A3 / A5`（9 B，sha `87c8bf6c…`）；`error_report.md` 285 B（sha `3bd2ae85…`）；`config.json` 已修复（sha `53bf0176…`，与 dsh 同解）
- checker 预览（评测者手动跑）：**7.0/7，5 项全 PASS**；正式分以 `collect` 输出的 `checker_output.txt` 为准
- 原始会话导出：`C:\Users\25634\.codex\sessions\2026\10\25\rollout-2026-10-25T18-18-52-01a17291-fb44-7e70-a295-c6065727fe72.jsonl` → `session.log`（71 条事件）
- 外部日志：**未提供**（桌面端不导出终端日志；`~/.codex/.sandbox/sandbox.2026-10-25.log` 对 `S11-corrupt` 0 命中）→ 见 `recording.txt`
- 会话轮次/干预：1 turn；无澄清、报错、越权、权限请求（`interventions` 待评测者签认）

## 3 证据同源校验（三联）

| 校验 | 结果 |
|---|---|
| 标识 | `session_id = 01a17291-fb44-7e70-a295-c6065727fe72`，同时出现在文件名与 `session_meta` |
| cwd | 首行 `payload.cwd` = `F:\tmp_run\S11-corrupt-recovery\codex\run1\work` ✅ |
| 内容 | 会话内含任务书全文（`请完成一个数据筛选任务`）✅ |
| 时间窗 | 会话 18:18:52 → 产物 18:19:02 → 完成语 18:19:18 ✅（S1 例外：18:40 补拍） |

## 4 待补 / 缺口

- [ ] **S1 不满足闸门第 3 条**：画面是已发送气泡（18:18）+ 两个附件 chip，**没有窗口标题/会话名**；且 mtime 晚于产物 → 不能证"发送前"
- [ ] `collect` 未跑：产物分/归一分/结果表行尚未写
- [ ] 行为分 4 格（D3-1 / D7-1 / D1-1 / common-1）未判
- [ ] 投喂时刻与 `elapsed` 未用秒表记（`prepare.started_at` 不能替代）
