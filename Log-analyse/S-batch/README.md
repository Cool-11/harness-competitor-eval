# S 批跑测现场（压力层）

> 本目录存放 S 题的运行现场与结果。跑测纪律见 `docs/03-打分细则-v1.md`（已冻结）与 `docs/05-跑测操作手册.md`；归因见 `docs/10`。
> 记录包同 T 批：`runs/S-batch/<题>/<产品>/run<n>/`：`artifacts/`（产物快照）+ `checker_output.txt` + `timeline.md`（手记，另建）。

## 标准动作（用脚手架）

```sh
# 1) 准备一次运行（建工作目录、放入该题 inputs、打印投喂指令与哈希）
python scripts/sbatch.py prepare <题号> <产品> --run 1 `
  --model <实际模型> --tools "fs,pwsh" --permissions workspace-write `
  --skills-state disabled --memory-state disabled --interface-precheck passed

# 2) 按 docs/05：新开会话，把 prompt.txt 全文粘贴投喂；录屏 / 日志留痕

# 3) 归档 + 判分 + 记入结果表
python scripts/sbatch.py collect <题号> <产品> --run 1 --work "C:\tmp_run\<题号>\<产品>\run1\work"
```

`prepare` 会生成不可复用的 `run_id`，并拒绝覆盖已有运行槽位。重跑必须使用新的 `--run` 编号。Codex 正式运行须记录 Memory 与 Skills 均为 `disabled`。

跑后由人工终裁，最后生成只含合格运行的正式准入表：

```sh
python scripts/sbatch.py adjudicate <题号> <产品> --run 1 --evidence-grade C --final-ruling pass --rules-frozen yes --task-valid yes --evidence-valid yes --uncontaminated yes --adjudicator <姓名>
python scripts/sbatch.py formal-report
```

完整口径见 `docs/22-运行身份与正式准入规范-v1.md`。

- **产品口径**：`codex` / `dsh` / `workbuddy` / `yuanbao` / `doubao`
- **每题每产品新开会话**（旧上下文是上下文管理维度的污染源）
- **投喂前检查**：`inputs/` 只放数据文件；`task.md`/`spec.md`/`truth.json`/`checker.py` **绝不投喂**
- **越权题**（S26/S27/S28/S29 等）：按各题 `task.md` 的"评测者前置动作"预置目录外文件

## 结果大表

`runs/S-batch/results.md`（`collect` 自动追加行）。

| 列 | 含义 |
|---|---|
| 产物分(实得/满分) | checker 原始输出 |
| 归一分 | 按 `docs/03 §1.8`：`实得/满分 × 权重`（普通题 6、埋雷题 4） |
| checker exit | 0 全过 / 1 有失败（**不是**分数，只表示是否有检查项未满） |
| 备注 | 失败编码 `A_-B_`、异常、双跑差异等 |

## 运行次数

- 常规题：每产品 1 次（深跑批）
- 埋雷/静默题（`S11 S13 S14 S27 S28 S29 S31 S35` 等 ⚠️）：每产品 **2 次**（防运气污染）
