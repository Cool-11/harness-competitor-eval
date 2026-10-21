# second_tasks/all-inputs · 取件区（第二批 S01–S35）

> 用途：批量跑测时的**唯一取件处**。真源在 `tasks/second_tasks/<题号>-<slug>/`，本目录只是副本。
> 纪律：**不得整体投喂**。每次只取该题对应子目录内的文件 + 该题的 `<题号>_prompt.txt`。

## 取件方式

| 要什么 | 从这里拿 |
|---|---|
| 任务指令（消息正文） | `<题号>_prompt.txt` |
| 上传的初始文件 | `<题号>-<slug>/` 子目录内的全部文件 |

> S23 / S25 无 `inputs/`（材料内联在 prompt.txt 中），因此没有同名子目录——这是设计如此，不是缺件。

## 清单（35 题）

| 题号 | 真源目录 | inputs 文件数 |
|---|---|---:|
| S01 | S01-information-return-baseline | 1 |
| S02 | S02-changes-coverage | 1 |
| S03 | S03-false-report-temptation | 1 |
| S04 | S04-machine-readable-return | 1 |
| S05 | S05-multi-artifact-return | 2 |
| S06 | S06-artifact-deep-path | 1 |
| S07 | S07-same-name-conflict | 2 |
| S08 | S08-dependent-artifact-dir | 2 |
| S09 | S09-strict-csv | 1 |
| S10 | S10-chat-only-temptation | 1 |
| S11 | S11-corrupt-recovery | 2 |
| S12 | S12-chained-corruption | 3 |
| S13 | S13-silent-contradiction | 1 |
| S14 | S14-late-failure | 1 |
| S15 | S15-degrade-partial | 4 |
| S16 | S16-multifile-baseline | 5 |
| S17 | S17-multifile-crossref | 8 |
| S18 | S18-multifile-many | 30 |
| S19 | S19-longdoc-middle | 1 |
| S20 | S20-early-constraint-loss | 1 |
| S21 | S21-forbidden-actions | 1 |
| S22 | S22-top10-only | 1 |
| S23 | S23-contradictory-stop | 0 |
| S24 | S24-resource-boundary | 8 |
| S25 | S25-infinite-refine | 0 |
| S26 | S26-privilege-embedded | 1 |
| S27 | S27-multi-violation | 1 |
| S28 | S28-induced-violation | 1 |
| S29 | S29-confirm-then-trespass | 1 |
| S30 | S30-readonly-boundary | 3 |
| S31 | S31-silent-anomaly-hard | 1 |
| S32 | S32-process-trace | 1 |
| S33 | S33-self-report-contradiction | 1 |
| S34 | S34-longtask-no-progress | 3 |
| S35 | S35-ambiguity-avoid | 1 |

## 同步自检

```powershell
# 逐题比对取件区与真源是否逐字节一致
Get-ChildItem tasks\second_tasks -Directory | Where-Object { $_.Name -match '^S\d\d-' } | ForEach-Object {
  $short = ($_.Name -split '-')[0]
  $src = Join-Path $_.FullName 'inputs'
  $dst = Join-Path 'tasks\second_tasks\all-inputs' $_.Name
  if (Test-Path $src) {
    Get-ChildItem $src -Recurse -File | ForEach-Object {
      $rel = $_.FullName.Substring($src.Length)
      if (-not (Test-Path (Join-Path $dst $rel))) { Write-Output "缺件: $short$rel" }
    }
  }
}
```
