# S06-artifact-deep-path · S06 管线试点汇总

> 试点只验证流程与证据完整性，**不作五款排名**。
> 覆盖：5/5；success 仅由 checker 产物分推导，行为分另见 `grade.yaml`。

| 产品 | status | 产物分 | success | v1 | failure_code |
|---|---|---:|---:|---:|---|
| codex | scored | 7.0/7.0 | 1 | 2.68 |  |
| dsh | scored | 7.0/7.0 | 1 | 4.0 |  |
| workbuddy | scored | 7.0/7.0 | 1 | 3.67 |  |
| yuanbao | scored | 7.0/7.0 | 1 | 2.68 |  |
| doubao | scored | 7.0/7.0 | 1 | 3.0 |  |

## 证据与口径（人工补记；`summary` 重跑会覆盖本节，以 `docs/reports/阶段报告-01-2026-10-24.md` 为准）

- **覆盖 5/5**：dsh 为 **2026-10-23 23:00 重跑**（prepare 22:57:25 → 投喂 23:00 → 产物 23:00:35，产物落在 `run1/work`）；旧 dsh 现场已归档至 `dsh/prerun-2026-10-23-0246/`，**不计入本表**。
- **yuanbao**：桌面端无“工作区”选项，产物默认落沙箱 `/data/workspace`；评测者从会话文件卡片手动导出，按相对路径归档，checker 7/7。`docs/18` U-01 已结清。
- **codex** 为完整现场（prepare 早于产物，含 session.log 814 KB + 3 张截图）；**workbuddy / doubao** 为 retrofit（时间/轮次不可用，行为分依据截图与产物签认）。
- **evidence_grade**：五款均为 **C**（同题同指纹：产物分 5/5 均 7.0/7；非换件因果，不升 A/B）。
- **v1 行为分**：五款均已签认——dsh 4.0（10.0）、workbuddy 3.67（9.67）、doubao 3.0（9.0）、yuanbao 2.68（8.68）、codex 2.68（8.68）；仍是单产品单次，不得据此写“五款稳定性”或排名结论。
- **投喂偏差**：workbuddy / doubao 的 S2 显示读取仓库 `tasks/.../inputs/notes.md`（retrofit 期工作目录尚未建立）；未见读取 spec/truth，已记各自 `record_quality.feed_deviation`，不扣分。
- **产物落点差异（不影响 D2 测点）**：doubao 落产品自选根、yuanbao 落沙箱；dsh 重跑已回到 `run1/work`。三者相对路径 `输出/汇总/月报_v1.md` 均正确。
- **dsh 重跑证据**：`session.log` 为 dsh 原生事件流解压所得（56 行 JSONL：「@notes.md」投喂、6 次工具调用与结果、18.99 s turn），非转录；压缩原件 `session.v4.jsonl.zstd` 并存。**外部日志仍缺**（desktop logs 仅历史 crash 日志），`recording.txt` 已如实登记。S1 为完成态截屏（含任务书与 `用时 18 秒`），非发送前画面，且未含产品窗口标题。
