# S11 × DSH run4 新制式流程试点复核（2026-11-01）

状态：`hjs 确认核对成功并授权 Codex 代签；本场终裁 pass，证据等级 C`。本场唯一 ID `hev-20261101T015900+0800-S11-dsh-r4-fb43b7cd`。四格档位由 Codex 按锚点复核代录，见 `grade.yaml`；不声称 hjs 亲自逐格计算。run3 是另一次目录错位的 `invalid` 尝试，见相邻 `run3/invalid-attempt.md`，不与本场混算。

## 观察

本场在发送 S11 题目前生成 v2 `prepare.json`；工作区起始只有源 `config.json`、`data.csv`。DSH 在同一深层 `run4/work` 读取两输入，修复 `config.json`，写 `result.md`、`error_report.md` 并回传。归档产物 checker 为 **7.0/7**。按冻结锚点，D3/D7/D1/common 档位为 **3/3/3/3**，行为分 **6.0/6.0**；产物归一 **4.0/4.0**，单题 **10.0/10.0**。终裁 `pass` 指本场任务通过，不推断跨轮稳定。

## 证据

- `prepare.json` 保存 `2026-11-01T01:59:00+08:00`、唯一 ID、任务/产品 revision、模型 `deepseek-flash`、推理 `high`、权限和源输入短哈希。
- 原生会话 `session-517abe74-714f-42d4-8877-1235786dd407`，压缩原件在外部同场 `log/session.v4.jsonl.zstd`；SHA-256 `8bb8e2b3d39ff391a66d6ca429ca102b0be6b9ecb06c1736cff2e926f196bf97`。会话头 cwd 精确等于 run4/work；seq 20/21 相对路径读取两输入，seq 28 就地修复，seq 42/44 写两结果，seq 58 回传；完整时点见 `timeline.md`。
- 用户新导出同场 zip 至外部 `log`；与自动保存版共有的 seq 0–67 逐条相同，新增两条仅为会话结束后的导出动作。哈希与方法见 `export-verify.md`。
- 活动分账保留初次收件时 `product_run=unknown` 的历史记录；后续代签与重算另登记为 `OR-20261101T022946+0800-7f467d12`，当前终裁以本场 `run.json` 和正式准入表为准，不把两条记录当两次产品运行。
- 外部同场 `shots/S1.png` 发送前保存，`S2.png` 为首次处理状态，`S4.png` 为完成语，`S5.png` 为产物卡片；截图与原生消息先后顺序一致。`artifacts/` 快照、`checker_output.txt`、`manifest.json`、`usage.json`、`score.json` 已归档。修前/修后输入及结果完整 SHA-256 见 `timeline.md`。

## 解释

该场验证了 **F 盘此深层工作区**的 DSH 真实 cwd 绑定、相对路径读取、就地修复、同目录产物写入及原生日志回收。checker 7/7 只证明产物内容；行为分另由 `grade.yaml` 的逐格证据与理由支持。hjs 在本对话确认核对成功并授权 Codex 直接签认，故按本场证据给 `pass`。`docs/07` R2 原规定为 AI 初评后由作者逐格核对；本场属于**明确授权代评代录**，报告须如实披露这一差异，不能写成 hjs 亲自逐格给分。

## 未排除因素

- 单场证据等级仅 C；不能据此声称跨轮稳定。Skills/Memory 当场状态记 `unknown`，未把当前设置推定为已关闭。
- S1 截图只显示工作区简称 `work`，完整路径由原生日志核实；S2 截图只显示首次处理中状态，工具步骤须查原生日志。
- `error_report.md` 对尾随逗号写“第 5 行、`mode` 字段之后”，源配置的 `mode` 在第 4 行、闭合括号在第 5 行。D7 仍给 3 档，因为字段名、原文片段和修复动作明确指向第二处，满足“行或字段”定位；行号偏差是报告瑕疵，已登记。

## 可复现实验与停止条件

1. 本场已按 hjs 明确授权完成代签与 `adjudicate`，正式准入以 `formal-results` 为准；报告方法论须披露代签方式、四格理由与证据哈希。若后续要求严格采用 `docs/07` R2 的作者逐格核对口径，hjs 可再逐格复核 `grade.yaml` 并补记二次签认。
2. 若原生日志与截图出现新的 cwd、输入或污染反证，改判 `invalid/unknown` 并停止本场正式准入；不得把产物 7/7 自动折算为产品成功。
3. 若需要重复稳定性，另起新 run 并完整重复运行前预检与证据纪律；不能把旧 run2 或 run3 与 run4 平均。
