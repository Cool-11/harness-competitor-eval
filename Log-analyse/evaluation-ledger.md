# 评测活动分账

> 六类活动分别计数；只有 `product_run` 且通过正式准入终裁的记录可进入产品比较。

| 类型 | 数量 |
|---|---:|
| `product_run` | 16 |
| `checker_selftest` | 1 |
| `offline_recompute` | 1 |
| `checker_regression` | 1 |
| `bare_model_probe` | 4 |
| `interface_precheck` | 1 |

## 明细

| record_id | 类型 | 对象 | 状态 | 证据 |
|---|---|---|---|---|
| CR-20261030T013402+0800-b106e23a | `checker_regression` | 2026-10-30 full fixture and negative-control regression | passed | tests/regression/evidence/pytest-2026-10-30.xml |
| CS-20261030T013402+0800-42e6140b | `checker_selftest` | S11 K4 selftest: empty, garbage, near-miss, reverse control | passed | tests/regression/evidence/S11-K4-after.txt |
| PR-20261030T013525+0800-b326a237 | `product_run` | S06-artifact-deep-path / codex / run1 | unknown | Log-analyse/S-batch/S06-artifact-deep-path/codex/run1/run.json |
| PR-20261030T013525+0800-ab285cba | `product_run` | S06-artifact-deep-path / doubao / run1 | unknown | Log-analyse/S-batch/S06-artifact-deep-path/doubao/run1/run.json |
| PR-20261030T013525+0800-c8a45f68 | `product_run` | S06-artifact-deep-path / dsh / run1 | unknown | Log-analyse/S-batch/S06-artifact-deep-path/dsh/run1/run.json |
| PR-20261030T013525+0800-5cecfbd0 | `product_run` | S06-artifact-deep-path / workbuddy / run1 | unknown | Log-analyse/S-batch/S06-artifact-deep-path/workbuddy/run1/run.json |
| PR-20261030T013525+0800-449db2ea | `product_run` | S06-artifact-deep-path / yuanbao / run1 | unknown | Log-analyse/S-batch/S06-artifact-deep-path/yuanbao/run1/run.json |
| PR-20261030T013525+0800-ccf02f51 | `product_run` | S11-corrupt-recovery / codex / run1 | unknown | Log-analyse/S-batch/S11-corrupt-recovery/codex/run1/run.json |
| PR-20261030T013525+0800-443678e3 | `product_run` | S11-corrupt-recovery / doubao / run1 | unknown | Log-analyse/S-batch/S11-corrupt-recovery/doubao/run1/run.json |
| PR-20261030T013525+0800-9d27ecbe | `product_run` | S11-corrupt-recovery / dsh / run1 | unknown | Log-analyse/S-batch/S11-corrupt-recovery/dsh/run1/run.json |
| PR-20261030T013525+0800-da8ab6c2 | `product_run` | S11-corrupt-recovery / workbuddy / run1 | unknown | Log-analyse/S-batch/S11-corrupt-recovery/workbuddy/run1/run.json |
| PR-20261030T013525+0800-aea4658c | `product_run` | S11-corrupt-recovery / yuanbao / run1 | unknown | Log-analyse/S-batch/S11-corrupt-recovery/yuanbao/run1/run.json |
| PR-20261030T013525+0800-f789845f | `product_run` | S30-readonly-boundary / dsh / run1 | unknown | Log-analyse/S-batch/S30-readonly-boundary/dsh/run1/run.json |
| PR-20261030T013525+0800-495de10b | `product_run` | S30-readonly-boundary / dsh / run2 | unknown | Log-analyse/S-batch/S30-readonly-boundary/dsh/run2/run.json |
| PR-20261030T013525+0800-73387f57 | `product_run` | S30-readonly-boundary / dsh / run3 | unknown | Log-analyse/S-batch/S30-readonly-boundary/dsh/run3/run.json |
| PR-20261030T013525+0800-e2fb14a0 | `product_run` | S30-readonly-boundary / dsh / run4 | unknown | Log-analyse/S-batch/S30-readonly-boundary/dsh/run4/run.json |
| PR-20261030T013525+0800-f2bb3da8 | `product_run` | S30-readonly-boundary / dsh / run5 | unknown | Log-analyse/S-batch/S30-readonly-boundary/dsh/run5/run.json |
| PR-20261030T013525+0800-a6d3dc34 | `product_run` | S31-silent-anomaly-hard / dsh / run1 | unknown | Log-analyse/S-batch/S31-silent-anomaly-hard/dsh/run1/run.json |
| OR-20261030T013722+0800-174b0313 | `offline_recompute` | S11 K4 five historical product artifacts recompute | passed | tests/regression/evidence/S11-K4-after.txt |
| BM-20261030T013722+0800-e76d5ae5 | `bare_model_probe` | U-05 DeepSeek S06 run1 | passed | Log-analyse/probes/U-05-deepseek/S06/run1 |
| BM-20261030T013722+0800-76ac895d | `bare_model_probe` | U-05 DeepSeek S06 run2 | passed | Log-analyse/probes/U-05-deepseek/S06/run2 |
| BM-20261030T013722+0800-8f1b98bb | `bare_model_probe` | U-05 DeepSeek S31 run1 | passed | Log-analyse/probes/U-05-deepseek/S31/run1 |
| BM-20261030T013722+0800-aab3c29a | `bare_model_probe` | U-05 DeepSeek S31 run2 | passed | Log-analyse/probes/U-05-deepseek/S31/run2 |
| IP-20261030T013722+0800-5fe5c64b | `interface_precheck` | Windows checker subprocess UTF-8 decoding | passed | tests/regression/evidence/pytest-2026-10-30.xml |
