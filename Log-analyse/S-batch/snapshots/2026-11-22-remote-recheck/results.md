# 全仓远端干净检出复算（2026-11-22）

复算身份：远端 `git@github.com:Cool-11/harness-competitor-eval.git` 分支 `codex/desktop-file-prepare` shallow clone，HEAD `4d5ade4`；临时目录新建 venv，仅安装 `pytest==9.1.1`（`requirements-dev.txt` 唯一依赖）。复算在本机工作树之外的临时目录执行，不触碰仓库现场。

## 六条复算命令

| 命令 | 结果 |
|---|---|
| `python -m pytest -o addopts= -q` | 355 passed, 13 skipped |
| `python scripts/eval_ledger.py validate` | 通过：55 条记录，record_id 无重复 |
| `python scripts/verify_frozen_checkout.py --output <tmp>/checkouts.json` | passed |
| `python scripts/core_score_calibration.py --output <tmp>/calibration.json` | S06/S11 golden=7.0、partial=5.5/6.0，正常 |
| `python scripts/sbatch.py formal-report --output-dir <tmp>/formal` | 纳入 19，排除/待裁 26 |
| `python scripts/coverage_report.py --output <tmp>/coverage` | 正式准入 19 条，覆盖 10/10 格 |

## 公开证据核验

`public_evidence_manifest.py` 对 5 份核心 manifest 在远端检出重新审计：

| manifest | total | verified | missing | mismatched |
|---|---:|---:|---:|---:|
| codex-r1 | 23 | 23 | 0 | 0 |
| dsh-r1 | 18 | 18 | 0 | 0 |
| workbuddy-r2 | 28 | 27 | 1 | 0 |
| doubao-r2 | 25 | 24 | 1 | 0 |
| yuanbao-r2 | 26 | 25 | 1 | 0 |
| **合计** | **120** | **117** | **3** | **0** |

3 条 missing 均为 `artifacts/__pycache__/bottle.cpython-313.pyc` 编译缓存（非原始证据）。在本机该缓存存在但被 `.gitignore` 排除（`local_only`），远端 clone 无此文件故计为 `missing`；两者同源、均非原始证据，不影响公开核验结论。0 mismatched 说明所有可复现证据哈希一致。

## 结论与差异

- 复算通过：软件（测试/冻结检出/校准）与可得账表（55 条、19 纳入）在远端可复现；公开证据 117/120 原始条目 verified、0 mismatched。
- 与 docs/48（2026-11-21 快照）差异：`sbatch formal-report` 排除/待裁由 25 → 26，来自快照后新提交的运行条目；纳入 19 不变。
- 局限：上述命令只复算软件与当前可得账表，不证明原件真实性或评委独立性（同 docs/48 第 39 行）。
