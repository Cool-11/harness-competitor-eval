# config.json 损坏报告

发现 **2 处** JSON 语法损坏，均已修复。修复后 `config.json` 可被标准 JSON 解析器正常解析，配置值为 `threshold = 10`、`mode = "gt"`、`columns = ["id", "amount"]`。

## 损坏 1：缺少字段分隔逗号

- **位置**：第 3 行，字段 `columns` 所在行末（即 `"columns": ["id", "amount"]` 之后、第 4 行 `"mode"` 之前）
- **原始内容**：
  ```json
    "columns": ["id", "amount"]
    "mode": "gt",
  ```
- **问题**：JSON 对象中两个成员之间必须用逗号分隔。解析器报错为 `Expecting ',' delimiter: line 4 column 3 (char 53)`，实际缺失位置在第 3 行行末。
- **修复方式**：在第 3 行末尾补上逗号：
  ```json
    "columns": ["id", "amount"],
  ```

## 损坏 2：对象末尾多余逗号

- **位置**：第 4 行，字段 `mode` 的值的末尾（`"mode": "gt",` 的逗号），位于第 5 行右花括号 `}` 之前
- **原始内容**：
  ```json
    "mode": "gt",
  }
  ```
- **问题**：JSON 标准不允许对象最后一个成员后出现尾随逗号（trailing comma）。
- **修复方式**：删除该多余逗号，改为：
  ```json
    "mode": "gt"
  }
  ```

## 修复后完整内容

```json
{
  "threshold": 10,
  "columns": ["id", "amount"],
  "mode": "gt"
}
```

## 说明

- 上述两处均属可确定的语法修复：仅调整逗号，未改动任何字段名或字段值，配置语义保持不变。
- 修复后已用 `json.load` 校验通过，并按 `mode = "gt"`（保留 `amount > threshold` 的行）完成筛选；`data.csv` 中 `amount` 大于 10 的行为 `A1`(12)、`A3`(15)、`A5`(20)，结果见 `result.md`。
