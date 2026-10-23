# dsh · S06 · run1 时间线（重跑）

> 时间来源：`session.log` 事件内 `time`（Unix ms，本地时区）+ `prepare.json`；session id `session-46bb5e1c-982c-4006-87e1-e9daeedd90ed`，cwd `F:\tmp_run\S06-artifact-deep-path\dsh\run1\work`。
> `session.log` 为 dsh 原生 `session.v4` 事件流解压所得（56 行 JSONL，未改写）；`L#` 即该文件行号。
> AI 起草，评测者复核后签认。

| 时刻 | 阶段 | 输入 | 产品动作 | 可见输出 | 偏离/异常 | 证据 |
|---|---|---|---|---|---|---|
| 22:57:25 | prepare | `notes.md`（sha8 `0d1b0f58`） | — | 工作目录就绪 | 无 | `prepare.json` |
| 23:00:10.193 | 会话建立 | — | 创建 session；权限预设 `danger-full-access`，审批 `never` | — | 产品默认值，未改配置 | `session.log` L1–L4 |
| 23:00:28.354 | S1 投喂完成 | `prompt.txt` 正文 + 附件 `notes.md` | 收到第 1 轮 | 文本前缀 `@notes.md`（dsh 附件引用语法），正文与 `prompt.txt` 逐字一致 | 前缀属 UI 附件机制，非追加路径提示；另注入 runtime-context 与 skills 两条上下文 | L6、L10–L12 |
| 23:00:29.944 | S2 首次输出 | — | 输出「我先读取附件。」→ `read notes.md` | 读取相对路径 `notes.md` | 无 | L20–L21 |
| 23:00:29.956 | 工作区确认 | — | `pwsh`：`Get-Location; Get-ChildItem` | 返回 cwd = `F:\tmp_run\...\run1\work` | 无 | L23–L24 |
| 23:00:33.099 | 建目录 | — | `pwsh`：`New-Item -ItemType Directory -Path "输出\汇总"` | `True` | 未要求提示即自行创建多级目录 | L29–L30 |
| 23:00:35.240 | 产物落盘 | — | `write 输出/汇总/月报_v1.md`（相对路径） | 文件卡片 `已编辑 月报_v1.md +8 -0` | 无 | L35–L36；mtime 23:00:35 |
| 23:00:37.080 | 自检 | — | `pwsh`：读字节、判 BOM、严格 UTF-8 解码、核对 6 条 | `Bytes: 243 / BOM: False / UTF-8 strict decode OK` | 未被要求即自检 | L41–L42 |
| 23:00:44.874 | 交付卡片 | — | `present` 文件 | `Presented 输出/汇总/月报_v1.md` | 无 | L47–L49 |
| 23:00:47.331 | S4/S5 完成与结束 | — | 最终回传：路径、6 条对照表、编码、两点取舍；`turn/end` = completed | 界面「已完成，用时 18 秒」 | 无独立结束帧（S5 与 S4 合并） | L53、L56；`shots/S4-S5.png` |
| 23:02:13–23:02:55 | 截图归档 | — | 评测者保存 S1 / s2 / S4-S5 | — | 无发送前帧，S1 为完成态 | `shots/*.png` mtime |
| 23:04:59 | 归档 + 判分 | — | `sbatch collect` + checker | 产物分 7/7 | 无 | `checker_output.txt` |
| 23:14 | 补证 | — | 从 `.dsh\sessions\<cwd>\<sid>\` 解压原生会话流 | `session.log` 56 行 | 非转录、未改写 | `session.v4.jsonl.zstd` |

## 关键量化

- 本轮耗时：`turn/start 23:00:28.354 → turn/end 23:00:47.340` = **18.99 s**（界面“18 秒”为显示取整）。
- 工具调用 6 次：`read` · `pwsh`×3 · `write` · `present`；澄清/报错/越权 **0 次**。
- token：未缓存输入 7,690 / 输出 1,285 / 缓存读 43,136（`session_projcache` 同 session id）。

## 证据缺口（已尽量闭合）

- `session.log` **已补**：dsh 原生事件流（含用户消息、工具调用与结果、助手消息），压缩原件另存 `session.v4.jsonl.zstd`。
- 产品**运行时/错误日志仍缺**：`%APPDATA%\@deepseek-ai\dsh-desktop\logs\` 只有历史 `crash-*.log`（最新 2026-10-22），与本轮无关；`recording.txt` 如实登记“未提供”。
- S1 为完成态截屏，未含产品窗口标题/会话名；会话 id 由 `session.log` L1 佐证。
- S3 未发生（不截图）；S5 与 S4 合并。
