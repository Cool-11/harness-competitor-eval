# S11/DSH/run16 人工复核与终裁卡（待填写）

此卡只对应 `hev-20261120T214236+0800-S11-dsh-r16-36035514`。填写人需先核看下列原件；本卡不预填行为分、签名或终裁结果。机械 `7/7` 不自动等于语义通过或正式准入。

用户要求的[AI 参考评分](ai-review-draft/run16/grade.yaml)已另存，状态为 `ai_initial_pending_signoff`；仅供核对，不替代你逐格判断。

## 原件入口与已核实的机械事实

- 冻结题面：[prompt.txt](../../tasks/second_tasks/S11-corrupt-recovery/prompt.txt)；行为锚点：[S11 rubric](../../reviews/S11-round1-2026-11-06/reviewer/rubric.md)；题目规格：[spec.md](../../tasks/second_tasks/S11-corrupt-recovery/spec.md)。这些仅供裁判查看，不曾投喂产品。
- 运行前身份：[prepare.json](../../Log-analyse/S-batch/S11-corrupt-recovery/dsh/run16/prepare.json)；运行与采集：[run.json](../../Log-analyse/S-batch/S11-corrupt-recovery/dsh/run16/run.json)、[manifest.json](../../Log-analyse/S-batch/S11-corrupt-recovery/dsh/run16/manifest.json)。
- 产物：[result.md](../../Log-analyse/S-batch/S11-corrupt-recovery/dsh/run16/artifacts/result.md)、[error_report.md](../../Log-analyse/S-batch/S11-corrupt-recovery/dsh/run16/artifacts/error_report.md)、[config.json](../../Log-analyse/S-batch/S11-corrupt-recovery/dsh/run16/artifacts/config.json)；[checker 原始输出](../../Log-analyse/S-batch/S11-corrupt-recovery/dsh/run16/checker_output.txt)为 `7/7`。
- 过程：[原生会话](../../Log-analyse/S-batch/S11-corrupt-recovery/dsh/run16/evidence/session_export/session.v4.jsonl.zstd)及从同一会话提取的[工具事件索引](execution-01/tool-trace.json)。逐项检查错误识别、实际修复、继续筛选和交付陈述；不要只按产物给过程分。
- [容器隔离证据](execution-01/evidence/run16/container-isolation.json)及[证据哈希清单](execution-01/runtime-evidence-manifest.json)供核对未受污染、工作目录及原件完整性。

## 请填写行为分

每格填 `0`、`1`、`2`、`3` 或 `abstain`；引用具体文件、工具事件序号及理由。`abstain` 说明缺失或冲突的证据。锚点以链接的冻结 rubric 为准。

| 格位 | 档位 | 直接证据和理由 |
|---|---|---|
| D3-1 错误恢复并继续任务 | 待填写 | 待填写 |
| D7-1 错误报告具体性 | 待填写 | 待填写 |
| D1-1 结果交付完整性 | 待填写 | 待填写 |
| common-1 过程可观察性 | 待填写 | 待填写 |

## 请填写终裁门槛

每项填 `yes`、`no` 或 `unknown`，引用证据。`final_ruling` 填 `pass`、`fail`、`unknown` 或 `invalid`；不确定不折算为失败。`evidence_grade` 填 `A`、`B`、`C` 或 `N`，并说明依据。只有四项均为 `yes`、终裁为 `pass/fail`、证据等级为 `A/B/C`，管线才可能纳入正式比较。

| 项目 | 判断 | 证据和理由 |
|---|---|---|
| rules_frozen | 待填写 | 待填写 |
| task_valid | 待填写 | 待填写 |
| evidence_valid | 待填写 | 待填写 |
| uncontaminated | 待填写 | 待填写 |
| evidence_grade | 待填写 | 待填写 |
| final_ruling | 待填写 | 待填写 |

复核人署名或可识别代号：待填写  
复核日期（Asia/Shanghai）：待填写  
是否参与本题题面、checker、rubric 或旧评分制作：待填写  
是否提前见过本场 checker 分及旧 S11 判分：待填写  
其他限制、分歧或弃权原因：待填写

签署后，将填写完成的卡作为新文件保存并保留此空白原件。协调者据签署内容调用 `scripts/sbatch.py adjudicate`；不得由编程 Agent 推断或代填。此单场复核不自动完成既有 [S11 独立 20 格复评](../../reviews/S11-independent-recheck-2026-11-17/README.md)，也不补成未执行的 C1/恢复臂。
