# tests/ · 评测系统自身的测试

> 测的是**尺子**，不是产品。产品表现记录在 `Log-analyse/`，不进入这里。

## 一键运行

```powershell
.\.venv\Scripts\python.exe -m pytest
```

首次在新机器上：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

## 目录

| 路径 | 作用 |
|---|---|
| `unit/` | 单题级断言：题包完整性、truth 可解析、checker `--selftest`、负控制（空→0 / 垃圾<满分）、sbatch 三件套字段 |
| `integration/` | 题库发现契约：批次目录、题号唯一、新增题自动纳入 |
| `regression/` | P0 fixture 分数快照（`expected_scores.json`），checker 改口径必须显式变红 |
| `fixtures/golden/<题号>/` | 人工签署的"应得满分"产物 |
| `fixtures/partial/<题号>/` | 故意做坏一条的产物，期望分写进快照 |

## 三级覆盖

| 级别 | 范围 | 内容 |
|---|---|---|
| P1 | 自动扫描 `tasks/` 全部题目录 | 题包 / truth / selftest / 负控制 |
| P0 | 深跑 12 题 | golden + partial + 分数快照 |
| P2 | 其余轻跑题 | 逐步补 partial fixture |

新增题目会自动进入 P1；没有 fixture 的题在 P0 阶段 `skip`，并计入覆盖率。

## fixture 编写规则

- **golden 不来自产品运行结果**：按 `prompt.txt` 的要求 + `truth.json` 的事实构造；checker 只用来验证，不用来倒推内容
- 每个 fixture 目录必须有一份 `WHY.md`：说明满足哪些完成条件、对应 `spec.md` 哪条锚点
- partial 必须**只破坏一个条件**，并在 `WHY.md` 写明期望丢多少分
- 签署状态见 `fixtures/SIGNOFF.md`；`draft` 可用于开发期回归，`signed` 才可用于对外报告引用
- 现有口径差异见 [`KNOWN_ISSUES.md`](KNOWN_ISSUES.md)（fixture 校准发现，修复前不得当作已验证结论）

## 失败怎么读

- **红 = 尺子变了**，不是产品变了：先查 `git diff` 是否动了 checker / truth / prompt
- 如果是有意改口径：重跑后更新 `expected_scores.json`，让分数变化出现在 diff 里
