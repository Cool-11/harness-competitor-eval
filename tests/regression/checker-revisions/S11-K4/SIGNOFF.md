# S11 · K4 checker 修订包签署

| 项 | 证据 | 状态 |
|---|---|---|
| 修前代码 | `checker-before.py` | 已保存 |
| 修后代码 | `checker-after.py`、生产 `tasks/second_tasks/S11-corrupt-recovery/checker.py` | 已保存 |
| 正例 | `tests/fixtures/golden/S11-corrupt-recovery/` | 回归通过，待独立签署 |
| 近似错误例 | `tests/fixtures/tampered/S11-corrupt-recovery/` | 期望 6.0，回归通过，待独立签署 |
| 反向对照 | 修后 checker `--selftest` 的“两处缺陷都报” | 期望 7.0，回归通过 |
| 修前/修后输出 | `tests/regression/evidence/S11-K4-{before,after}.txt` | 已保存 |
| 历史复算影响 | 元宝 S11 run1：7.0 → 6.0；其余四款仍 7.0 | 已记录，待独立签署 |

## 独立验收

- 验收人：`待填写（不得由本次修改者代签）`
- 验收日期：`待填写`
- 结论：`pending`
- 复核备注：`待填写`

> 未完成独立验收前，只能表述为“自动回归通过、待签”，不得作为已签署的对外分数引用。

## 精确来源指纹

- 修前生产文件 Git blob：`621c23ea7d90e4503744363d423f472aa0036fa1`（可由 `git show <blob>` 精确复原）。
- 修后生产文件 SHA-256：`e2d80a7a72e1e51a198c0a757b12577cfc75cb6c8aff48320b0889fe2d2f200e`。
- 本目录两个 `.py` 是可独立执行的核心判定快照；上述 blob/SHA 用于核对精确生产版本。
