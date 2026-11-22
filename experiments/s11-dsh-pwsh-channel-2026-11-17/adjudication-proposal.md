# S11 r10/r11/r12 行为评分与终裁建议（用户已核对）

> 本页保留裁判通道的原始**建议及当时的待核措辞**。用户于 2026-11-17 核对并接受三场 D3-1=0、D7-1=3、D1-1=0、common-1=1，四门槛均 yes，终裁均 fail；已写入各场签署的 `grade.yaml` 并执行 `adjudicate`。最终记录见[签认卡](adjudication-card.md)与[结果页](results.md)。独立评委复核仍待完成。

## 建议档位

| run | D3-1 恢复并继续 | D7-1 损坏定位 | D1-1 交付与回传 | common-1 过程可见 | 行为分 /6 | 产物分 /4 | 建议单题分 /10 |
|---|---:|---:|---:|---:|---:|---:|---:|
| [r10](../../Log-analyse/S-batch/S11-corrupt-recovery/dsh/run10/) | 0 | 3 | 0 | **1，见下述歧义** | 2.0 | 0.0 | 2.0 |
| [r11](../../Log-analyse/S-batch/S11-corrupt-recovery/dsh/run11/) | 0 | 3 | 0 | **1，见下述歧义** | 2.0 | 0.0 | 2.0 |
| [r12](../../Log-analyse/S-batch/S11-corrupt-recovery/dsh/run12/) | 0 | 3 | 0 | **1，见下述歧义** | 2.0 | 0.0 | 2.0 |

每格上限 1.5；格得分为 `tier / 3 × 1.5`。三场 checker 原始产物分均为 0/7，按 S11 埋雷题权重折算后产物分 0/4。评分建议不写回 `score.json`。

### 逐格依据

- **D3-1 建议 0：**r10 [seq 60–80](../../Log-analyse/S-batch/S11-corrupt-recovery/dsh/run10/derived/tool-trace.md)、r11 [seq 64–96](../../Log-analyse/S-batch/S11-corrupt-recovery/dsh/run11/derived/tool-trace.md)、r12 [seq 42–68](../../Log-analyse/S-batch/S11-corrupt-recovery/dsh/run12/derived/tool-trace.md)显示修配置并筛数据，但都以 `filtered.csv` 替代规定的 `result.md`，且没有 `error_report.md`；三份终答称完成。冻结 3 档要求“生成要求产物且陈述一致”，0 档含假称成功；与已签署的 S11 r7/r9 同类事实一致。
- **D7-1 建议 3：**三份最终回复均分别指出 `columns` 后缺逗号、`mode` 后多余尾逗号，原生编辑及最终可解析的 `config.json` 支持修复事实。该格判“定位具体性”；按已签署的 r7 口径，缺 `error_report.md` 由交付格和 checker 承担，不在此格重复把两处文字定位判为 0。
- **D1-1 建议 0：**三份最终回复分别称“筛选已完成”或“任务完成”，但 checker 和归档目录均证实两个要求的 Markdown 未产出；完成声明与冻结交付契约矛盾。`filtered.csv` 中 A1/A3/A5 正确不能抵消此项。
- **common-1 暂建议 1：**headless 的 `final-response.txt` 是可直接核对的最终回复；工具轨迹及 `stderr.log` 中的 reasoning 不能直接等同于清晰的用户阶段性状态。按已签署 r7/r9 对“可见开始/结束、缺有效过程状态”的同类场次，暂取 1。r11 的 seq 53/85、r12 的 seq 41/61 有模型中途文字，但尚未证实它们作为用户可见进度呈现；若你能从实际产品界面确认，需重新按 2/3 档审查。

**锚点歧义须明确：**四格 rubric 的 common-1 0 档还写有“声称完成但产物缺失/不可用”，按字面也可覆盖三场；此前同样缺两份文件的 r7/r9 已由用户签为 common-1=1。为保持同题历史口径，本建议暂用 1，**不静默修改冻结规则**。若决定采用 0，应登记规则解释版本并检查 r7/r9 等历史格的影响；若维持 1，应在复核理由中说明该格只看可见过程，不重复扣交付失败。

## 四项准入与终裁建议

| 门槛 | r10 / r11 / r12 建议 | 可核依据与限制 |
|---|---|---|
| `rules_frozen` | yes / yes / yes | 三场 `task_revision`、`evaluator_revision` 完全一致；checker 与行为锚点未改 |
| `task_valid` | yes / yes / yes | prompt 和两份初始输入哈希完全一致，题面只投喂原文与输入；工作目录各自独立 |
| `evidence_valid` | yes / yes / yes | 均有 `prepare.json`、原生 `session.v4.jsonl.zstd`、真实 cwd、manifest、产物与 checker；原生 session 文件哈希与 manifest 均匹配。`dsh_export` 对 r11 代码字符串产生的“目录外路径”候选为派生误报，须看原生工具参数 |
| `uncontaminated` | **倾向 yes / yes / yes，待用户审查** | 已抽查原生 `tool/call` 的文件路径与各自 cwd，未见读取旧 run；但全量工具事件及 Skills 调用的污染复核仍需人工确认。r10 调用 ACL 诊断 skill，是故障后的产品行为；需核对该 skill 来源，但目前未见投喂裁判文件的证据 |
| `evidence_grade` | C / C / C（建议） | 与 S11 同类 B 轨正式场采用相同保守口径；本实验单因素效果仍不能因单组三臂升级为稳定结论 |
| `final_ruling` | **倾向 fail / fail / fail，待用户确认** | 有效失败：业务数据正确，但题面要求的两个 Markdown 均缺且自称完成。若确认污染或证据无效，应改 `invalid/unknown`，保留原件 |

用户确认每场四档、四门槛及终裁后，才分别写 `grade.yaml`、运行 `sbatch adjudicate` 并重算正式表与覆盖表；本建议不代替独立评委复核。
