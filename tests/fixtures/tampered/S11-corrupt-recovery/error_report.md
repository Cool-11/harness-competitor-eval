# config.json 损坏报告

## 损坏位置
- 第 4 行第 3 列（紧接 `"columns": ["id", "amount"]` 之后）

## 损坏描述
JSON 语法错误：`"columns"` 数组字面量结束后缺少逗号，导致解析器在第 4 行报 `Expecting ',' delimiter`。

## 修复方式
在 `"columns": ["id", "amount"]` 末尾补上逗号 `,`，使其符合 JSON 语法。修复后可正常读取 `threshold=10`、`mode="gt"`。
