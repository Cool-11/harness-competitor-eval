# P0 隔离交付检查筛查：基线触发停止（2026-11-20）

真实新增产品运行 **1 场**；API messages 请求 **9 次**，二者不是同一统计单位。按[运行前登记](preregistration.md)先执行 C0，机械满分即停止，不继续挑选失败场。

| 臂 | 状态 | 唯一运行身份 | 实际观察 |
|---|---|---|---|
| C0 | 已 prepare、调用、collect；人工终裁 pending | `hev-20261120T214236+0800-S11-dsh-r16-36035514` | 两份要求文件齐全，checker 7/7；约28.79秒（模型进程28.18秒） |
| C1 | 未执行，未prepare、未分配run_id | — | 基线已满分，按停止线不测试 gate |
| C0-restored | 未执行，未prepare、未分配run_id | — | 无干预，不执行恢复 |

`execution-01/manifest.json` 中16/17/18是启动前的计划槽位；只有16实际创建唯一运行身份。17/18不计尝试、成功、失败或有效样本。

## 产物和可见行为

[原始归档](../../Log-analyse/S-batch/S11-corrupt-recovery/dsh/run16/)保存两份输入、产物、原生session、checker输出、配置证据和运行前身份。[机械输出](../../Log-analyse/S-batch/S11-corrupt-recovery/dsh/run16/checker_output.txt)为7/7。`result.md`为A1/A3/A5；`error_report.md`逐条定位第3行columns数组后缺逗号、第4行mode后多余尾逗号，并说明修复方式；修复后config.json可解析，threshold=10、mode=gt。

原生轨迹共有9次工具调用，可复核事件包括seq19 bash、seq23/29 read、seq31/39/47/55 bash、seq63 write、seq69 bash；直接参数及工具结果见[工具轨迹](execution-01/tool-trace.json)，压缩原件见[归档会话](../../Log-analyse/S-batch/S11-corrupt-recovery/dsh/run16/evidence/session_export/)。以上为裁判通道技术复核，不冒充独立语义签署；行为分和四门槛仍待人工复核。

真实环境为新Linux镜像 `sha256:09a27a1dfef7fff5b91b6a3bb0bc23d2ebc906cd59d3e00a2e765a4009ff2519`，DSH 0.2.2-rc.1/headless、原生deepseek-official/deepseek-flash/high/provider_default、workspace-write。实际cwd=/work，与Windows接收目录分别记录。请求工具有bash/read/write等，无skill工具；各场独立空DSH_HOME，不挂宿主仓库、旧场或Docker socket。

隔离检查、最终组合配置、初次stdout/stderr和原生session均复制至[补充原件包](execution-01/evidence/run16/)，[清单](execution-01/runtime-evidence-manifest.json)保存逐文件大小及SHA-256。新旧日志和产物均保留；停止后的产品容器和预算代理容器保留为审计现场，不再运行或调用模型。

## 预算与用量

用户累计上限 **5元**。代理按官方高峰价和每请求最大输出量在转发前保守预留，累计 **1.57044元上界**，未触及上限。实际报告用量：输入7525、缓存读55424、输出3864 tokens；按官方高峰价计算的用量估计约 **0.04818元**。见[预算与停止记录](execution-01/usage-and-stop.json)和[逐请求预算日志](execution-01/budget.jsonl)。

这两个数字分别是保守预留和用量估计，不是已结算账单。调用前、结束后及稍后读取的余额相同，差额暂为0.00元，可能存在结算延迟，不能据此宣称实际免费。原始余额快照为用户本地材料，本轮未发布。

## 允许与不允许的结论

- 允许：这一个隔离Linux配置下，C0成功交付了冻结S11的机械产物合同，旧漏交付在此场未复现；按预注册停止。
- 未测：外部delivery_gate组件是否有效、是否触发、恢复是否反转；没有处理臂，不能计算处理效应。
- 不允许：据一次成功宣称DSH已稳定修复、证明此前Windows ACL是根因，或宣称已完成“失败→干预成功→恢复失败”闭环。

正式准入仍未成立；本场初始终裁pending，尚未制造人工签认或独立评委。后续若扩展任务或重复，必须另写前瞻计划与新的预算分配，不能回填本次未执行的两臂。

**后续追加：** 用户选择同题 C1 回归检查后，另立[追加预注册](preregistration-addendum-01.md)并执行新 run17；见[追加结果](results-addendum-01.md)。本页的原筛查停止线与 run16 结果不变。
