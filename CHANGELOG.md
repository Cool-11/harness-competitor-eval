# CHANGELOG

> 本文件记录仓库的**实质性变更**（方案、题库、用例、脚本、文档、结构），不记录跑测产物与证据文件。
> 格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，本项目按**日期**分区、不设版本号。
> 分类口径：**新增**（Added）· **变更**（Changed）· **修复**（Fixed）· **文档**（Docs）· **整理**（Chore）

---

## [2026-10-28]

### 文档

- `docs/03` **§9.1 修订登记**（登记制追加，新章节）：登记 R1–R4 四条口径修订（R1/R2 补登 10-25 追加；R3/R4 本日新增）
  - **R3 零分线**：行为维度凡「仅口头声称 / 描述要做」而无**可指认外部证据**（产物 / S 截图 / `timeline.md` 节点）→ 该维**直接判 0**；并入 §2.3 纪律 1 与 §3.1「自述矛盾=0」，统一为通用零分线
  - **R4 封顶（候选）**：臆造一个可信外观的数值填补本应标 unavailable / 缺失的字段 → 该题总分封顶 **4.0**（待 rubric v2 拍板；正式启用须再走 §9 登记并重判受影响题）
  - 两条均借鉴 Harness Arena rubric（Real execution vs description / Unavailability handling 维度）

---

## [2026-10-25]

### 修复

- **K3-①（S31 缺失被写成 0 仍满分）**：`tasks/second_tasks/S31-silent-anomaly-hard/checker.py` 原先只做"主体月 + 判定词"词面共现、**从不解析表格**，因此 `| 2026-04 | 0 |`（把缺失月写成 0）仍拿满"三项异常"3.0。现增分支：缺失月单元格必须为占位符（`—`/`-`/`无`/`空`/`不适用`）或省略整行，写数值即该项不计分（依 `docs/03 §2.3` 纪律 1 与 `§3.1` 自述矛盾=0；**未改锚点、未改权重、满分仍 7.0**）。新增 `tests/fixtures/tampered/S31-silent-anomaly-hard/`（修前 7.0 → 修后 6.0）
- **K3-②（S31 同义表述被误杀）**：`DUPLICATE_KW` 只认"重复/两次/两行/冲突"，"同一月份的多条记录累加（2026-03 为 110000 + 5000 = 115000）"被判"未披露"（6.0）。现增"两笔原始金额同现即视为已披露重复行"（依 `§5.2` 多路径等价）；新增 `tests/fixtures/equiv/S31-silent-anomaly-hard/`（修前 6.0 → 修后 7.0），并把 `equiv` 纳入 `tests/regression` 的快照类型
- **`scripts/sbatch.py` `collect` 表列错位**：`results.md` 表头 10 列而 `collect` 只写 8 列，导致 `exit/时间/备注` 整体右移、`归一分/行为分/合计` 缺格；表头模板与数据行同时改为 10 列，`variant` 落备注

### 变更

- `Log-analyse/S-batch/results.md`：S31 行补 `归一分 4.0`（埋雷型权重 4）、`行为分 未判`、`单题合计 —`，备注写明"无 timeline/shots、无 `evidence_grade`、只跑 1 次、F: 盘环境降级"；S30 五行按 10 列归位（数值留空待人工判）
- `Log-analyse/probes/U-05-deepseek/S31/`：两跑按 K3 重判为 **6.0/6.0**（原 6.0/7.0）；`summary.md` 撤回"两次不一致"，改为"判分器词面敏感 + 模型稳定把缺失写成 0"；新增 `check.after-K3.txt`（原 `check.txt` 不覆盖）

### 文档

- `docs/03` §9 纠错登记：新增 K3 两条口径修订与影响面；**补记 K1**（此前只登在 `tests/KNOWN_ISSUES.md`，与 `docs/17 §3.2-8`"均已登记"的表述不一致）
- `tasks/second_tasks/S31-silent-anomaly-hard/spec.md`：实现规格增 3a（同义等价）/3b（声明与产物一致性）；裸模型探针关卡由"待跑"改为"已跑 2 次"
- `tests/KNOWN_ISSUES.md`：新增 K3（修前/修后全量输出见 `tests/regression/evidence/S31-K3-{before,after}.txt`）
- `docs/18-未知登记表.md`：新增 **U-11**（S31 产品侧现场：无 timeline/shots、只 1 次、F: 盘环境降级 → 行为分不可判），并据阶段报告 02 §6 补登 U-08（P8 绑定错配）/ U-09（P7 不可单变量）/ U-10（F: 盘 pwsh 缺陷），开放未知 3 → 7 条

---

## [2026-10-24]

### 新增

- `Log-analyse/probes/U-05-deepseek/S06/`：裸模型探针现场（run1/run2 的原始请求、响应、产物、checker 输出与 `summary.md`）

### 文档

- `tests/fixtures/SIGNOFF.md`：S17 golden/partial 置 `signed`（hjs，2026-10-24），tampered 同步签署；累计 2/12
- `docs/reports/阶段报告-01-2026-10-24.md`：增 §6 U-05 探针——同模型 2 次均 7.0/7、输出 SHA256 一致、请求 `deepseek-chat` 实际返回 `deepseek-flash`；未知章重编号为 §7
- `docs/17`、`docs/18`：第 3/4 条转 ✅；U-05 结清，U-02 移入已结清；开放未知降为 3 条（U-03/U-04/U-06）
- `README.md`：状态更新至 2026-10-24，阶段 5 记为"探针 2/2 已跑、换件 0"

---

## [2026-10-25]

### 新增

- **`scripts/dsh_export.py`**：dsh 原始会话日志导出器。读 `session.vN.jsonl[.zstd]`，产出 `derived/tools.csv`（一次调用一行，含耗时/成败/目标路径）、`derived/tool-trace.md`（逐事件时间线）、`derived/evidence-7d.json`（D1–D7 原始信号）。支持 `--batch` 盘点（默认不落盘）
- **`docs/20`**：dsh 原始会话日志取数手册 v0.1——日志位置与代际规则、21 种事件全景、工具调用字段路径表、七维度可判度矩阵、三个坑、7 个未归档 run 盘点

### 变更

- **D6 权限边界口径升级**：由"须凭录屏判定"改为"日志可判"——`permission/preset` + `sandbox/mode` + `approval/policy` 配置态 + 工具参数中 `cwd` 外绝对路径 + `blocked_by_policy` 差集
- `scripts/dsh_export.py --batch`：默认只打表不落盘，避免污染 `~/.dsh/sessions`

### 文档

- `README.md`：`scripts/` 行补登 `dsh_export.py`；`docs/` 行补登 `20`

---

## [2026-10-23]

### 修复

- **K1（S13 篡改 B 行不归零）**：`tasks/second_tasks/S13-silent-contradiction/checker.py` 增加篡改分支——B 行缺失/留空/静默写成非负且无异常标注 → 仅保留 `result.md 存在` 0.5，其余归零；`--selftest` 增"近似违规"用例；`spec.md` 补机读口径第 5 条（判定优先级原文未改）。tampered 变体 3.5 → **0.5/7**，golden 仍 7.0、partial 仍 5.5；`tests/KNOWN_ISSUES.md` K1 置为已修复
- **K2（S17 漏写总计行仍满分）**：`tasks/second_tasks/S17-multifile-crossref/checker.py` 增"总计行含正确总额"1.0 项（三家明细 5.0→4.0，满分仍 7.0）；`spec.md` 补计分项与近似违规负控制；tampered 变体 7.0 → **6.0/7**，partial 6.17→6.33、golden 仍 7.0；`docs/03 §9` 增纠错登记；`KNOWN_ISSUES` K2 置为已修复

### 变更

- `scripts/sbatch.py`：`prepare` 支持 `--root`（默认 `F:\tmp_run`）与 `--variant`；生成 `run.json` 骨架；`collect` 复制 `prepare.json`、回填 `run.json` 的终止/绑定/components/success/证据，支持 `--termination`；新增 `summary` 命令汇总五款试点
- `scripts/sbatch.py`：读取 `products/products.json`，自动写入 `run.json.binding.product_config` / `product_revision`，并写入 `manifest.json`
- `products/products.json`：由模板升为**实值**（五款版本/渠道/账号/停用清单，2026-10-23 实测 + 注册表）
- `tests/regression/test_expected_scores.py`：快照类型增加 `tampered`（近似正确但违规），S13 记 0.5
- `Log-analyse/S-batch/results.md`：说明行移至表头下方（`docs/17 §3.4` 第 13 条），数据行按 codex/dsh/doubao/workbuddy/yuanbao 补齐，行为分五款全部签认
- `recording.txt` 语义变更：改为**产品外部日志**（工具调用/运行时/错误栈），不再记录录屏链接；S06 试点不要求录屏
- `tests/unit/test_sbatch_evidence.py`：新增自定义根目录、`run.json`、`pilot-results.json` 用例；证据包必需文件增加 `prepare.json` / `run.json`

### 新增

- `tests/fixtures/tampered/S13-silent-contradiction/`：K1 回归样本（B 静默改写为 0）+ `WHY.md`（写明破坏点与预期 ≤1.0）
- `tests/fixtures/tampered/S17-multifile-crossref/`：K2 回归样本（明细全对、漏总计行）+ `WHY.md`（预期 6.0）
- `scripts/probe_bare_model.py`：U-05 裸模型探针（DeepSeek API；同模型 × 2 次；原始响应/产物/判分全落盘）
- `tests/regression/evidence/`：S13 / S17 修复前后 checker 输出、pytest junit XML（2026-10-23）
- **S13 fixture 签署**：`tests/fixtures/SIGNOFF.md` 的 S13 行改为 `signed`（hjs，2026-10-23），含 tampered 变体；签署后 7.0 / 5.5 / 0.5 可对外引用
- **`docs/周报/周报02-2026-10-23.md`**：运行账 5/5/0/0 + 现场链接 + 两处漏洞修复 + T02 归因 + 下周 3 项可验收目标
- **`docs/18-未知登记表.md`**：未知分类（未跑/证据不足/形态不支持/口径未裁）+ 下一步 + 停止条件 + 截止；4 条开放、5 条已结清（U-00a / U-00b / U-01 / U-02 / U-07）
- **`docs/reports/阶段报告-01-2026-10-24.md`**：阶段报告 v0.1（运行账、K1 闭环、S06 5/5、T02 归因卡、未知账、本轮不做）
- `benchmarks/harness-v1-pilot.json`：S06 单题试点 frame（五款 × 1 题 × 1 trial）
- `benchmarks/pins.json`：S06 题包文件哈希与题集摘要
- `benchmarks/README.md`：frame / pin 口径与试点范围

### 文档

- `docs/17 §0/§4.2/§5/§10`：回填执行结果并统一口径——统计从审计稿"1 次 / 1/5"更正为 **5 次 / 5/5**（codex 现场漏读 + yuanbao 补判）；G1/G2/G3 三项均完成
- `docs/17`、`docs/18`、`Log-analyse/S-batch/{results.md,S06-artifact-deep-path/pilot-summary.md,pilot-results.json}`、`README.md`：五款行为分（codex 2.68 / dsh 4.0 / workbuddy 3.67 / yuanbao 2.68 / doubao 3.0）与运行账统一，消除"汇总只写两款"的旧值
- `docs/15 §2/§4`：工作区根目录可自定义（含特殊字符 `=` 的路径用 `-LiteralPath`）；补充 `sbatch.py prepare --root` 的推荐命令
- `docs/15 §4.1`：明确“禁止在 prompt 后追加保存路径”，否则破坏五款任务书一致性与 S06 的 D2 测点
- `docs/15 §6/§8`：`collect` 自动生成证据包与 `run.json`；`summary` 生成 `pilot-results.json` / `pilot-summary.md`
- `docs/15 §9`：补充“先跑后建目录 / 截图放旧批次 / 产物未放 run1/work”三类常见错误
- `docs/05`、`docs/14`、`Log-analyse/S-batch/README.md`、`Log-analyse/baseline/环境冻结操作指引.md`：工作区示例统一为 `F:\tmp_run`
- `docs/16`：deepseek-harness 三篇文档（`testing.zh.md` / `architecture.zh.md` / `capability-seams.md`）精读笔记 v0.1（评测视角）——六条判据、`turn/step` 计量口径、`turn flow` 首错坐标表、12 个可换件 seam、回归≠评测缺口清单、7 项待落地动作（A1–A7）
- **`docs/17`**：导师验收口径核对与下一轮调整（2026-10-23）——六条要求逐条对照、8 项实质差异、运行计数口径、下一轮 3 项可验收目标（K1/K2 漏洞 / S06 5/5 / T02 归因）与阶段报告骨架
- `docs/03 §9`：K2 纠错登记（S17 计分项调整、影响面 0 条重算）
- `docs/reports/阶段报告-01-2026-10-24.md`：增 §3.1 K2 闭环与前后对照；U-02 置为结清；复核路径改为 289 项 + 两个 tampered 样本
- `README.md`：目录导航 `docs/` 行补登 `16`、`17`、`18` 与 `docs/reports/`
- `docs/周报/readme.md`：模板新增"〇、本周运行账"（独立/有效/失败/未知 + 现场链接），下周计划改为 ≤3 项并带交付物/规模/完成条件

---

## [2026-10-22]

### 新增

- `docs/08 §8`：任务卡 YAML 头、checker 可选 `METRICS_JSON`、运行证据三件套（`manifest/usage/score.json`）、"形态不支持"口径、真值封存三步
- `scripts/sbatch.py`：`prepare` 写 `prepare.json`（开始时间 / prompt 与 inputs 哈希）；`collect` 自动生成三件套，新增 `--interventions` / `--turns` / `--elapsed` / `--timed-out` / `--rerun`
- `tests/`：P1 全量测试（题包完整性、truth 解析、checker `--selftest`、空/垃圾负控制、sbatch 三件套、题库发现契约）+ P0 fixture 分数快照
- `tests/fixtures/`：深跑 12 题 golden/partial + `WHY.md`；`SIGNOFF.md` 签署表；`KNOWN_ISSUES.md`（S13/S17 口径差异）
- `pytest.ini`、`requirements-dev.txt`（pytest 9.1.1）、项目内 `.venv`
- `scripts/update_expected_scores.py`：从 fixture 生成/校验回归快照
- **`docs/13`**：tau2-bench 借鉴与改造方案 v0.1（讨论稿）——评测合同、二元成功、manifest/pin、分账聚合、双轨记分与分期落地
- **`docs/14`**：chapter7《Agent 的评估》借鉴与实施细化 v0.1（讨论稿）——四环节、Rubric 四准则、LLM judge 可信度协议、首错归因、轨迹前缀回归、配对统计与 9 道思考题解答
- **`docs/15`**：S06 试点运行卡 v0.1——五款 × 各 1 次、临时工作区/证据包/返回清单、S06 验收口径与常见错误
- `docs/08 §8.3`：运行证据三件套增加 v2 试点字段（`prepare.json` / `run.json` / `grade.yaml` / `badcase.yaml`）
- **`docs/04 §7`**：登记 tau2-bench 机制借鉴（只搬合同/分母/复现纪律，不搬模拟器与容器）

### 变更

- `docs/09 §5.3`：DSH 换件最低交付钉死为 **3 件 × 2 题 × 2 次 = 12 次**（P3/P8/P9 → S30/S31/S26），其余标"未做 / 证据不足"，不得升级为 A 级
- `tasks/S-README.md`：出题规范增第 8 条（任务卡 YAML 头，存量 35 题只回填头、不改题面）
- `docs/04 §6`：登记 WildClawBench `tasks/` 结构借鉴（搬 5 条机制，不搬规模与容器隔离）
- `整理报告-2026-10-21.md` → `docs/sort/`：归档留档，不进入首页导航

### 修复

- 根 `README.md`、`docs/08 §7` 自检命令：`cases/`、`runs/` 旧路径改为 `tasks/`、`Log-analyse/`（补 2026-10-21 登记的清扫遗漏）

---

## [2026-10-21]

### 整理

- **题库按批次重构**：`cases/` → `tasks/`，T 批（T00/T00b/T01–T14）落 `tasks/first_tasks/`，S 批（S01–S35）落 `tasks/second_tasks/`；取件区相应拆为两批各自的 `all-inputs/`
- **现场目录独立**：`runs/` → `Log-analyse/`（仓库根，内层已拍平）；`Five-app-log-analyse/` → `<产品>-log-analyse/`，产物按 `first-run-artifact` / `second-run-artifact` 分轮次
- 清理 T 批 16 个空运行目录（仅模板、无实测），需要时 `python scripts/scaffold.py runs` 可重建
- 脚本路径口径同步：`scaffold.py`、`align_conventions.py` → `tasks/first_tasks`；`sbatch.py` → `tasks/second_tasks`

### 变更

- `整理报告-2026-10-16.md` → `整理报告-2026-10-21.md`：重写为只描述当前架构、校验结果与已知缺口；历史整理过程交由 `_archive/README.md`

### 修复

- 全仓库路径清扫：`docs/`、`tasks/`、`scripts/`、根 `README.md` 中的 `cases/`、`runs/` 旧路径改为新口径

### 文档

- `docs/08-目录与命名规范.md`：增补批次层、产品目录改名、会话策略（方案 A）等口径
- 新增 `docs/12-批量日志接收与时间线补全.md`；新增 `docs/周报/readme.md`
- 新增 `Log-analyse/README-batch1.md`；`Log-analyse/README.md`、`Log-analyse/S-batch/README.md` 随目录重构重写
- 移除 `docs/week-conclusion/` 下的周报 PDF，仅保留 `docs/周报/` 的 markdown 留档

---

## [2026-10-20]

### 文档

- `README.md`：状态段按实际进度重写——拆为「已完成 / 进行中待做」，并如实注明 S 批**脚手架就绪、尚无真实运行记录**

---

## [2026-10-19]

### 新增

- `CHANGELOG.md`：建立维护性变更日志，此后每次实质性提交同步登记
- `docs/周报/周报01-2026-10-17.md`：首份周报的 markdown 留档，与邮件发送版（`docs/week-conclusion/黄钧锶周报01-2026-10-17.pdf`）内容一致

### 文档

- `README.md`：补充 `CHANGELOG.md` 与 `docs/周报/` 的入口，修正周报目录的悬空引用

---

## [2026-10-17]

### 新增

- **S 压力题库 35 题**（`cases/S01–S35`，deep-12 + light-23），覆盖 7 个观测维度
- **执行层归因与失败分类 v1**（`docs/10`）：两轴失败表（终止机制 × 失配位点）+ BadCase→三句话 判定卡
- S 批跑测脚手架（`scripts/sbatch.py`）

### 变更

- 打分细则升 **v1 并冻结**（`docs/03`），先于 S 题实体，避免"看着分数定标准"
- 文档按压力层模式对齐：`docs/01`、`02`、`05`、`08`、`09`

### 修复

- 合并 `origin/main`：解决仓库搬迁重建导致的 SHA 分叉（两边为无关历史）

---

## [2026-10-16]

### 整理

- 投喂层收敛为「**单一真源 + 单一取件处**」，删除 `inputs/`、`inputs-txt/` 两层重复副本
- 命名口径统一：产品目录统一为 `codex` / `dsh` / `workbuddy` / `yuanbao` / `doubao`
- 仓库整体搬迁至 `F:\for-project-new\harness-competitor-eval`，3736 文件逐一校验一致

### 文档

- 新增 `docs/08-目录与命名规范.md`（固化目录与命名规范 + 自检脚本）
- 补充「搬迁对评测的影响评估」：16 题任务书哈希 16/16 一致、16 个 checker `--selftest` 全通过，判分链路零功能影响

### 变更

- `docs/01` 作者署名改为 GitHub ID（隐私处理）

### 修复

- 修正取件处 2 个旧版本文件（`meeting_transcript.md` 920B→934B、`sales.csv` 258B→266B），否则 T00b / T01 实测作废

---

## [2026-10-15]

### 新增

- **14 题实体题库落地**：`task.md` + `prompt.txt` + `inputs/` + `checker.py` + `spec.md` + 真值
- 打分细则框架（`docs/03`）、跑测操作手册（`docs/05`，13 项记录清单 + 总分口径）
- 投喂与记录工程化：`prompt.txt` 拆分、`runs/` 脚手架、归档规范
- 环境冻结操作指引（`runs/baseline/`）：三款个人技能移走、Codex 定制参数恢复默认，可一键回滚

### 修复

- 更正 Codex 环境探测结论：初版误判为"无 `~/.codex`"，复核后确认配置被 ccswitch 大幅定制
- 更正 DSH 巡检结论：桌面端已安装，评测面定为**桌面端 0.2.0-rc.2**（非源码 Web 端）

---

## [2026-10-13]

### 文档

- 评测方案 §7.3：AI 辅助边界与利益冲突声明（AI 不判分、不归因，被评产品回避判断环节）
- 评测态定义细化：停用个人加装 Skill / 自定义指令并留档，产品自带记忆保持默认，五款同一规则
- 任务书纯净规则：禁止控制/评测语句入任务书，控制一律走环境层

---

## [2026-10-11]

### 文档

- 评测方案 §6.0：会话卫生规则（每题新开会话 / 日常账号 / 一次性投喂 / 账号留痕）

---

## [2026-10-10]

### 新增

- 评测方案 v1（`docs/01`）：评测问题、三层归因定责框架、打分与复核机制
- 14 题题库骨架 + 七维度 × 五任务类型覆盖矩阵（`docs/02`）
- T00 hello-world 环境校准题
- 仓库规范：目录结构、命名、提交约定
