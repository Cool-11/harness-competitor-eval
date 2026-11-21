# 前三项整改第二批证据（2026-11-20）

架构与执行合同见 [43](../../docs/43-四轨架构与前三项整改执行合同-2026-11-20.md)，验收报告见 [44](../../docs/reports/44-前三项整改实施与验收-2026-11-20.md)。新增产品运行 0；没有写入新实验结果或独立签署。

| 产物 | 内容与边界 |
|---|---|
| clean-checkout-export.json | 真实临时 Git 仓库的 LF/CRLF 两次克隆均导出 10 场40格；只覆盖冻结导出最小快照，不是全项目远端复现 |
| read-isolation-probe.json | 同身份无模型读取探测；当前裁判文件可读，因此预检必须拒绝 |
| core-calibration-v2.json | 九个核心校准结果及新增题包/fixture 精确指纹，仍非独立签认 |
| coordinator-reference.csv | 从历史已签 grade 提取的原判，供协调者计算，不交给盲于原判的复核人 |
| reference-sources.json | 上述原判的原文件、run_id、SHA-256；不改原判 |
| reviewer-agreement-pending.json | 复评 20 格未填，status=pending、overall=null，独立关系 unknown |
| by-track/formal-results.json / .md | 新版正式表含研究轨道及机制绑定，不覆盖旧表；16 纳入/25 排除或待裁 |
| formal-results.json / .md | 本轮早期输出的既有格式快照，保留不覆写 |
| coverage.json / .md | 当前核心两题35条现场、16正式、10/10格；与全批正式表范围不同 |

复算时使用新输出目录：

```powershell
.\.venv\Scripts\python.exe scripts\verify_frozen_checkout.py --output <新目录>\checkouts.json
.\.venv\Scripts\python.exe scripts\core_score_calibration.py --output <新目录>\calibration.json
.\.venv\Scripts\python.exe scripts\sbatch.py formal-report --output-dir <新目录>\formal
.\.venv\Scripts\python.exe scripts\coverage_report.py --output <新目录>\coverage
.\.venv\Scripts\python.exe scripts\reviewer_agreement.py --reference experiments/review-remediation-phase2-2026-11-20/coordinator-reference.csv --review reviews/S11-independent-recheck-2026-11-17/review-form.csv --protocol reviews/S11-independent-recheck-2026-11-17/agreement-protocol-v1.json --output <新目录>\agreement.json
```

复评命令目前应返回 pending。真实复核人完成并封存新表后，协调者更换 `--review` 并追加真实关系声明文件；不要让 Agent 代写复评意见或声明独立身份。统计工具不会覆盖历史评分或自动终裁。
