# fixture 人工签署表

> 规则（`docs/08 §8` + 本轮拍板）：**golden 必须全新起草，partial 可复用历史产物**。
> 状态：`draft` = AI 按 prompt/truth/spec 起草、checker 已复算，可用于开发期回归；`signed` = 评测者人工核对 `WHY.md` 后确认，可用于对外报告引用。

| 题号 | golden | partial | 签署人 | 日期 |
|---|---|---|---|---|
| S06 | signed | signed | 黄钧锶 | 2026-11-21 |
| S09 | draft | draft | — | — |
| S10 | draft | draft | — | — |
| S11 | signed | signed | 黄钧锶 | 2026-11-21 |
| S13 | signed | signed | hjs | 2026-10-23 |
| S17 | signed | signed | hjs | 2026-10-24 |
| S19 | draft | draft | — | — |
| S22 | draft | draft | — | — |
| S24 | draft | draft | — | — |
| S26 | draft | draft | — | — |
| S30 | draft | draft | — | — |
| S31 | draft | draft | — | — |

> 另：S13 增加 `tampered` 变体（B 行静默改写为 0）用于 K1 回归，**已于 2026-10-23 由 hjs 签署**，预期 0.5/7，见 `tests/fixtures/tampered/S13-silent-contradiction/WHY.md`。
> 另：S17 增加 `tampered` 变体（漏写总计行）用于 K2 回归，**已于 2026-10-24 由 hjs 签署**，预期 6.0/7，见 `tests/fixtures/tampered/S17-multifile-crossref/WHY.md`。
> 另：S31 增加 `tampered`（缺失月写成 `0`，预期 6.0）与 `equiv`（同义表述，预期 7.0）两个变体用于 K3 回归，**状态仍 `draft`、待签**；K3 修复仅把它们当回归基线，未签前不得作对外引用分数（U-03）。
>
> 2026-11-21 补记：黄钧锶在本轮对话确认已逐份核看 S06/S11 的 golden、partial 产物及四份 `WHY.md`，同意预期分数分别为 S06 7/7、5.5/7 和 S11 7/7、6/7。此签署仅覆盖四份 fixture，不自动签署其他语义反例、产品行为格或独立复评。
>
> 当前进度：**S06、S11、S13、S17 已签（4/12 题）**；其余 8 题仍为 `draft`（含 S31 的 golden/partial/tampered/equiv 四份）。
