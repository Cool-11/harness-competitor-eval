# tool-fs 高密度图像探针 v2 · 预注册（2026-11-24）

## 与 v1 的唯一差异

题面新增一句退出指令（三臂完全相同，不构成 treatment 差异）：

> 若无法读取图片，请在 `cross_ref.md` 写明原因并立即结束，不要尝试其他绕过方式。

原因：v1 的 B 臂缺少 `read_image`/`read` 后持续尝试旁路，157s / 29 次请求后被代理 ¥10 上限截断，只能记 `invalid`。退出指令让 B 臂自然结束。

## 三臂

| 臂 | tool-fs | 其余条件 |
|---|---|---|
| A1 | 开 | 同题面、同输入、同模型、同镜像、同网络与权限 |
| B | 关 | 同上；`tool-bash` 保持开 |
| A2 | 开 | 同上 |

配置：`workspace-write`、`deepseek-flash` / `deepseek-official` / `high`、`skill` 关闭。

## 判据

- A1 未满分 → 停止，判字号过小或渲染不可读（题包缺陷）。
- B 预期 ≈ 1.0/7；若 B 仍能 OCR 到部分条目，如实记分；若 B=7.00，结论为「`tool-fs` 可被完全替代」。
- 反转判据：A2 回到 7.00。
- 任一臂被预算截断、超时或污染 → 记 `invalid`。

## 版本与历史

- v1（`mechanism-probe-tool-fs-dense-2026-11-24`）：A1 7.00，B 因预算截断记 invalid。原始记录不改写。
- 本版仅改 prompt；`inputs`、`checker`、`truth` 与 v1 相同哈希。

## 冻结与预算

- 镜像 `harness-p0-dsh:20261120`；脚本 `scripts/probe_tool_fs_aba.py`；代理上限 ¥10，日志顺序命名。
- 每臂 n=1，只作一次观察。
