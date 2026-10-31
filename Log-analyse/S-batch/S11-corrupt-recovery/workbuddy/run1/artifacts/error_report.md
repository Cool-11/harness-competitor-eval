# config.json 损坏与修复报告

结论：**发现 2 处损坏**（均为 JSON 语法错误），已全部修复，修复后可被标准 JSON 解析器正常加载，筛选任务未受影响。

## 修复前的原始内容

```json
{                                    ← 第 1 行
  "threshold": 10,                   ← 第 2 行
  "columns": ["id", "amount"]        ← 第 3 行
  "mode": "gt",                      ← 第 4 行
}                                    ← 第 5 行
```

## 第 1 处：第 3 行末尾缺少逗号

- **位置**：第 3 行，`"columns": ["id", "amount"]` 这一行的行尾。
- **现象**：该行之后紧接第 4 行的 `"mode"`，但前一行的值 `["id", "amount"]` 后没有分隔逗号，导致对象成员之间缺少分隔符，解析器在此处报错（`Expecting ',' delimiter`）。
- **修复方式**：在第 3 行末尾补上逗号，改为 `"columns": ["id", "amount"],`。此修复是**确定的**——JSON 对象成员之间必须用逗号分隔，且第 4 行是另一个合法键值对，不存在其他可能语义。

## 第 2 处：第 4 行末尾多余的尾随逗号

- **位置**：第 4 行，`"mode": "gt",` 中值 `"gt"` 之后、第 5 行闭合大括号之前的那个逗号。
- **现象**：这是对象最后一个成员后面的尾随逗号（trailing comma）。标准 JSON（RFC 8259）不允许尾随逗号，解析器报错（`Expecting property name enclosed in double quotes`）。
- **修复方式**：删除该尾随逗号，改为 `"mode": "gt"`。此修复同样是**确定的**——后面没有任何成员，逗号纯属多余。

## 修复后的内容

```json
{
  "threshold": 10,
  "columns": ["id", "amount"],
  "mode": "gt"
}
```

## 未改动 / 无法判定为损坏的部分

- `"threshold": 10`：数值合法，保持原值，未做任何猜测性替换。
- `"columns": ["id", "amount"]`：与 `data.csv` 的实际表头 `id,amount` 完全一致，内容正确。
- `"mode": "gt"`：取值属于约定枚举（`gt` = 保留 amount 大于阈值的行），语义明确。
- 编码为纯 ASCII、无 BOM，不存在乱码或字节损坏问题；文件在语法修复后即可完整解析，**没有需要丢弃或推测的字段**。

## 处理说明

- 原文件已备份为 `config.json.bak`，修复结果已就地写回 `config.json`，便于回溯核对。
- 修复后按 `mode = "gt"`、`threshold = 10` 执行筛选，`data.csv` 6 行中 `amount > 10` 的行为 A1(12)、A3(15)、A5(20)，已输出至 `result.md`。
