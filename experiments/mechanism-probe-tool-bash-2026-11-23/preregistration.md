# tool-bash 机制探针 · 三臂预注册（2026-11-23）

## 目的

方向 E 的最后一个可行落点：用一个「必须执行外部程序才能完成」的题面，让 `tool-bash` 成为物理必需的单变量，完成 A→B→A 因果闭环。

本实验是**机制灵敏度验证**（证明评测尺子能检出真实的能力缺失差），不解释 S11 的 Windows 0/7，也不构成新的 S 题或正式准入样本。

## 题面与物理门槛

- 输入 `inputs/data.gz`：gzip 压缩的 CSV（60 条，列 `编号,金额`）。解压后逐条汇总到 `cross_ref.md` 并给出总计。
- 已核查的两道门槛（2026-11-23，静态）：
  1. `tool-fs` 的 `read` 无二进制守卫，只按行渲染 + 截断 → gzip 读出来是乱码，不泄露明文数值；二进制守卫只作用于 patch。
  2. `workflow`（PTC）运行在 `node:vm` 上下文，`createContext` 后逐键复制 `globalThis`；`dsh-ptc-runtime*`/`dsh-workflow*`/`dsh-tool-workflow` 均无 `child_process`、无 `node:fs`、无 `node:zlib`；唯一 `spawn` 是宿主侧启动受限 node 进程。
- 因此关掉 `tool-bash` 后：不能执行 shell、不能解 gzip。纯算术绕过（如 S18 求和）仍然存在，所以本题面刻意不采用「可心算」的数据形态。

## 唯一改动

| 臂 | tool-bash | 其余条件 |
|---|---|---|
| A1 | 开 | 题面、输入、模型、镜像、网络、权限、其他工具全部相同 |
| B | 关（`tool-bash.disabled: true`）| 同上 |
| A2 | 开 | 同上 |

其他组件保持与 S30/S26 baseline 相同的配置（`workspace-write`、`approval` 按预设、`skill` 关闭）。

## 预期与判据

- A1/A2：产物分 7/7。
- B：无法解压 → `cross_ref.md` 缺失或内容错误 → 产物分 ≤ 1.0。
- 闭环成立条件：A1 成功、B 失败、A2 成功；三次 observed model 均为 `deepseek-flash`、reasoning `high`。

## 停止条件

1. A1 失败（题面本身不可完成）→ 停止，题面作废，不发射 B/A2。
2. B 成功（存在未识别的绕过通道）→ 停止，登记失败模式，不发射 A2。
3. 任一臂超时、observed 模型/推理不符、容器污染 → 该臂 `invalid`，不折算分数，按同一配置重开新槽。

## 无效场与证据纪律

- 每臂独立容器、独立 run 身份，禁止覆盖。
- 保留容器 identity、merged-config、原生 session、产物与 checker 输出。
- 失败是能力缺失（非网络/权限阻断），按 docs/41 计 `fail`；不写成 `invalid`。

## 残留风险（未排除）

- vm 构造函数链逃逸在理论上可能让 `workflow` 获得宿主能力；本预注册承接为「低概率未排除」，若 B 臂成功则按停止条件 2 处理。

## 预算

三臂，各 ≤ ¥2（deepseek-flash，600s 上限）。

## 冻结

- 题面/输入/checker/truth 的 SHA-256 见 `manifest.json`。
- 镜像 `harness-p0-dsh:20261120`；脚本 `scripts/probe_tool_bash_aba.py`。
