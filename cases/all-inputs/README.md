# all-inputs — 取件处（投喂对照表）

> ⚠️ **这个文件夹是"取件处"，不是"投喂包"。**
> **千万不要把这里的文件一次性全丢进对话框** —— 那等于把 16 个用例揉成一道，产品不知道你要它做哪题，还会读到别题的文件。

## 维护须知（改前必读）

| 要点 | 说明 |
|---|---|
| **唯一真源** | `cases/<题号>/inputs/` 与 `cases/<题号>/prompt.txt`。本目录只是它们的**扁平取件副本** |
| **禁止在此编辑** | 任何内容修订都要改真源，然后重新同步本目录；直接改这里会被下次同步覆盖 |
| **两类文件别搞混** | 数据文件（`.md/.csv/.json/.txt` 附件）= 挂进对话框；`<题>_prompt.txt` = **指令原文，只能复制粘贴到正文，不能当附件挂** |
| **同步方式** | 从真源按文件名覆盖；`cases/<题号>/prompt.txt` → 本目录 `<题号>_prompt.txt` |
| **不进 git 的例外** | 本目录与真源内容一致，纳入 git 跟踪；`_archive/` 快照不跟踪 |

## 正确投喂姿势（每题重复一次）

1. **新开一个会话**（`docs/01 §6.0`：每题独立会话）
2. **只挂本题的输入文件**（下表「附件」列，1~14 个）
3. **把该题 `cases/<题号>/prompt.txt` 的文字内容复制粘贴进对话框正文** ← **这一步不能省**
4. 发送
5. **绝不投喂**：`task.md`、`spec.md`、`truth.json`、`checker.py`（泄题/泄真值）

## 为什么不能整体投喂

| 后果 | 说明 |
|---|---|
| 产品不知道做哪题 | 46 个文件混在一起，没有任务指向 |
| 会读到别题的文件 | T07 只有 1 个文件，旁边却摆着 T12 的 12 个合同，隔离全破 |
| 埋雷题失效 | T05/T06/T07/T14 考的是"能不能察觉异常"，混投后异常被淹没 |
| 指令变成素材 | 把 `*_prompt.txt` 当附件挂进去，产品可能把它当成**被处理的数据**，而不是指令 |

## 每题附件对照

| 题号 | 附件（**只挂这些**） | 个数 | 指令文字来源 |
|---|---|---|---|
| T00 hello-world | `participants.txt` | 1 | `cases/T00-hello-world/prompt.txt` |
| T00b file-format-probe | `sales.csv` | 1 | `cases/T00b-file-format-probe/prompt.txt` |
| T01 meeting-notes | `meeting_transcript.md` | 1 | `cases/T01-meeting-notes/prompt.txt` |
| T02 data-cleaning | `raw.csv` | 1 | `cases/T02-data-cleaning/prompt.txt` |
| T03 report-chain | `背景.md`、`数据.md`、`反馈.md` | 3 | `cases/T03-report-chain/prompt.txt` |
| T04 long-doc-extract | `long_doc.md` | 1 | `cases/T04-long-doc-extract/prompt.txt` |
| T05 contradiction-trap | `expenses.csv` | 1 | `cases/T05-contradiction-trap/prompt.txt` |
| T06 corrupted-input-trap | `config.json`、`data.csv` | 2 | `cases/T06-corrupted-input-trap/prompt.txt` |
| T07 privilege-trap | `records.csv` | 1 | `cases/T07-privilege-trap/prompt.txt` |
| T08 scope-constraint | `messy_notes.md` | 1 | `cases/T08-scope-constraint/prompt.txt` |
| T09 ambiguity-assumptions | `quarterly.md` | 1 | `cases/T09-ambiguity-assumptions/prompt.txt` |
| T10 decision-log | `source_notes.md` | 1 | `cases/T10-decision-log/prompt.txt` |
| T11 artifact-location | `draft.md` | 1 | `cases/T11-artifact-location/prompt.txt` |
| T12 cross-reference | `合同-A.md` ~ `合同-I.md`（9 个）、`报价单-1.md`、`备忘录-1.md`、`会议纪要-1.md` | 12 | `cases/T12-cross-reference/prompt.txt` |
| T13 proofreading | `ledger.csv` | 1 | `cases/T13-proofreading/prompt.txt` |
| T14 silent-anomaly-trap | `monthly_sales.csv` | 1 | `cases/T14-silent-anomaly-trap/prompt.txt` |

> 注：本表只列出**文件清单与指令来源**，不含真值与判分标准 —— 真值在 `cases/<题号>/truth.json`，**任何情况下都不投喂**。
