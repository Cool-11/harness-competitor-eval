# 豆包 run3 独立人工复核签署卡（待签）

对象：`file-interface-v1__doubao__r3`，运行身份 `tb2file-20261116T170302+0800-doubao-r3-2d71a076`。本卡供未参与[裁判文件](../experiments/external-terminal-bench-fix-code-vulnerability/file-interface-v1/evidence/doubao-r3/adjudication.json)制作的人复核。当前**没有独立人工签署**；裁判通道的 `pass` 不等于独立验收完成。

## 复核顺序

1. 先核对[冻结题面与输入清单](../experiments/external-terminal-bench-fix-code-vulnerability/file-interface-v1/manifest.json)、[运行前记录](../experiments/external-terminal-bench-fix-code-vulnerability/file-interface-v1/evidence/doubao-r3/prepare.json)、[回收清单](../experiments/external-terminal-bench-fix-code-vulnerability/file-interface-v1/evidence/doubao-r3/collect.json)及[30 项证据哈希](../experiments/external-terminal-bench-fix-code-vulnerability/file-interface-v1/evidence/doubao-r3/manifest.json)。
2. 查看 `screenshots/`：发送前模型界面与项目名 `work`、附件目录截图、完成后的两文件与完整工作路径。明确附件选择器截图早于固定模型发送截图且未显示文件被点击选中；发送前只显示工作目录名称，完整路径来自完成后截图。不要推断不可见的内部轨迹。
3. 比对两份[冻结产物](../experiments/external-terminal-bench-fix-code-vulnerability/file-interface-v1/evidence/doubao-r3/artifacts/bottle.py)和[判卷结果](../experiments/external-terminal-bench-fix-code-vulnerability/file-interface-v1/evidence/doubao-r3/offline-verifier/result.json)：`bottle.py` SHA-256 `abf643683b4870e07500f8a035d1a076d4bf0bbf98eb2fb5180fbc3ef8fad802`，`report.jsonl` SHA-256 `ebfb63dd13ab68ef8e205b576df25b98430cdbce1b5085a8791514170e2010a3`；新容器原仓库 367/367、附加 6/6、离线诊断 reward=1。
4. 最后阅读[裁判终裁](../experiments/external-terminal-bench-fix-code-vulnerability/file-interface-v1/desktop-doubao-r3-adjudication-2026-11-17.md)，判断是否同意 `pass`、证据等级 C 和所列限制。本变体不产生 Terminal-Bench 官方成绩，也不支持 Harness 组件因果归因。

## 由复核人填写

| 项目 | 复核结论及依据 |
|---|---|
| 题包、运行身份和输入哈希一致 | 待填 |
| 附件来源与工作目录证据足以准入，或需标为 unknown/invalid | 待填 |
| 两份产物确属本场且哈希与快照一致 | 待填 |
| 冻结镜像、脚本、CTRF、reward 与容器日志一致 | 待填 |
| 对裁判 `pass` 的意见及理由 | 待填 |
| 利益冲突或未参与裁判文件制作声明 | 待填 |
| 复核人姓名或 GitHub 身份、日期、签名 | 待填 |

签署前保持 `independent_human_signoff=pending`。如不同意裁判结果，保留原裁判文件，另写复核意见和更正版本，不覆盖原始证据。
