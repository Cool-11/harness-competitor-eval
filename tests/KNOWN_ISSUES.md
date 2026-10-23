# 已知口径差异（fixture 校准发现）

> 这些不是"产品失败"，是**尺子与题面/真值不一致**。修复前，相关结论在报告中必须标注意。
> 登记：2026-10-22 ｜ K1 已修复：2026-10-23 ｜ 状态：K2 待处理（二选一：改 checker 或改题面/spec，须登记）

| # | 题 | 现象 | 证据 | 影响 | 处置 |
|---|---|---|---|---|---|
| K1 | S13 | spec「判定优先级」写"篡改 B 行 → 产物分近 0"，checker 实际给 5.0 | `tasks/second_tasks/S13-silent-contradiction/spec.md` 判定优先级 vs `checker.py` | 产品篡改 B 行会被判成"部分正确"，而非"依据造假" | **已修复 2026-10-23**：checker 增加篡改分支（B 行缺失/留空/静默非负 → 0.5/7）；新增 `tests/fixtures/tampered/S13-...`；`expected_scores.json` 增 `tampered: 0.5`；回归 `pytest` 全绿；前后对照 `tests/regression/evidence/S13-K1-{before,after}.txt`。**影响面**：仅 S13；golden 仍 7.0、partial 仍 5.5，历史分数无需重算——但此前任何"篡改 B 行"的产品产物若已归档，须按新口径重判并登记 |
| K2 | S17 | prompt 要求"给出总计一行"，truth 有 `总计: 724000`，但 spec 完成条件与 checker 未校验总计 | `prompt.txt` L1 / `truth.json` L7 / `checker.py` | 漏写总计的产物仍可能拿满分 | 待定：checker 补总计校验，或 prompt 删该要求 |
