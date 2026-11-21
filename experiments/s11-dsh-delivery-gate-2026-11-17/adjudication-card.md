# S11 DSH r13 污染现场终裁卡（用户已核对）

| 项 | 建议 | 直接证据 |
|---|---|
| `rules_frozen` | yes | 题包和 checker 未改；`manifest.json` 记录 prompt/input 哈希 |
| `task_valid` | yes | 预注册 S11 原版题面与初始输入，工作目录和运行身份唯一 |
| `evidence_valid` | yes | 原生 session 与 manifest SHA-256 一致，实际 cwd、产物及 checker 均归档 |
| `uncontaminated` | **no** | 原生 seq 98–105 成功读取裁判 `checker.py`、`task.md` 和 golden fixture |
| `final_ruling` | **invalid** | 裁判材料进入被测会话；checker 7/7 不能作为未污染产品能力证据 |

用户于 2026-11-17 在本对话确认四门槛 `yes/yes/yes/no`、终裁 `invalid`；已按此执行 `sbatch adjudicate`，`official_eligible=false`。原件：[run13](../../Log-analyse/S-batch/S11-corrupt-recovery/dsh/run13/)；实验停止记录：[results.md](results.md)。原始 session、产物和 checker 未修改。
