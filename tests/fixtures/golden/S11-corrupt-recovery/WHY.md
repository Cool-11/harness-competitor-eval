# S11 golden · 为什么应得满分

依据 `prompt.txt` 的要求、`truth.json` 的事实与 `spec.md` 的完成条件构造（未参考 checker 判定逻辑，checker 仅用于验证）。

## 满足的完成条件（task.md「完成条件」1–3）

| # | 完成条件 | 产物中的证据 |
|---|---|---|
| 1 | `result.md` 存在，内容恰为 `A1 / A3 / A5`（threshold=10、mode=gt，即 amount>10） | `result.md` 仅三行 `A1`、`A3`、`A5`；对应 `data.csv` 中 amount 为 12、15、20 的三行 |
| 2 | `error_report.md` 存在，且指到 2 处损坏位置 | 逐条写明第 3 行 `columns` 数组后缺逗号、第 4 行 `mode` 值后多余尾逗号，并各自给出修复方式 |
| 3 | `result.md` 中 id 均来自 `data.csv`（无编造） | `A1/A3/A5` 均为 `inputs/data.csv` 中真实存在的 id，未出现 A2/A4/A6 |

## 对应 spec.md 判定锚点

- 「失败恢复｜检测与报告」：指出损坏 + 给出修复 + 继续完成任务，且产物与报告一致 → 3 档。
- 「可观测性｜损坏定位具体性」：逐处定位（2 处）且说明修复方式 → 3 档。
- 与 `truth.json` 的「损坏位置」两条（行 3 缺逗号 / 行 4 尾逗号）逐条一致。

## 预期判分

产物分 7.0/7。行为分 0–3 由人工按会话记录评定，不在本 fixture 范围。
