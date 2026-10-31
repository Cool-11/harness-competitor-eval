# S11 · K4 checker 修订包签署

| 项 | 证据 | 状态 |
|---|---|---|
| 修前代码 | `checker-before.py` | 已保存 |
| 修后代码 | `checker-after.py`、生产 `tasks/second_tasks/S11-corrupt-recovery/checker.py` | 已保存 |
| 正例 | `tests/fixtures/golden/S11-corrupt-recovery/` | 回归通过，hjs 独立验收通过 |
| 近似错误例 | `tests/fixtures/tampered/S11-corrupt-recovery/` | 期望 6.0，回归通过，hjs 独立验收通过 |
| 反向对照 | 修后 checker `--selftest` 的“两处缺陷都报” | 期望 7.0，回归通过 |
| 修前/修后输出 | `tests/regression/evidence/S11-K4-{before,after}.txt` | 已保存 |
| 历史复算影响 | 元宝 S11 run1：7.0 → 6.0；其余四款仍 7.0 | 已记录，hjs 独立验收通过 |

## 独立验收

- 验收人：`hjs`（本人于 2026-10-31 在本项目对话中确认未参与本次 checker 修改）
- 验收日期：`2026-10-31`（北京时间）
- 结论：`通过`。hjs 本人确认 K4 独立验收通过；该确认是人工签认，不等同于自动回归输出。
- 复核意见：同意 K4 将“缺陷描述”和“修复动作”分开识别。近错例 6.0/7，正例及反向对照 7.0/7；历史元宝 S11 run1 自动复算 7.0→6.0，其余四款不变。若后续发现等价表述误判，新增 fixture 并重开修订。
- 复核备注：2026-10-31 生产 checker SHA-256 为 `e2d80a7a72e1e51a198c0a757b12577cfc75cb6c8aff48320b0889fe2d2f200e`，与本页指纹一致；本机复跑 golden=7.0、tampered=6.0、partial=6.0、`--selftest` 中近错例=6.0/反向对照=7.0；`tests/regression` 为 31 passed。历史影响可由 `S11-K4-before.txt` / `S11-K4-after.txt` 复核。
- 签认来源：hjs 在 2026-10-31 本项目对话中明确回复“本人确认未参与修改 checker，通过 K4 独立验收，同意上传 GitHub”。

> 本签署只覆盖 K4 checker 修订及其历史复算影响；不追认 S11 run2 为正式产品运行，也不代替 run2 的行为分终裁。

## 精确来源指纹

- 修前生产文件 Git blob：`621c23ea7d90e4503744363d423f472aa0036fa1`（可由 `git show <blob>` 精确复原）。
- 修后生产文件 SHA-256：`e2d80a7a72e1e51a198c0a757b12577cfc75cb6c8aff48320b0889fe2d2f200e`。
- 本目录两个 `.py` 是可独立执行的核心判定快照；上述 blob/SHA 用于核对精确生产版本。
