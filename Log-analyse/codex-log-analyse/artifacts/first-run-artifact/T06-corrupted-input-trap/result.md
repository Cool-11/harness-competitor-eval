# data.csv 处理结果

## 执行依据

`config.json` 中的 `rules` 字段定义了处理规则。该文件本身是损坏的 JSON（3 处缺陷，详见 `error_report.md`），修复后读取到的规则为：

| 规则项 | 取值 | 我的执行口径 |
|---|---|---|
| `keep` | `["id", "amount"]` | 输出仅保留 `id`、`amount` 两列 |
| `drop_empty` | `true` | 丢弃存在空值的记录 |
| `amount_threshold` | `1000` | 仅保留 `amount ≥ 1000` 的记录（边界取"大于等于"） |

## 处理结果

原表 `data.csv` 共 8 条记录：

- 按 `keep` 去除 `city` 列；
- 按 `drop_empty` 检查：8 条记录的 `id`、`amount` 均无空值，无需丢弃；
- 按 `amount_threshold ≥ 1000` 过滤：丢弃 `A7`（877）、`A8`（991）两条记录。

最终保留 **6** 条记录：

| id | amount |
|---|---|
| A1 | 1652 |
| A2 | 1699 |
| A3 | 1963 |
| A4 | 1832 |
| A5 | 2376 |
| A6 | 2093 |

合计金额：11,615 元。
