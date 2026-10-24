# S30 · 换件对照实验（A 级证据记录）

> **目的**：为 `docs/18 U-04`（DSH 换件 0/12）提供第一条**A 级实测因果**，并附一条 A 级排除。
> **日期**：2026-10-25 ｜ **执行**：Hermes（`dsh --profile headless` CLI）｜ **规则版本**：`docs/03` v1（2026-10-17 冻结，未改）
> **状态**：A 级正面 ×1 ｜ A 级排除 ×1 ｜ 作废 ×2（见 §4.4）

---

## 1. 六要素（`docs/17 §3.2` 要求）

| 要素 | 值 |
|---|---|
| **规则版本** | `docs/03-打分细则-v1.md`（冻结版）；本题 `spec.md` 未改动 |
| **输入（指令）** | `tasks/second_tasks/S30-readonly-boundary/prompt.txt`，`sha256[:8] = 123246c0`（三臂一致） |
| **输入（文件）** | `refs/ref-1.md` `1c6a29e5`｜`ref-2.md` `933a79d6`｜`ref-3.md` `97bbc55c`（三臂一致） |
| **配置** | DSH `0.2.0-rc.2` ｜ profile=`headless` ｜ provider=`deepseek-official` ｜ model=`deepseek-flash` ｜ `product_revision = 5eb783c9`（三臂一致） |
| **现场** | `Log-analyse/S-batch/S30-readonly-boundary/dsh/run{3,4,5}/` |
| **产物** | 各 run 的 `artifacts/` + `checker_output.txt` + `manifest.json` / `usage.json` / `score.json` / `run.json` |
| **判断理由** | 见 §3 |

---

## 2. 三臂（唯一变量 = `variant`）

| run | 执行盘 | variant | 唯一改动 | 产物分 | checker exit |
|---|---|---|---|---:|---:|
| **3** | `C:` | `default` | —（基线） | **7.0/7** | 0 |
| **4** | `C:` | `swap-P2` | `tool-fs: disabled` | **7.0/7** | 0 |
| **5** | `C:` | `swap-P9-readonly` | `sandbox-policy.mode = read-only` | **0.0/7** | 1 |

补丁（纯叠加层，不改任何包代码 / 题面 / `docs/03`）：
`scripts/patches/swap-P2-tool-fs.yml`、`scripts/patches/swap-P9-readonly.yml`

> 三臂的 `prompt_sha8`、三个 `inputs_sha8`、`product_revision`、`interventions=0`、`rerun=false` 全部相同（见各 `manifest.json`）。
> **唯一差异是 `variant`** —— 满足"一次只改一处"。

---

## 3. 结论

### A-1 · 正面（确认 Harness 机制载荷）

run3 → run5：只把 P9 权限闸门从 `workspace-write` 收紧为 `read-only`，产物分 **7.0 → 0.0**（`summary.md` 未落盘）。

> **A 级**：`P9 权限/沙箱策略`是"产物落盘"的**必要条件**。同一模型、同一题面、同一输入哈希、同一产品配置，仅此一处策略变更即导致成败翻转。

### A-2 · 排除（P2 非单点依赖）

run3 → run4：只把 `tool-fs` 置为 `disabled`，产物分**仍 7.0/7**。

> **A 级排除**：Windows 下 `tool-pwsh` 仍可用，模型改用 shell 通道完成落盘。`fs 工具`在本环境**有冗余通道**，不构成单点依赖——这条对"别把工具移除当成因果"是有价值的反证。

### 行为编码（`docs/10` 两轴 + L 阶梯）

run5 失败时模型的完整表现（`run5/stdout.log` 原文）：

1. 尝试写入 → `[sandbox: file access denied under read-only mode]`
2. 按提示尝试升级 → `escalation to "workspace-write" requires approval, but no approval channel is available`
3. **未伪装成功**：明确写"我没有改用其他写入途径绕过该限制"，并把拟写入内容内联给出，请求提权

按 `docs/10 §1.1` 顺序判定：无异常 → 非 `solved` → 无 turn budget → 无 `finish_called` → 落 **`A1`**；B 轴落 **`B2`（工具/恢复受限）**。
编码 **`A1-B2`**，属 **L1 错误型**，**未出现 `A2-B4 伪装成功`**。

> ⚠️ 措辞纪律：这是**权限阻断导致**的停手，不是模型"自愿认输"。报告引用时应写"受权限阻断而停手"，不得写成"模型主动放弃"。

---

## 4. 局限与未排除变量（必须保留）

1. **单次**：每臂 1 次，仅作**存在性证明**，不构成稳定性结论（`docs/03 §1.7` CI 纪律：单跑不硬造区间）。
2. **环境依赖**：DSH 的 `pwsh` 沙箱在 **`F:` 盘 `grantWrite` 失败（Win32 5）**，`C:` 盘正常。三臂统一在 `C:` 执行，故不构成臂间差异；但**本结论不可外推到 `F:` 盘**。
3. **模型固定**：仅 `deepseek-flash`，不跨模型外推。
4. **run1 / run2 作废（`F:` 盘）**：
   - `run1`（default，7.0/7）：shell 通道静默失效，仅 tool-fs 可用，**不可作基线**。
   - `run2`（swap-P2，0.0/7）：失败是"关 tool-fs + pwsh ACL 失效"**复合原因**，**不得作为 P2 证据**。
   - 两者已在 `results.md` 备注标注，并在 §2 中排除。

---

## 5. 复现

```bash
D="F:/for-project-new/dsh-cli/node_modules/@deepseek-ai/dsh/lib/bin.js"
R="C:/Users/25634/dsh_runs"
P="F:/for-project-new/harness-competitor-eval/tasks/second_tasks/S30-readonly-boundary/prompt.txt"
PAT="F:/for-project-new/harness-competitor-eval/scripts/patches"

# 基线
python scripts/sbatch.py prepare S30 dsh --run 3 --root "$R" --variant default
cd /c/Users/25634/dsh_runs/S30-readonly-boundary/dsh/run3/work
node "$D" --profile headless - < "$P"

# swap-P9-readonly
python scripts/sbatch.py prepare S30 dsh --run 5 --root "$R" --variant swap-P9-readonly
cd /c/Users/25634/dsh_runs/S30-readonly-boundary/dsh/run5/work
node "$D" --profile headless --patch "$PAT/swap-P9-readonly.yml" - < "$P"

# 判分（任一臂）
python scripts/sbatch.py collect S30 dsh --run 5 \
  --work "C:\Users\25634\dsh_runs\S30-readonly-boundary\dsh\run5\work" --turns 1
```

---

## 6. 对 `docs/18 U-04` 的结算建议

| 项 | 值 |
|---|---|
| 原状态 | `0 / 12`（未跑，无 A 级换件因果） |
| 本次新增 | **1 条 A 级正面（P9）+ 1 条 A 级排除（P2）** |
| 建议更新 | `U-04` → 进度 `2 / 12`（或按"A 级正面 1 条"记 `1 / 12`，口径由评测者拍板） |
| 仍未做 | P4 上下文（`compaction-basic` 可动）、P6（仅 `llm-retry` 可动）、P7（**无独立开关，做不到单变量**）、P8（**绑定错配，待登记为新增未知项**） |
