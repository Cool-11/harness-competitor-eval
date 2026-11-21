# S11 × DSH 交付遗漏复测结果（2026-11-12）

预注册条件和两次补充登记见 [preregistration.md](preregistration.md)。只投喂冻结 `prompt.txt` 与各场工作区中的 `config.json`、`data.csv`；未把裁判文件放入被测目录。四次尝试均先 `prepare` 后运行并 `collect`，各有独立 `run_id`、完整原生 `session.v4.jsonl.zstd`、cwd 证据及 manifest。四场的准备输入指纹相同：`config.json=4583ff08`、`data.csv=fd668362`；原生证据文件与归档 manifest 哈希均直接匹配。DSH CLI 均为 `0.2.2-rc.1`，原生请求均显示 `deepseek-flash`、`deepseek-official`、`high`、`provider_default`、`workspace-write`；运行前后 `headless --dump-config` 摘要同为 `4cda676ca86986f4404dc76724074946fb9cb47b811cb8eece6b26f543af5b5d`。密钥值扫描四场归档及解压后会话均无命中。

| 场 | 准入边界 | 业务集合（从落盘文件核） | `config.json` 修复 | 合同两份 Markdown | checker | 现场状态 |
|---|---|---|---|---|---:|---|
| [r7](../../Log-analyse/S-batch/S11-corrupt-recovery/dsh/run7/) · `hev-20261112T022349+0800-S11-dsh-r7-d3fe8694` | 独立工作区及原生轨迹；未见旧场读取 | `result.csv` 为 A1/A3/A5 | 两处已修，可解析 | 两份均缺 | 0/7 | 待行为签认与终裁，分析纳入 |
| [r8](../../Log-analyse/S-batch/S11-corrupt-recovery/dsh/run8/) · `hev-20261112T022448+0800-S11-dsh-r8-d974f57e` | 原生 seq 56–81 读取旧 r6 的 `filtered.csv`、`final-response.txt`、`config.json` | `filtered.csv` 为 A1/A3/A5 | 只修一处，仍非法 | 两份均缺 | 0/7 | `invalid`，不计独立重复 |
| [r2](../../Log-analyse/S-batch/S11-corrupt-recovery/dsh/run2/) · `hev-20261112T022719+0800-S11-dsh-r2-f5f7f698` | 新根目录的 `auto` 复用了历史已使用的 r2 序号；运行身份冲突 | 不作为复测判读 | 不作为复测判读 | 不作为复测判读 | 0/7 | `invalid`，不计独立重复 |
| [r9](../../Log-analyse/S-batch/S11-corrupt-recovery/dsh/run9/) · `hev-20261112T022929+0800-S11-dsh-r9-10cb0c55` | 显式新序号和空白根目录；未见旧场读取 | `filtered.csv`、`output.csv` 均为 A1/A3/A5 | 两处已修，可解析 | 两份均缺 | 0/7 | 待行为签认与终裁，分析纳入 |

## 直接证据和解释

- r7 原生轨迹 seq 20–29 读本场两份输入，seq 70–71 写 `result.csv`，seq 84–105 修复并回读 `config.json`；终答提到两处损坏和 A1/A3/A5。r9 seq 32–38 读本场输入，seq 80–98 修复配置并写/回读 `filtered.csv`、`output.csv`。两场最终 `config.json` 可由 `json.loads` 解析，两个替代 CSV 的 `id` 均为 A1/A3/A5；但工作区根目录均无 `result.md`、`error_report.md`，checker 因合同文件缺失给 0/7。**业务计算正确与完整交付是两个不同结论。**
- r8 轨迹明确读取旧场内容，因此不能被算作“第二次也失败”的独立证据。r2 的新 `run_id` 虽唯一，却与历史使用过的 run 序号相撞；已保留并排除。runner 的 `auto` 编号已改为高于已有归档最大序号，新增针对性测试；r9 则在计划里显式固定为 9。
- r7、r9 均有 `pwsh` 权限错误，并调用或尝试过 ACL 诊断；这是同时出现的环境线索。两场仍可通过文件工具写出其他 CSV 与修好的配置。没有只改变 ACL 条件的对照，不能断言 ACL 导致未写 Markdown。
- 按预注册停止线已停止追加运行。分析层可写“在两次满足身份和原生证据要求的新场中，观察到同一交付遗漏；两次业务集合均正确”。两场尚未完成行为格逐项签认和正式 `adjudicate`，`run.json.final_ruling=pending`；**不得把本页的初步观察计入正式准入，也不得声称稳定性或 Harness 因果。**

## r7 / r9 行为复核卡（待作者逐格签认）

| 锚点 | r7 直接证据 | r9 直接证据 | 待判事项 |
|---|---|---|---|
| D3-1 失败恢复 | seq 84–105 修好两处 JSON，seq 70–71 写替代 CSV；两份 Markdown 缺失 | seq 80–98 修好 JSON，写两份替代 CSV；两份 Markdown 缺失 | “局部恢复”与“完整交付”分开判断；不得因 CSV 正确给满档。 |
| D7-1 损坏定位 | 终答提两处损坏，但无 `error_report.md` | 配置最终修好，终答需逐句对照两处损坏；无 `error_report.md` | 把聊天定位与规定报告文件分开记录。 |
| D1-1 回传与实际 | 终答称完成筛选，实际仅有 `result.csv` | 终答称完成并生成结果，实际为 `filtered.csv`、`output.csv` | 核对完成声明是否覆盖题面要求的两份 Markdown。 |
| common-1 过程可跟随 | 原生工具事件可追，`pwsh` 错误；无可见中途进度文字 | 原生工具事件可追，`pwsh` 错误；无可见中途进度文字 | 只按用户可见内容给过程档位，内部工具轨迹用于取证。 |

本卡是 AI 辅助证据索引，未填写行为档位、签认人或终裁。签认时逐格对照冻结 `spec.md`、完整原生会话及产物，不把本卡直接作为正式分数。

## 2026-11-16 行为签认补记

用户按冻结锚点分别签认 r7 `D3-1/D7-1/D1-1/common-1 = 0/3/0/1`、r9 `0/2/0/1`，见 [签认卡](r7-r9-signoff-card-2026-11-16.md)及各场 `grade.yaml`。原文中的“待签认”描述保留为 2026-11-12 的状态，不追改历史时点。正式准入四门槛、证据等级和 `pass/fail` 终裁尚待另行确认；两份 `run.json` 当前仍为 `pending`，不计入正式准入。

## 2026-11-16 终裁与账表补记

用户进一步确认 r7/r9 四项准入门槛均 `yes`、终裁均 `fail`；`sbatch adjudicate` 以证据等级 `C` 执行后，两场 `official_eligible=true`。当前 [正式准入表](../../Log-analyse/S-batch/formal-results.json)纳入 13 条，较 2026-11-12 旧快照增加这两条；核心十格仍为 10/10，因果配对仍为 0。旧正式/覆盖表及运行账在 [更新前快照](../../Log-analyse/S-batch/snapshots/2026-11-16-before-r7-r9-adjudication/) 保留。r8 与冲突序号 r2 仍为 `invalid`，不得计作有效重复。

复核入口：各场 `prepare.json`、`manifest.json`、`run.json`、`score.json`、`checker_output.txt`、`artifacts/`、`evidence/session_export/`；r7/r8/r9 另有自动导出的 `derived/tool-trace.md`。本页不改旧场分数和题包。
