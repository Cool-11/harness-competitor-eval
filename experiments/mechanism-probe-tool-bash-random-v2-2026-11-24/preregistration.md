# tool-bash 随机值探针 v2 · 预注册（2026-11-24）

## 与 v1 的唯一差异

题面新增一句退出指令（三臂完全相同，不构成 treatment 差异）：

> 若工作目录中的文件无法读取或解压，请在 `cross_ref.md` 写明原因并立即结束，不要尝试其他绕过方式。

原因：v1 的 B 臂在缺少 `bash` 时持续尝试旁路，105s / 43 次请求后被代理 ¥10 上限截断，只能记 `invalid`。退出指令让 B 臂自然结束，得到可解释的产物分。

## 三臂

| 臂 | tool-bash | 其余条件 |
|---|---|---|
| A1 | 开 | 同题面、同输入、同模型、同镜像、同网络与权限 |
| B | 关 | 同上 |
| A2 | 开 | 同上 |

配置：`workspace-write`、`deepseek-flash` / `deepseek-official` / `high`、`skill` 关闭。

## 判据

- A1 未满分 → 停止，判题面不可靠。
- B 预期 ≈ 1.0/7（只有文件存在分，写明原因）；若 B=7.00，结论为「`tool-bash` 可被完全替代」。
- 反转判据：A2 回到 7.00。
- 任一臂被预算上限截断、超时或污染 → 记 `invalid`，不折算。

## 版本与历史

- v1（`mechanism-probe-tool-bash-random-2026-11-24`）：A1 7.00，B 因预算截断记 invalid。原始记录不改写。
- 本版仅改 prompt；`inputs`、`checker`、`truth` 与 v1 相同哈希。

## 冻结与预算

- 镜像 `harness-p0-dsh:20261120`；脚本 `scripts/probe_tool_fs_aba.py`；代理上限 ¥10，日志顺序命名。
- 每臂 n=1，只作一次观察。
