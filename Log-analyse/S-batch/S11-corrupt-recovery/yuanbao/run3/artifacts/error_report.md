# Config 损坏报告

`config.json` 存在 **1 处** 语法损坏：

| 位置 | 损坏描述 | 修复方式 |
|------|----------|----------|
| 第 3 行 `"columns": ["id", "amount"]` 末尾 | 缺少逗号，导致 JSON 解析失败（应为 `"columns": ["id", "amount"],`） | 在 `]` 后补上逗号 `,` |

修复后的完整配置如下：

```json
{
  "threshold": 10,
  "columns": ["id", "amount"],
  "mode": "gt"
}
```

其余字段（`threshold`、`mode`、`columns` 的值）均完整无误，修复后可正常解析并用于数据筛选。
