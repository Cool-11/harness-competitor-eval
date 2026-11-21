# S11 DSH r7/r9 行为签认卡（待人工签认）

两场均已按[预注册](preregistration.md)执行并归档。本卡只摆证据，不代填行为档位或终裁。2026-11-16 机械复核：r7/r9 的 `manifest.json` 所列产物哈希逐项匹配；两个 `run.json.final_ruling` 均为 `pending`；两个 checker 均为 0/7。

| 运行 | 身份与证据 | 可核事实 |
|---|---|---|
| r7 | `hev-20261112T022349+0800-S11-dsh-r7-d3fe8694`；[原生时间线](../../Log-analyse/S-batch/S11-corrupt-recovery/dsh/run7/derived/tool-trace.md)、[判卷](../../Log-analyse/S-batch/S11-corrupt-recovery/dsh/run7/checker_output.txt)、[归档](../../Log-analyse/S-batch/S11-corrupt-recovery/dsh/run7/manifest.json) | seq 22–29 读本场输入；seq 70–71 写 `result.csv`（A1/A3/A5）；seq 84–105 修好并回读两处 JSON 损坏；终答提到两处损坏；没有 `result.md` 或 `error_report.md`。 |
| r9 | `hev-20261112T022929+0800-S11-dsh-r9-10cb0c55`；[原生时间线](../../Log-analyse/S-batch/S11-corrupt-recovery/dsh/run9/derived/tool-trace.md)、[判卷](../../Log-analyse/S-batch/S11-corrupt-recovery/dsh/run9/checker_output.txt)、[归档](../../Log-analyse/S-batch/S11-corrupt-recovery/dsh/run9/manifest.json) | seq 32–39 读本场输入；seq 80–83 修好 JSON，seq 88–91 写 `filtered.csv` 与 `output.csv`（A1/A3/A5）；seq 96–101 回读；终答称完成；没有两份要求的 Markdown。 |

两场都出现 `pwsh` 权限错误，但文件工具成功写入替代 CSV 与配置；本卡不把 ACL 故障归为交付遗漏原因。r9 使用隔离根目录，不能把两场表述为完全相同的外部环境。r8 读到旧场、r2 序号冲突，均按[结果记录](results.md)排除。

请人工对照冻结 [spec](../../tasks/second_tasks/S11-corrupt-recovery/spec.md)、完整原生会话与产物，分别填写下表；“聊天说到”与“按规定文件交付”分开判断。

| 运行 | D3-1 失败恢复 0–3 | D7-1 损坏定位 0–3 | D1-1 回传一致性 0–3 | common-1 过程可跟随 0–3 | 证据不足的格及理由 |
|---|---|---|---|---|---|
| r7 | 待签 | 待签 | 待签 | 待签 | 待签 |
| r9 | 待签 | 待签 | 待签 | 待签 | 待签 |

签认后再写各自 `grade.yaml`，核对准入四门槛、证据等级并执行 `adjudicate`；若某格证据不足，保留 `unknown`，不为使正式准入增加而猜档。

## 2026-11-16 用户初步意见与待澄清

用户初步给两场相同的“失败恢复 3、损坏定位 2份、回传一致性 1、common-1 过程可跟随 1”。这不是最终逐格签认，未写入 `grade.yaml`：

- 冻结 `spec.md` 的 D3-1 3 档要求“继续完成任务，且与产物一致”；两场都缺 `result.md`、`error_report.md`，终答却称完成。业务集合正确不能代替交付契约完成，需要用户确认“3”指业务结果还是 D3-1 档位。
- r7 终答明确说两处损坏，r9 终答只明确说尾逗号；“损坏定位 2份”是档位还是文件数不明。D7-1 必须按两场各自证据和冻结锚点分别判断。
- D1-1=1、common-1=1 记录为用户初步意见，待上述歧义澄清后逐场签认。

## 2026-11-16 最终行为档位签认

用户依据冻结锚点重新确认：r7 `D3-1/D7-1/D1-1/common-1 = 0/3/0/1`；r9 为 `0/2/0/1`。两份签认已分别写入 [r7 grade.yaml](../../Log-analyse/S-batch/S11-corrupt-recovery/dsh/run7/grade.yaml) 与 [r9 grade.yaml](../../Log-analyse/S-batch/S11-corrupt-recovery/dsh/run9/grade.yaml)。上节初步意见保留为裁判过程，不作为当前档位。正式准入四门槛、证据等级及 `pass/fail` 终裁仍待用户单独确认；当前两份 `run.json` 保持 `pending`。

## 2026-11-16 正式终裁补记

用户随后确认两场 `rules_frozen/task_valid/evidence_valid/uncontaminated` 均为 `yes`，最终均为 `fail`。按本批 B 轨同类场次采用保守证据等级 `C` 执行 `adjudicate`；两场均返回 `official_eligible=true`。上节的 `pending` 是签行为格时的中间状态，当前状态以各场 `run.json` 和新生成的 `formal-results.json` 为准。正式准入不改变“无法证明 ACL 或某项 Harness 组件导致遗漏”的结论。
