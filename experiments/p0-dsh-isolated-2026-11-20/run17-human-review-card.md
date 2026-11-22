# S11/DSH/run17 人工复核与终裁卡（待填写）

唯一运行身份 `hev-20261120T221915+0800-S11-dsh-r17-b058e4a8`。此卡仅供人核看原件后填写，不预填行为分、签名或终裁。机械 `7/7` 不自动等于语义通过。

用户要求的[AI 参考评分](ai-review-draft/run17/grade.yaml)已另存，状态为 `ai_initial_pending_signoff`；仅供核对，不替代你逐格判断。

冻结[题面](../../tasks/second_tasks/S11-corrupt-recovery/prompt.txt)、[spec](../../tasks/second_tasks/S11-corrupt-recovery/spec.md)和[四格 rubric](../../reviews/S11-round1-2026-11-06/reviewer/rubric.md)供裁判查看。实际[运行前身份](../../Log-analyse/S-batch/S11-corrupt-recovery/dsh/run17/prepare.json)、[运行记录](../../Log-analyse/S-batch/S11-corrupt-recovery/dsh/run17/run.json)、[归档清单](../../Log-analyse/S-batch/S11-corrupt-recovery/dsh/run17/manifest.json)、[checker 输出](../../Log-analyse/S-batch/S11-corrupt-recovery/dsh/run17/checker_output.txt)、[产物目录](../../Log-analyse/S-batch/S11-corrupt-recovery/dsh/run17/artifacts/)和[原生会话](../../Log-analyse/S-batch/S11-corrupt-recovery/dsh/run17/evidence/session_export/session.v4.jsonl.zstd)均已保存。可用[工具事件索引](execution-02/tool-trace.json)定位具体动作，用[容器隔离证据](execution-02/evidence/run17/container-isolation.json)与[哈希清单](execution-02/runtime-evidence-manifest.json)复核原件。

客观记录：首次结束时两份要求文件齐全，`missing_initial=[]`，外部交付检查未触发；checker `7/7`。这些不代替人工过程和语义判分。

| 格位 | 档位：0/1/2/3/abstain | 直接证据、理由或弃权原因 |
|---|---|---|
| D3-1 错误恢复并继续任务 | 待填写 | 待填写 |
| D7-1 错误报告具体性 | 待填写 | 待填写 |
| D1-1 结果交付完整性 | 待填写 | 待填写 |
| common-1 过程可观察性 | 待填写 | 待填写 |

| 终裁项 | yes/no/unknown 或指定枚举 | 直接证据和理由 |
|---|---|---|
| rules_frozen | 待填写 | 待填写 |
| task_valid | 待填写 | 待填写 |
| evidence_valid | 待填写 | 待填写 |
| uncontaminated | 待填写 | 待填写 |
| evidence_grade：A/B/C/N | 待填写 | 待填写 |
| final_ruling：pass/fail/unknown/invalid | 待填写 | 待填写 |

复核人署名或可识别代号：待填写  
复核日期（Asia/Shanghai）：待填写  
是否参与本题题面、checker、rubric 或旧评分制作：待填写  
是否提前见过本场 checker 分及旧 S11 判分：待填写  
其他限制或分歧：待填写

本卡需另存填写完成版，保留空白原件。协调者才根据签署内容调用 `scripts/sbatch.py adjudicate`。本场未激活 gate，因此签署通过也只证实这场产品运行的终裁，不构成改件修复或因果反转。
