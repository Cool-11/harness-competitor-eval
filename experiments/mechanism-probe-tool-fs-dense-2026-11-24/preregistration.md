# tool-fs 高密度图像探针 · 预注册（2026-11-24）

## 目的

v1（`mechanism-probe-tool-fs-2026-11-24`，6 行、大字号）中，B 臂在 `tool-fs` 关闭后用 `bash` + 纯 Python 解码 PNG、ASCII 渲染目视 OCR，仍得 4.33/7。本版提高信息密度与还原成本，检验 `tool-fs` 的边际贡献是否增大。

## 相对 v1 的改动（只改输入）

| 项 | v1 | 本版 |
|---|---|---|
| 行数 | 6 | **12** |
| 字号 | 44 / 38 / 34 | **34 / 26 / 24** |
| 排版 | 整齐栅格 | 每行 ±6px 水平抖动 |
| 数值 | 137/248/51/469/322/190 | 固定种子随机 100–999 |

题面、checker 结构（存在 1.0 + 逐条 4.0 + 总计 2.0）不变。

## 三臂

| 臂 | tool-fs | 其余条件 |
|---|---|---|
| A1 | 开 | 题面、输入、模型、镜像、网络、权限、其他工具全部相同 |
| B | 关（`tool-fs.disabled: true`）| 同上；`tool-bash` 保持开 |
| A2 | 开 | 同上 |

配置：`workspace-write`、`deepseek-flash` / `deepseek-official` / `high`、`skill` 关闭。

## 判据与停止条件

1. A1 未满分 → 停止，判为字号过小导致不可读（题包缺陷），不发 B/A2。
2. B 跑完即继续，不设分数停止线；B 若为 7.00，结论为「`tool-fs` 可被完全替代」，不再发 A2。
3. 反转判据：A2 回到 7.00。
4. 任一臂超时、observed 模型/推理不符、容器污染 → 记 `invalid`，按同配置新槽重开。

## 证据与预算

每臂独立容器与 run 身份；保留 `shared.yml`、`merged-config.yml`、session、产物与 checker 输出；`tool-diff.json` 记录工具目录差集。代理预算上限 ¥10，日志顺序命名。

## 残留风险

- 字号缩小可能同时降低 A1 的可读性；A1 未满分即按停止条件 1 处理，不把题包缺陷记成产品失败。
- 每臂 n=1，只作一次观察；B 的部分得分含 OCR 噪声。

## 冻结

- 输入由 `make_inputs.py` 生成（Pillow 13.0.0，Consolas）；哈希在运行时写入 `manifest.json`。
- 镜像 `harness-p0-dsh:20261120`；运行脚本 `scripts/probe_tool_fs_aba.py`。
