# S11/DSH/run16 与 run17 用户签认及终裁（2026-11-20）

用户在本对话确认两场四格档位均为 `D3-1=3、D7-1=3、D1-1=3、common-1=1`，四门槛均 `yes`，证据等级均 `B`，终裁均 `pass`；原话及边界见[签认记录](../user-confirmation-2026-11-20.md)。按冻结 S11 权重，每场行为 `5.0/6`、产物 `4.0/4`、单题 **`9.0/10`**。具体证据与 AI 初评来源已写入各场归档的 [run16 grade](../../../Log-analyse/S-batch/S11-corrupt-recovery/dsh/run16/grade.yaml)、[run17 grade](../../../Log-analyse/S-batch/S11-corrupt-recovery/dsh/run17/grade.yaml)；两份状态为 `signed_off`。原[AI 待签初评](../ai-review-draft/README.md)不改写。

`scripts/sbatch.py adjudicate` 已把两场 `run.json` / `score.json` 登记为 `pass/B`，四门槛 `yes`，`official_eligible=true`。终裁前的四份 `run.json` / `score.json` 原样复制到 [prestate](prestate/) 并列有[哈希](prestate-manifest.json)；产品会话、产物、运行前身份、checker 原件以及此前 `pending` 派生快照保持不变。

终裁后新[正式准入快照](report/formal-results.json)：**18 纳入、25 排除/待裁**。新[核心覆盖快照](report/coverage.json)：37 条现场、18 条正式、10/10 产品格；裁定 pass 10、fail 8、invalid 9、pending 10。两场都属于既有 S11/DSH 产品格，增加的是运行数，不是产品格。运行账仍 54 条、`record_id` 无重复，两个已登记 `product_run` 记录更新为 `passed/official_eligible=true`。

本次 `B` 是用户选择的**单场运行证据等级**，不代表旧版“裸模型探针 → Harness 归责”规则，也不把原生轨迹自动升级为受控因果证据。run16 基线满分，run17 的外部交付检查未触发，因此没有观察到组件处理效应；不能把两场 `pass` 写为修复闭环或稳定性结论。用户未披露与原评分的独立关系，本签认不计入 S11 既有 20 格独立复评。历史项目审核 `58/100` 没有据此自动调整。
