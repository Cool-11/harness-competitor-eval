# S11 × DSH r10/r11/r12 人工行为与终裁复核卡（已由用户签认）

本卡列事实索引和用户签认结果。冻结题面见 [S11 prompt](../../tasks/second_tasks/S11-corrupt-recovery/prompt.txt)，四格逐档锚点见 [复核 rubric](../../reviews/S11-round1-2026-11-06/reviewer/rubric.md)。逐场原生 session、[结果页](results.md)、落盘文件和 `grade.yaml` 保留评分证据；checker 0/7 不自动决定行为分或终裁。

[逐格评分与准入建议](adjudication-proposal.md)已由用户核对。独立评委复核另行开展，不能与用户签认混同。

| run | D3-1 恢复与继续 | D7-1 两处损坏定位 | D1-1 交付与回传 | common-1 可见过程 |
|---|---|---|---|---|
| [r10](../../Log-analyse/S-batch/S11-corrupt-recovery/dsh/run10/) | seq 60/62 写备份和修复，seq 68 写 `filtered.csv`；两份 Markdown 缺 | 终答文字指出两处损坏；无 `error_report.md` | 终答称筛选完成；实际仅有 `filtered.csv` 等替代产物 | seq 22/52/70 `pwsh` 错误；中途用户可见输出与原生工具轨迹分开判 |
| [r11](../../Log-analyse/S-batch/S11-corrupt-recovery/dsh/run11/) | seq 70、86 修复两处，seq 64 写 `filtered.csv`；两份 Markdown 缺 | 终答文字指出两处损坏；无 `error_report.md` | 终答称任务完成；实际仅有 `filtered.csv` 等替代产物 | 无 `pwsh`；seq 53 有中途文字；内部工具轨迹不等同用户可见进度 |
| [r12](../../Log-analyse/S-batch/S11-corrupt-recovery/dsh/run12/) | seq 42、62 修复两处，seq 44 写 `filtered.csv`；两份 Markdown 缺 | 终答文字指出两处损坏；无 `error_report.md` | 终答称筛选完成；实际仅有 `filtered.csv` 等替代产物 | seq 28/54/70 `pwsh` 错误；中途文字见 seq 41/61 |

| run | D3-1 档位/证据 | D7-1 档位/证据 | D1-1 档位/证据 | common-1 档位/证据 | 四门槛与终裁 | 签认人/日期 |
|---|---|---|---|---|---|---|
| r10 | 0；[逐格证据](../../Log-analyse/S-batch/S11-corrupt-recovery/dsh/run10/grade.yaml) | 3；同左 | 0；同左 | 1；同左 | 四门槛 yes；C；fail；正式准入 | 用户本人；2026-11-17 |
| r11 | 0；[逐格证据](../../Log-analyse/S-batch/S11-corrupt-recovery/dsh/run11/grade.yaml) | 3；同左 | 0；同左 | 1；同左 | 四门槛 yes；C；fail；正式准入 | 用户本人；2026-11-17 |
| r12 | 0；[逐格证据](../../Log-analyse/S-batch/S11-corrupt-recovery/dsh/run12/grade.yaml) | 3；同左 | 0；同左 | 1；同左 | 四门槛 yes；C；fail；正式准入 | 用户本人；2026-11-17 |

运行前身份、题包、原生 session 和 cwd 均可在各场 `prepare.json`、`manifest.json`、`evidence/` 核查。用户已确认四门槛并逐场执行 `sbatch adjudicate`；`official_eligible=true`。本次签认不替代独立复核，也不升级为 Harness 因果结论。
