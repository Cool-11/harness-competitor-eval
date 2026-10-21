# Log-analyse/Log-analyse · 五款产品批量日志与产物现场

> 前身：`Log-analyse/Five-app-log-analyse/`（2026-10-21 改名）。
> 记录包按**第几轮**分层：`first-run-artifact`（第一批 T00–T14）、`second-run-artifact`（第二批 S01–S35）。

## 目录结构

```
Log-analyse/<产品>-log-analyse/
├── session.log                     # 产品输出日志（原始/导出）
├── checker_output.txt              # 当时 checker 的原始输出（历史证据，不改写）
├── artifacts/
│   ├── first-run-artifact/
│   │   ├── <题号>-<slug>/          # 第一批 16 题产物快照
│   │   ├── shots/<题号>/S1..S5.png # 关键节点截图（按题分目录）
│   │   └── recording/              # 产品输出日志副本（txt / csv / md）
│   └── second-run-artifact/
│       ├── <题号>-<slug>/          # 第二批 S01–S35 产物快照
│       ├── shots/<题号>/
│       └── recording/
```

## 命名与放料纪律

1. **按轮次分**：第几次批量跑就放对应的 `*-run-artifact`，不混层。
2. **按题分**：产物子目录名与真源目录名一致（`S06-artifact-deep-path`）。
3. **shots 按题分**：`shots/S06/S1.png`…，S 编号定义见 `docs/07 §3.1`。
4. **recording 放日志**：产品输出的 txt / csv / md 一律放 `recording/`；录屏链接仍写各题 `recording.txt`。
5. **不改写历史**：`session.log`、`checker_output.txt` 属原始证据，路径迁移只做记录、不改内容。

## 路径迁移记录（2026-10-21）

| 旧路径 | 新路径 |
|---|---|
| `Log-analyse/Five-app-log-analyse/` | `Log-analyse/` |
| `artifacts/T00-hello-world` … `artifacts/T14-silent-anomaly-trap` | `artifacts/first-run-artifact/<同名>` |

> `checker_output.txt` 与 `session.log` 中记录的仍是**旧路径**（保全原则不改写）。复现时按上表做前缀替换即可。
