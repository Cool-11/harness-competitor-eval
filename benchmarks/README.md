# benchmarks/ · 评测 frame 与冻结指纹

> 本目录定义“这次评测到底跑哪些题、哪些产品、几次、按什么成功合同”，不存产品表现。

## 文件

| 文件 | 作用 |
|---|---|
| `harness-v1-pilot.json` | S06 单题试点 manifest：五款 × 1 题 × 1 trial |
| `pins.json` | S06 题包文件哈希与题集摘要 |

## 口径

- `task_subsets.<name>.sha256` = 该题集所有文件 `相对路径:sha256` 排序后用 `\n` 连接，再取 SHA-256。
- 改题面、`prompt.txt`、`inputs/`、`checker.py`、`spec.md`、`truth.json` 中任意一项，都必须更新 `pins.json` 并升级 `revision`。
- 试点阶段只登记 S06；扩到 12 题时新增 subset，不改已有 revision。
- manifest 不是投喂内容，产品不可见。

## 试点范围

`harness-v1-pilot.json` 只用于验证：

1. 五款各 1 次运行能否走通；
2. 证据包是否齐全；
3. checker → `score.json` → `run.json` → `pilot-results.json` 是否能复算。

**试点结果不作五款排名。**
