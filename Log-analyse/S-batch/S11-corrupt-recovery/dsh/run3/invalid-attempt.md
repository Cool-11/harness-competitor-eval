# S11 × DSH run3：目录错位的无效尝试（2026-11-01）

运行前 `prepare.json` 的唯一身份为 `hev-20261101T014857+0800-S11-dsh-r3-f31eec6c`，指定正式工作区 `F:\for-project-tmp-run\runs\S11-corrupt-recovery\dsh\run3\work`。该目录在投喂后仍只有原始 `config.json` 和 `data.csv`，没有本场产物。

实际 S11 会话的原生日志位于 `F:\for-project-tmp-run\prechecks\dsh\2026-11-01\work\Log\dsh-session-session-b34be32a-8225-40a2-9fcb-da77a21798c7.zip`，SHA-256 为 `BF06EC50AAFCFE182D90677C1F0372EBBD7690345FCBF99BF7C5000F6F7DE982`，含 73 条事件。会话头 `cwd=F:\for-project-tmp-run\prechecks\dsh\2026-11-01\work`；seq 20/21 读取的是仓库题包 `tasks/second_tasks/S11-corrupt-recovery/inputs/` 中的两个文件；seq 44/46 将 `result.md`、`error_report.md` 写入预检工作区；seq 60 将两份文件作为产物回传。S1/S2/S4/S5 截图位于 `F:\for-project-tmp-run\prechecks\dsh\shots\`，其中 S1 为发送前画面，附件为仓库题包输入，而非 run3/work 中的隔离副本。

预检工作区两份 Markdown 产物用当前 checker **离线检查为 7.0/7**；这只说明这两份内容符合规则，不是 run3 正式产物分。产物与原始 zip 均原地保留，不复制到 run3/work，不将预检目录改名成正式工作区，也不为该场创建虚假的 `collect`/`score.json`。

终裁：`invalid`，证据等级 `N`，`evidence_valid=no`，`uncontaminated=no`。原因是运行前绑定的正式 work 与实际 cwd、输入来源、产物落点不一致；此问题是执行流程错位，**不是 DSH 产品失败**。本槽位永久保留，不覆盖；下一场须使用更大的 run 序号和新的空白会话，发送前核对真实 cwd 及两个输入确在新 work。
