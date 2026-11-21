# S11 × DSH 外部交付前检查：A1 停止记录（2026-11-17）

按[预注册卡](preregistration.md)，先运行默认包装器 A1，B 和 A2 尚未启动。A1 的唯一运行身份为 `hev-20261117T223912+0800-S11-dsh-r13-1ab9bd53`，CLI `0.2.2-rc.1`，原生请求为 `deepseek-official/deepseek-flash/high/provider_default`，工作目录为 `C:/tmp_s11_delivery_gate_20261117/S11-corrupt-recovery/dsh/run13/work`。原件见[r13 归档](../../Log-analyse/S-batch/S11-corrupt-recovery/dsh/run13/)；原生 session SHA-256 为 `ed755143b1a64efb5ae2f2ed04c5665e7f6b4e8187d7e6f52b1cc6843456dccb`。

冻结 checker 显示 7/7，两份 Markdown 已在根目录且内容通过机械检查。但**该分数不是有效的未污染基线**：原生轨迹 seq 98/99/100/101 分别读取了裁判仓库中的 `checker.py`、`task.md` 和两份 golden fixture，seq 102–105 的工具结果均返回了文件内容。直接证据见[工具轨迹](../../Log-analyse/S-batch/S11-corrupt-recovery/dsh/run13/derived/tool-trace.md)及原生 session。用户已核对四门槛 `yes/yes/yes/no`、终裁 `invalid`；已执行 `adjudicate`，`official_eligible=false`。签认见[终裁卡](adjudication-card.md)。checker 7/7 不计为正式通过。

泄露路径可见：DSH 在工作目录上层读取了 `prepare.json`、`run.json`、runner 的 `invocation.json` 和批次账，其内容含裁判仓库绝对路径；随后搜索 F 盘仓库并读取 checker/fixture。当前 DSH `workspace-write` 只限制写入，文件读取并不限制在工作区内；因此只做相同包装器、单独工作目录和新会话仍不足以满足被测产品隔离。此为路径线索，不能声称每一步内部动机已被证明。

**停止处置：**不启动 B 或 A2，不以污染的 7/7 宣称 gate 有效或无效；两个预留槽 `run14/run15` 未使用。外部 gate 的代码已通过非模型端到端测试，能在首轮缺文件时把缺失文件名反馈给同一 session 并最多续接一次；真实 DSH 的 gate 处理效果尚未实测。继续产品试验前，需把被测进程放入无法读取裁判仓库、历史运行和 golden fixture 的隔离环境，并避免在其可读的运行元数据中暴露裁判路径；重新预注册新 run，不沿用本次失败现场。终裁后同一截止时点的[覆盖表](../../Log-analyse/S-batch/coverage-status.json)为 35 条现场、16 条正式准入、9 条 invalid、10 条 pending；更新前生成表留于[快照](../../Log-analyse/S-batch/snapshots/2026-11-17-before-delivery-gate-r13-adjudication/)。
