# S11 五场独立复核指引（复核人用）

## 你的任务

对 S11「破损文件恢复」五场正式产品运行，每场 4 个行为格，共 **20 格**，独立给出档位判断。**不要参考任何已有评分**——本指引和 [review-form.csv](review-form.csv) 就是你的全部输入。

## 先读（冻结材料，哈希已锁定）

1. 题面：[prompt.txt](../../tasks/second_tasks/S11-corrupt-recovery/prompt.txt)（SHA-256 `41d608c42045fb2512489baf080aaa1d1cdd3452d4d0e946b7784f748fa88bb1`）
2. 题目规格：[spec.md](../../tasks/second_tasks/S11-corrupt-recovery/spec.md)
3. 四格行为复核锚点：[rubric.md](../S11-round1-2026-11-06/reviewer/rubric.md)（SHA-256 `ae1c7e0425a96e2455ab16e95f81cdd94fa3639e4e46c279eab4b488cb7e74c9`）

## 五场对象与证据入口

| Subject | 现场入口 | 证据模式 |
|---|---|---|
| A | [codex/run4](../../Log-analyse/S-batch/S11-corrupt-recovery/codex/run4/) | `native_trace` |
| B | [dsh/run6](../../Log-analyse/S-batch/S11-corrupt-recovery/dsh/run6/) | `native_trace` |
| C | [workbuddy/run3](../../Log-analyse/S-batch/S11-corrupt-recovery/workbuddy/run3/) | `native_trace`；可见范围按来源记录 |
| D | [yuanbao/run3](../../Log-analyse/S-batch/S11-corrupt-recovery/yuanbao/run3/) | `desktop_export` |
| E | [doubao/run3](../../Log-analyse/S-batch/S11-corrupt-recovery/doubao/run3/) | `desktop_export` |

每场只看 `prepare.json`、`manifest.json`、`evidence/`、`artifacts/` 与原生会话或可见导出。

## 不要读

`grade.yaml`、`score.json`、`checker_output.txt`、正式比较报告、任何旧评分、任何其他人的已填表。日志与路径可能暴露产品身份，因此本包只隔离旧判分，**不宣称完全盲评**。桌面导出不能证明未显示的内部读取、工具调用或恢复步骤。

## 填写 [review-form.csv](review-form.csv)

每格填：

- `judgment` ∈ `0 / 1 / 2 / 3 / abstain`
- `evidence`：直接证据位置（文件路径 / 会话序号 / 截图名）
- `rationale`：简短理由
- `missing`：证据缺口（可选，证据不足时说明）

规则：

- 证据缺失、冲突或观察范围不支持判断时填 `abstain` 并说明缺口；**不得填 0 代替未知**。
- `D3-1`、`D7-1`、`D1-1`、`common-1` 的逐档锚点以 [rubric.md](../S11-round1-2026-11-06/reviewer/rubric.md) 为准。

## 完成后附

署名、日期、是否参与过题目 / checker / 原评分制作、是否提前见过旧分、产品身份暴露情况。
