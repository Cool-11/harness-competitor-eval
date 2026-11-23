# tool-fs 图像探针 · 三臂预注册（2026-11-24）

## 目的

用「只有 `read_image` 才能看见答案」的题面，使 `tool-fs` 成为物理必需的单变量，完成 A→B→A 因果闭环。与 2026-11-23 的 `tool-bash` 探针同属机制灵敏度阳性对照，不解释 S11，也不构成新 S 题或正式准入样本。

## 为什么必须用图像

- `read`/`write`/`edit`/`read_image` 都隶属 `tool-fs`；配置树里没有单独的「图像读取」开关（`image-offload` 是上下文压缩组件，不是读图工具）。
- `tool-bash` 保持开启时，文本任务的输入输出都能被 shell 替代（`cat`/`echo`/`sed`），关闭 `tool-fs` 不构成物理缺失。
- PNG 内容只能经 `read_image` 呈现给模型；`bash` 读出的是二进制乱码。因此只有图像型任务能让 `tool-fs` 成为唯一通路。

## 任务包（冻结）

- 输入：`inputs/inventory.png`，6 行库存表（编号 + 数量），白底黑字、无总计行。
- 题面：转录到 `cross_ref.md` 并给出总计。
- 真值：`truth.json`，总计 1417。
- checker：`checker.py`，逐条 4.0 + 总计 2.0 + 文件存在 1.0 = 7.0，机械比对。

## 三臂

| 臂 | tool-fs | 其余条件 |
|---|---|---|
| A1 | 开 | 题面、输入、模型、镜像、网络、权限、其他工具全部相同 |
| B | 关（`tool-fs.disabled: true`）| 同上；`tool-bash` 保持开 |
| A2 | 开 | 同上 |

配置：`workspace-write`、`deepseek-flash` / `deepseek-official` / `high`、`skill` 关闭。

## 判据与停止条件

- 成功：7.00/7（含总计）。
- A1 未满分 → 停止，判为题面不可靠（OCR/渲染问题），不发射 B/A2，登记为无效题包。
- B 得分 > 1.05（15% 总分）→ 停止，说明存在未识别通路，登记失败模式，不发射 A2。
- 任一臂超时、observed 模型/推理不符、容器污染 → 该臂 `invalid`，不折算，按同配置新槽重开。

## 无效场与证据纪律

每臂独立容器与 run 身份；保留 `shared.yml`、`merged-config.yml`、session、产物与 checker 输出；`tool-diff.json` 记录 A1 与 B 的工具目录差集，作为开关生效的机械证据。

## 残留风险

- 模型 OCR 误差可能让 A1 失分；这正是停止条件 1，不把题包缺陷记成产品失败。
- vm 构造器链逃逸理论上未排除；若 B 臂成功，按停止条件 2 处理。

## 预算

三臂，各 ≤ ¥2（600s 上限）。

## 冻结与复现

- 输入由 `make_inputs.py` 生成（Pillow 13.0.0，Consolas 38/44/34 号字）；文件哈希在运行时写入 `manifest.json`。
- 镜像 `harness-p0-dsh:20261120`；脚本 `scripts/probe_tool_fs_aba.py`。
