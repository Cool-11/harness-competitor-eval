# tool-fs 图像探针结果（2026-11-24）

## 实验身份

- 目录：`experiments/mechanism-probe-tool-fs-2026-11-24/aba-01/`
- 镜像：`harness-p0-dsh:20261120`；`workspace-write`、`deepseek-flash` / `deepseek-official` / `high`
- 题面：读取 `inventory.png`（6 行 ID/QTY 表，无总计行），转录到 `cross_ref.md` 并给出总计（冻结真值 1417）
- 唯一改动：`tool-fs` 开 → 关 → 开（`read`/`write`/`edit`/`read_image` 一并移除；`tool-bash` 保持开）

## 三臂

| 臂 | tool-fs | 结果 | 有效性 |
|---|---|---|---|
| A1（run1）| 开 | **7.00/7**（6/6 + 总计 1417），9.2s | ✅ 有效 |
| B（run2，重跑）| 关 | **4.33/7**（5/6 条对、总计错），107.1s，rc=0 | ✅ 有效 |
| A2 | 开 | 未发射 | 停止条件 2 触发 |

B 场 observed 工具确实不含 `read`/`write`/`edit`/`read_image`（`tool-diff.json`：removed_in_b 为这四项，added_in_b 为空），但 `bash`、`glob`、`grep`、`workflow`、`subagent` 仍在。

## B 臂如何绕过

B 臂用 `bash` + 纯 Python 解码 PNG（zlib 解压 + 反滤波），渲染成 ASCII 字符画后目视 OCR：6 条中读对 5 条，总计读错。原始推理与命令记录见 `arm-b/initial.stderr.txt` 与 session。

## 结论

- 图像题面同样**没有**让 `tool-fs` 成为物理必需：`bash` + 纯 Python 可以部分替代读图能力。
- B 得分 4.33 > 阈值 1.05，触发预注册停止条件 2，A2 不发射，A/B/A 不成立。
- 若要让门真正闭合，需要：高熵内容（随机数、无规律）、更小字号或抗 OCR 排版，并以「B 必须为 0」为前提再发 A2。

## 首轮无效场与缺陷

- 首轮 B/A2 因代理 ¥5 上限被 429 中止（`budget_limit` 拦截 13 次），记 `invalid`，归档于 `arm-b-invalid-01-budget/`、`arm-a2-invalid-01-budget/`，原件保留。
- 重跑使用独立代理、¥10 上限，预算日志 `budget-run2.jsonl`（24 次请求、reserved ¥7.204、0 次拦截）。
- 预算读取为 reserved 上界，不等于实际扣费；`balance-before/after` 均为 ¥8.03，不做折算。
