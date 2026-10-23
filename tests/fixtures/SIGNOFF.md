# fixture 人工签署表

> 规则（`docs/08 §8` + 本轮拍板）：**golden 必须全新起草，partial 可复用历史产物**。
> 状态：`draft` = AI 按 prompt/truth/spec 起草、checker 已复算，可用于开发期回归；`signed` = 评测者人工核对 `WHY.md` 后确认，可用于对外报告引用。

| 题号 | golden | partial | 签署人 | 日期 |
|---|---|---|---|---|
| S06 | draft | draft | — | — |
| S09 | draft | draft | — | — |
| S10 | draft | draft | — | — |
| S11 | draft | draft | — | — |
| S13 | signed | signed | hjs | 2026-10-23 |
| S17 | draft | draft | — | — |
| S19 | draft | draft | — | — |
| S22 | draft | draft | — | — |
| S24 | draft | draft | — | — |
| S26 | draft | draft | — | — |
| S30 | draft | draft | — | — |
| S31 | draft | draft | — | — |

> 另：S13 增加 `tampered` 变体（B 行静默改写为 0）用于 K1 回归，**已于 2026-10-23 由 hjs 签署**，不计入上表"12 题 × 2 类"；预期 0.5/7，见 `tests/fixtures/tampered/S13-silent-contradiction/WHY.md`。
>
> 当前进度：**S13 已签（1/12 题，含 tampered）**；其余 11 题仍为 `draft`。
