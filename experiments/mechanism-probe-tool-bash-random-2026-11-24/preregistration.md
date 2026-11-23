# tool-bash 随机值探针 · 预注册（2026-11-24）

## 目的

v1（`mechanism-probe-tool-bash-2026-11-23`）的题面金额是 `101..160` 规则序列，模型在无 `bash` 时按规律重建出全部答案，B 臂 7.00/7，A/B/A 不成立。本版只改输入数据：**金额改为固定种子随机值**，消除规律推断旁路，检验 `tool-bash` 的边际贡献。

## 唯一改动

| 臂 | tool-bash | 其余条件 |
|---|---|---|
| A1 | 开 | 题面、输入、模型、镜像、网络、权限、其他工具全部相同 |
| B | 关（`tool-bash.disabled: true`）| 同上 |
| A2 | 开 | 同上 |

配置：`workspace-write`、`deepseek-flash` / `deepseek-official` / `high`、`skill` 关闭。

## 与 v1 的差异

- 金额：规则序列 → 固定种子（`random.Random(20261124)`）随机 100–999。
- 主指标：产物分（0–7 连续），不是 pass/fail。
- A2：**必跑**，不以 B 是否归零为前置。
- 反转判据：A2 回到 A1 同分（7.00）。

## 判据与停止条件

1. A1 未满分 → 停止，判题面不可靠，不发 B/A2。
2. B 跑完即继续，不设分数停止线；B 若为 7.00，结论为「`tool-bash` 可被完全替代」，不再发 A2。
3. A2 未回到 7.00 → 判 4 分以下差值来自噪声，题面需再改。
4. 任一臂超时、observed 模型/推理不符、容器污染 → 记 `invalid`，按同配置新槽重开。

## 无效场与证据纪律

每臂独立容器与 run 身份；保留 `shared.yml`、`merged-config.yml`、session、产物与 checker 输出；`tool-diff.json` 记录 A1 与 B 的工具目录差集。代理预算上限 ¥10，日志顺序命名。

## 残留风险

- `workflow`（`node:vm`）无 `child_process`/`zlib`，无法解 gzip；若 B 仍满分，按停止条件 2 登记为替代证据。
- 每臂 n=1，只作一次观察。

## 冻结

- 题面、输入、checker、truth 的哈希在运行时写入 `manifest.json`；镜像 `harness-p0-dsh:20261120`。
- 运行脚本 `scripts/probe_tool_fs_aba.py`（通用组件探针，`--component tool-bash`）。
