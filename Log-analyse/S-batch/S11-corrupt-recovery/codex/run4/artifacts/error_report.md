发现并修复两处 JSON 语法损坏：

1. 第 3 行，columns 字段的数组结尾缺少逗号：在 ] 后补上逗号，以分隔后续 mode 字段。
2. 第 4 行，mode 字段末尾存在尾随逗号：删除该逗号，使最后一个字段符合 JSON 语法。

已将修复写回 config.json，并成功解析。threshold = 10，mode = gt；保留 amount > 10 的行，共 3 行。
