# tool-bash A/B/A 机制探针结果（2026-11-23）

## 实验身份

- 目录：`experiments/mechanism-probe-tool-bash-2026-11-23/aba-01/`
- 镜像：`harness-p0-dsh:20261120`；配置：`workspace-write`、`deepseek-flash` / `deepseek-official` / `high`
- 题面：`data.gz`（gzip CSV，60 条）解压后逐条汇总到 `cross_ref.md` 并给出总计（冻结真值 7830）
- 唯一改动：`tool-bash` 开 → 关 → 开
- 读取隔离：内部网络、`--cap-drop ALL`、非特权、无挂载，每臂独立容器与 run 身份

## 三臂结果

| 臂 | tool-bash | 工具目录含 bash | 产物分 | 说明 |
|---|---|---|---|---|
| A1（run1）| 开 | 是 | **7.00/7**（60/60 + 总计 7830）| 解压成功 |
| B（run2）| 关 | **否** | **0.0/7**（cross_ref.md 不存在）| 无执行通道 |
| A2（run3）| 开 | 是 | **7.00/7**（60/60 + 总计 7830）| 解压成功 |

三臂 observed 均为 `deepseek-flash`、reasoning `high`，cwd `/work`，未超时（15.4s / — / 14.8s）。

## 结论

**A/B/A 闭环成立**：开 → 成功、关 → 失败、开 → 再次成功，唯一变化是 `tool-bash`。B 臂失败是能力缺失（无法解压 gzip），不是网络或权限阻断，按 docs/41 计 `fail`，不记 `invalid`。

同时验证了两道物理门槛：

- `read` 对 gzip 不作二进制拒绝，只按行渲染乱码，未泄露明文数值。
- `workflow`（PTC，`node:vm`）无 `child_process`/`zlib`，无法替代 shell 解压。B 场另出现 1 个嵌套会话（70 事件，主会话 116 事件），模型的旁路尝试未产出 `cross_ref.md`。

## 边界

- 这是**机制灵敏度阳性对照**：证明评测尺子能检出真实的能力缺失差，并提供可反转的三臂先例。
- 它不解释 S11 的 Windows 0/7，也不构成 S 题库新题或正式准入样本。
- 单场三臂、每臂 1 次，不作稳定性结论。
- 残留：vm 构造器链逃逸理论上未排除；本场未触发。

## 现场处置

- 首轮 runner 在 B 臂「会话选择」处崩溃（该场有两个 session 目录）。B 臂执行本身已完成，`run.json` 由归档的会话与产物重建，字段 `recovered: true` 已标注；未补造运行前字段，也未重复调用模型。
- 预算：预算代理记录 121 + 33 条请求；`balance-before/after` 均为 ¥8.03（账面未变，与代理计数并存，不做折算）。
