# 从 lm-evaluation-harness 的 New Task Guide 学任务契约

> 2026-11-09 对照记录。借鉴的是评测任务的定义、版本与验证流程；本项目被测对象是带工具的 Agent 产品，不把 `lm_eval` 的语言模型接口直接套在桌面产品上。

## 一条样本从哪里来、到哪里去

| New Task Guide 中的环节 | 本项目对应物 | 可检查的问题 |
|---|---|---|
| task / dataset / split | `tasks/<批次>/<题号>/`、`inputs/` | 每场究竟用了哪份输入？是否把真值混入被测工作区？ |
| `doc_to_text` 与目标答案 | `prompt.txt`；裁判侧 `truth.json` | 产品收到的指令是否逐字一致？答案是否只在裁判侧？ |
| 模型请求接口 | CLI adapter 或桌面人工投喂 | 实际调用了哪个产品配置、权限、模型和工具？哪些状态不可见？ |
| 原始响应与过滤 | 原生会话/导出、`artifacts/` | 原始输出和落盘文件是否都保留？是否把聊天自述误当产物？ |
| `metric_list` / `process_results` | `checker.py`、`spec.md` 行为锚点、`grade.yaml` | 哪些能机械判，哪些必须人工按证据复核？ |
| task/group version 与汇总 | `task_revision`、`evaluator_revision`、`adjudicate`、`formal-report` | 判分依据能否回到运行前版本？`pending` 是否被排除？ |

官方阅读：[New Task Guide](https://github.com/EleutherAI/lm-evaluation-harness/blob/main/docs/new_task_guide.md)、[Task Configuration Guide](https://github.com/EleutherAI/lm-evaluation-harness/blob/main/docs/task_guide.md)、[Model Guide](https://github.com/EleutherAI/lm-evaluation-harness/blob/main/docs/model_guide.md)。先读任务 YAML 中的数据、提示、指标与 `metadata.version`，再读模型接口；本项目的 `prompt.txt` 与 `inputs/` 是投喂真源，`spec.md`、`truth.json` 和 checker 不能进入被测工作区。

## 已落地的最小改进

新运行的 `prepare.json`、`run.json.binding` 和收件 `manifest.json` 记录 `evaluator_revision`：由 `checker.py`、`spec.md`、`truth.json` 的内容哈希生成。`task_revision` 仍绑定题包整体，包括 prompt、输入和判分文件。这样可以分别回答“题包是什么版本”和“判分依据是什么版本”。

`collect` 在新协议中会先比较当前题包与运行前 `prepare.json` 的两个指纹；若中途改了题面、输入或评分器，就拒绝用变化后的 checker 给该场判分。旧运行的 `evaluator_revision: docs/14-v0.1` 与历史分数原样保留，不追溯替换。哈希是精确内容身份，不代替可读的修订登记；冻结规则变更仍按 `docs/03 §9` 留版本、回归和历史影响。

## S06 / S11 的实作练习

1. 读 `S06/prompt.txt`、`inputs/notes.md`、`spec.md`、`checker.py`，分别写出：被测产品看到了什么、必须交什么、checker 能验证什么、人工仍需验证什么。
2. 用 S06 的“不得增补”作反例：当前 checker 的六关键词命中不能证明没有额外事实；这部分必须在人工语义复核中明示，不能把 7/7 解释为全部合同满足。
3. 读 `S11/truth.json` 和 `checker.py`，解释为何 `filtered.csv` 中列出了正确的 A1/A3/A5，仍可能得到 0/7：产物文件名与错误报告也是合同的一部分。
4. 在一次新场的 `prepare.json`、`run.json.binding`、`manifest.json` 中核对两个 revision 和同一 `run_id`。修改评分规则前先登记新版本，不在已有运行上重算并覆盖原分。

完成本课的标准：能对 S06 或 S11 画出“输入 → 产品运行 → 原始输出 → checker / 人工复核 → 准入 → 汇总”的链条，并指出每一步的文件、版本和不可观察边界。

## 下一课：输出处理与聚合（2026-11-09）

`lm-evaluation-harness` 的 `Instance.resps` 保存原始响应，`filter_list` 将指定处理结果放到 `filtered_resps`；任务的 `metric_list` 定义如何打分，组的 `aggregate_metric_list` 再指定跨任务指标与 micro/macro 权重。这里最值得借鉴的是**每次转换都显式命名、保留原始值，并预先说明聚合单位**，而不是直接照搬文本答案抽取器。[Task Configuration Guide](https://github.com/EleutherAI/lm-evaluation-harness/blob/main/docs/task_guide.md)、[New Task Guide](https://github.com/EleutherAI/lm-evaluation-harness/blob/main/docs/new_task_guide.md)。

本项目现有链条可按下表逐段核对；表中“现状”是截至本次检查的实现，不是新增判分规则。

| 层 | 输入与处理 | 结果及边界 |
|---|---|---|
| 原始输出 | `evidence/session_export/`、归档 `artifacts/`、聊天回传 | 原件及 manifest 哈希留存；不能从最终聊天文字替换缺失的指定产物。 |
| 产物处理 | 冻结的 `checker.py` 对 `artifacts/` 检查，写 `checker_output.txt`、`score.json.raw_got/raw_full` | `run.json.evaluation.success` 当前由 checker 是否全过推导，只表示**产物契约全过**；即使 `final_ruling=pending`，它也可能已有 0/1。 |
| 行为处理 | `spec.md` 四档锚点 + 原生轨迹/可见证据，逐格记 `grade.yaml` 并由作者签认 | 观察不到的行为写未知；未签认的建议分不进入正式结论。 |
| 单场合成 | 普通题产物 `raw_got/raw_full × 6`、行为上限 4；埋雷题产物 `× 4`、行为上限 6；两项相加最多 10 | 例如 S06 DSH run4 为 4.71+1.66=6.37；S11 DSH run6 为 0+1.50=1.50。小数沿现行逐格取值记录，不重算旧场。**单场总分不等于正式准入。** |
| 准入与组汇总 | `adjudicate` 登记四门槛、证据等级及 `pass/fail/unknown/invalid`；`formal-report` 只列出正式准入场 | 当前 `formal-report` 是**准入清单**，没有实现跨题 micro/macro 均分，也没有生成产品排名；不得把“纳入场数”当成通过率。 |

下一轮若要报告跨题指标，先冻结：题目清单及版本、分析单位（一次运行还是一题）、重复场如何合成、缺失/无效场的分母、指标及权重、是否按题等权。`pending`/`unknown`/`invalid` 要分开列数，不折成 0；不同证据模式、产品表面和版本的运行先分层。现阶段正式准入场太少，保持逐场报告更诚实。

手算练习（纯示意，非本项目数据）：题 A 跑 1 次且通过，题 B 跑 3 次且均失败。按**运行等权**的 micro 通过率是 `1/4=25%`；先算每题通过率再按**题等权**的 macro 是 `(100%+0%)/2=50%`。两者回答的问题不同；埋雷题通常双跑，若直接 micro 汇总会让它比单跑题拥有更大权重，故须在运行前选定单位与权重。

## 下一轮高挑战题的筛选结论

当前 S/T 题是项目自建的机制探针，不因来源于模型就自动无效；但“设计稿写了压力”也不等于实际题包有足够压力。`docs/09` 中 S17 规划为 20 文件，现有 `tasks/second_tasks/S17-multifile-crossref/inputs/` 为 8 文件；S20 规划为约束跨多步，实际 `prompt.txt` 是一次简报整理。S12 的 `cfg→map→rows` 是顺序要求，三个文件尚未形成强制的数据依赖。这三处应视为**区分度待验证**，不能仅凭题名宣称长上下文或复杂编排能力。

建议下一轮只选两类小样本闭环：① 从现有题中优先审 S31 的三种静默数据异常、S12 的恢复行为，用于**产品行为观察**；两题先检查 checker 的正例、近错例和反向对照，S31 已被开发探针使用，不能冒充未见 holdout。`docs/18 U-08` 已指出 P8 遥测不参与决策，故 S31 不能沿旧方案用“关闭遥测”做单零件因果结论；S12 的 P6 改动也须先证明可单变量。若目标是受控换件，另核 S26/S30 的权限或沙箱接缝，并先排除 `docs/18 U-04` 的 P3/P9 耦合。② 另选一条公开、可在本项目 CLI 表面重放的**真实代码修复任务**，优先从 [Terminal-Bench](https://github.com/harbor-framework/terminal-bench) 的 Software 类任务筛选，再用 [SWE-bench Verified](https://www.swebench.com/verified) 的真实 issue 与测试补丁作为候选参照。公开题只作**外部效度补充**，记录题号、来源版本、许可证、环境镜像、时间/成本预算及可能的数据污染；先在裁判工作区证明能稳定复现、能由 oracle 判定，再新建题包版本与独立产品运行。公开榜单的分数不可与本项目 0–10 分直接合并。

筛题门槛：任务结果可由外部状态或测试验证；失败会暴露至少一个明确的 Harness 行为（例如工具调用、恢复、上下文保持）；题面和真值无歧义；正例、近错例、反向对照均能区分；本项目所测产品能在同一表面执行。先闭合 S06/S11 的终裁与十格覆盖，再决定是否正式扩题；新题的版本和预期签名应在运行前登记，不能看结果后改难度或评分器。

## 2026-11-09 路线确认与执行前提

本日复核并经用户逐格签认其余八场后，正式覆盖已到 **10/10 格、11 条准入运行**；S11 DSH 两条不同运行占同一产品格。八场原本都有 v3 `prepare.json` 和相应的原生轨迹或桌面导出证据；本次先核旧现场再终裁，没有重跑产品。详见 `reviews/十格覆盖-其余八场终裁预审-2026-11-09.md` 与 `Log-analyse/S-batch/coverage-status.md`。`lm-evaluation-harness` 继续作为方法参照，下一步只验证三件事：原始输出与处理结果能否回溯、单场分数是否与终裁分离、跨题聚合的单位/缺失口径是否预注册；不为学框架而提前做产品排行或通用聚合器。

公开代码题已选定 Terminal-Bench 2.0 的 `fix-code-vulnerability`，固定任务 commit、题面、测试与环境要求见 `experiments/external-terminal-bench-fix-code-vulnerability/plan.md`。本题使用真实 Bottle 代码库，但通过 Dockerfile 人工构造缺陷，不能外推为原生 GitHub issue。2026-11-09 Docker Desktop 恢复后，官方 oracle 对同一题重复 5 次均得 `reward=1`。前三次 Codex 产品尝试在 Agent 安装阶段无效；2026-11-10 第四次独立运行完成，官方 verifier 得 `reward=1`，预登记的 `_hval()` 补充诊断通过。该结果是一条产品配置下的外部观察，不与 S06/S11 的 0–10 分合并，也不支持稳定性或单因素因果结论。
