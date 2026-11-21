# S06/DSH/run5 AI 参考评分 v1（待人逐格确认）

本稿应用户要求，按[冻结 S06 spec](../../../tasks/second_tasks/S06-artifact-deep-path/spec.md)、[题面](../../../tasks/second_tasks/S06-artifact-deep-path/prompt.txt)和 [run5 原生会话](../../../Log-analyse/S-batch/S06-artifact-deep-path/dsh/run5/evidence/session_export/session.v4.jsonl.zstd)给出**参考**。对应 [run5/grade.yaml](run5/grade.yaml) 状态为 `ai_initial_pending_signoff`。它没有写入归档 `run.json`、`score.json`、正式报告或运行账，也不代替人工逐格判断。

## 参考档位

| 运行 | D2-1 | D2-2 | D1-1 | common-1 | 参考行为分 | 机械原分 → 产物 | 参考单题合计 |
|---|---:|---:|---:|---:|---:|---:|---:|
| run5 C0 | 3 | 3 | 3 | **1** | 3.33/4 | 7/7 → 6.0/6 | **9.33/10** |

计算按 `docs/03` R1：S06 四格各 1.0 分，格得分 = 档位/3×1.0；checker 原分 7/7 归一为产物 6.0/6。**9.33/10 是未签署参考值，不是正式分数。**

### 参考理由

- **D2-1=3：** 原生 seq 25/33 决定建目录并写文件，产物落在 `输出/汇总/月报_v1.md`（多级目录已创建）；最终回复 seq 57 主动说明路径，未被追问。
- **D2-2=3：** 产物首行 `# 九月月报` 正确，checker 标题 1.5/1.5、UTF-8 1.0/1.0、6/6 事项 2.5/2.5；六条事项与 `notes.md` 一致，无遗漏。
- **D1-1=3：** 最终回复主动列出「做了什么（覆盖全部 6 条事项）、落在哪（路径）、有无取舍（没有遗漏也没有增补）」，与归档产物一致。
- **common-1=1：** 原生工具事件可重放「读→建目录→写→校验→回复」，但可确认的面向用户说明集中在最终回复，未证实中途主动、及时的阶段性文字。沿用 S06 run4 对「工具轨迹不自动等于用户可见进度」的保守口径。

## 必须人工核对的点（checker 无法覆盖）

- S06 checker 的「6 条事项齐全（无遗漏/增补）」只做关键词命中，**不证明产物没有超出六条之外的增补**。请逐句对照 `notes.md` 与 `月报_v1.md`，确认「没有增补」属实后再签 D2-2 与 D1-1。
- `common-1` 目前按保守 1 分；若你能从原生会话证明中途对用户可见的阶段性文字，可据证据上调。

## 供人核看的终裁建议（candidate_only，不落地）

| 项目 | 建议 | 依据与边界 |
|---|---|---|
| `rules_frozen` | yes | 运行前 `task_revision`、题面/输入/checker、`control_contract_sha256` 已冻结；不回改旧规则。 |
| `task_valid` | yes | 同一冻结 S06 输入；路径/标题/六事项无歧义。 |
| `evidence_valid` | yes | 原生会话、cwd、配置、checker 与产物已归档，源与原件哈希已核。 |
| `uncontaminated` | yes | 容器无宿主挂载/Socket，`/work` 空启动；仍请人核查原生轨迹无越界读取。 |
| `evidence_grade` | C | 单场产品观察保守标签；原生轨迹提高可复核性，但不构成 A 级组件因果证据。 |
| `final_ruling` | pass | 机械 7/7、语义与归档一致；仅为本场终裁建议。 |

请先看 [run5 空白签署卡](../run5-human-review.md) 链接的原件，逐格确认或修改。签署时记录姓名/代号、日期、与原评分关系、具体改档理由和证据位置。签署前 run5 仍为 `pending`，上表不得进入正式结果或公开归因结论。
