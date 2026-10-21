# CHANGELOG

> 本文件记录仓库的**实质性变更**（方案、题库、用例、脚本、文档、结构），不记录跑测产物与证据文件。
> 格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，本项目按**日期**分区、不设版本号。
> 分类口径：**新增**（Added）· **变更**（Changed）· **修复**（Fixed）· **文档**（Docs）· **整理**（Chore）

---

## [2026-10-21]

### 整理

- **题库按批次重构**：`cases/` → `tasks/`，T 批（T00/T00b/T01–T14）落 `tasks/first_tasks/`，S 批（S01–S35）落 `tasks/second_tasks/`；取件区相应拆为两批各自的 `all-inputs/`
- **现场目录独立**：`runs/` → `Log-analyse/`（仓库根，内层已拍平）；`Five-app-log-analyse/` → `<产品>-log-analyse/`，产物按 `first-run-artifact` / `second-run-artifact` 分轮次
- 清理 T 批 16 个空运行目录（仅模板、无实测），需要时 `python scripts/scaffold.py runs` 可重建
- 脚本路径口径同步：`scaffold.py`、`align_conventions.py` → `tasks/first_tasks`；`sbatch.py` → `tasks/second_tasks`

### 变更

- `整理报告-2026-10-16.md` 校订：导航路径改为现状口径、关闭已完成遗留项、补记本次重构（§九）

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
