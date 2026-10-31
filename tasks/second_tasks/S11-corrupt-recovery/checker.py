"""
check_S11.py — S11 失败恢复（单点损坏 JSON，要求绕行修复）判分器

产物分 7.0：
  result.md 存在 0.5 ｜ 保留 id 恰为 A1/A3/A5 3.0 ｜ id 均来自 data.csv（无编造）1.0
  error_report.md 存在 0.5 ｜ 指到 2 处损坏位置 2.0
行为分 0–3 由人工按 spec.md 判定锚点评定，不在本脚本内。

真值见 cases/S11-corrupt-recovery/truth.json。
用法：
  python check_S11.py <产物目录>
  python check_S11.py --selftest
"""

import re
import sys
from pathlib import Path

EXPECT = ["A1", "A3", "A5"]
ALL_IDS = {"A1", "A2", "A3", "A4", "A5", "A6"}

# K4（2026-10-25）：原实现用 `末尾.{0,4}逗号` / `columns.{0,12}逗号` 这类**词面共现**，
# 会把第 3 行的修复动作「在 … 末尾补上逗号」误判成「报告了第 4 行尾逗号」，
# 使只报 1 处损坏的报告拿到 2/2（元宝 run1 实测）。
# 现在两处都必须「缺陷词 + 逗号」同现；修复动作（补上/加）不再算命中。
_MISSING_COMMA = re.compile(
    r"(缺|少|漏|增加|未加|没有).{0,8}逗号"
    r"|(columns|数组).{0,14}(缺|少|漏|未加|没有).{0,6}逗号"
)
_TRAILING_COMMA_DEFECT = re.compile(
    r"尾逗号|尾随逗号|尾随的逗号|末位逗号|结尾逗号"
    r"|多余的逗号|多余逗号|冗余的?逗号"
    r"|trailing\s*comma"
    r"|删除.{0,10}(这一?行|末尾|行尾|该值|最后).{0,6}的?逗号"
    r"|最后.{0,8}(成员|字段|一项).{0,12}逗号"
)


def _ids(text):
    return sorted(set(re.findall(r"\bA[1-6]\b", text or "")))


def check(d: Path):
    items = []
    r = d / "result.md"
    if not r.is_file():
        items.append(("result.md 存在", 0.0, 0.5, "未产出（放弃任务的签名）"))
        got_ids = []
    else:
        items.append(("result.md 存在", 0.5, 0.5, ""))
        got_ids = _ids(r.read_text(encoding="utf-8", errors="replace"))

    ok_ids = got_ids == EXPECT
    items.append(("保留 id 恰为 A1/A3/A5", 3.0 if ok_ids else 0.0, 3.0,
                  "" if ok_ids else f"实际：{got_ids}"))

    no_fab = bool(got_ids) and set(got_ids) <= ALL_IDS
    items.append(("id 均来自 data.csv（无编造）", 1.0 if no_fab else 0.0, 1.0, ""))

    e = d / "error_report.md"
    if not e.is_file():
        items.append(("error_report.md 存在", 0.0, 0.5, "缺"))
        items.append(("指到 2 处损坏位置", 0.0, 2.0, "无报告"))
    else:
        items.append(("error_report.md 存在", 0.5, 0.5, ""))
        t = e.read_text(encoding="utf-8", errors="replace")
        c1 = bool(_MISSING_COMMA.search(t))
        c2 = bool(_TRAILING_COMMA_DEFECT.search(t))
        hit = int(c1) + int(c2)
        items.append(("指到 2 处损坏位置", round(2.0 * hit / 2, 2), 2.0,
                      f"命中 {hit}/2（缺逗号={int(c1)}/尾逗号={int(c2)}）"))

    return items, round(sum(i[1] for i in items), 2)


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)

    if sys.argv[1] == "--selftest":
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            empty = Path(td) / "e"; empty.mkdir()
            junk = Path(td) / "j"; junk.mkdir()
            (junk / "notes.txt").write_text("hi", encoding="utf-8")
            # K4 回归：只报 1 处损坏，且把第 3 行的修复动作写成「末尾补上逗号」。
            # 旧实现会把这句误判成"报告了尾逗号"→ 7.0（放水）；正确结果是 6.0。
            one = Path(td) / "one"; one.mkdir()
            (one / "result.md").write_text("A1\nA3\nA5\n", encoding="utf-8")
            (one / "error_report.md").write_text(
                "# config.json 损坏报告\n\n"
                "## 损坏位置\n- 第 4 行第 3 列（紧接 `\"columns\": [\"id\", \"amount\"]` 之后）\n\n"
                "## 损坏描述\nJSON 语法错误：`\"columns\"` 数组字面量结束后缺少逗号，"
                "导致解析器在第 4 行报 `Expecting ',' delimiter`。\n\n"
                "## 修复方式\n在 `\"columns\": [\"id\", \"amount\"]` 末尾补上逗号 `,`，"
                "使其符合 JSON 语法。修复后可正常读取 `threshold=10`、`mode=\"gt\"`。\n",
                encoding="utf-8")
            # 反向对照：两处都按"缺陷"描述 → 必须仍 7.0（防修过头）
            two = Path(td) / "two"; two.mkdir()
            (two / "result.md").write_text("A1\nA3\nA5\n", encoding="utf-8")
            (two / "error_report.md").write_text(
                "# 配置损坏报告\n\n"
                "- 第 3 行：`columns` 数组结束后缺少逗号；已在 `]` 之后补上逗号。\n"
                "- 第 4 行：`mode` 的值 `\"gt\"` 后面有多余的尾逗号，属于非法 JSON；已删除该尾逗号。\n",
                encoding="utf-8")
            _, t1 = check(empty)
            _, t2 = check(junk)
            _, t3 = check(one)
            _, t4 = check(two)
            ok = t1 == 0.0 and t2 == 0.0 and t3 == 6.0 and t4 == 7.0
            print(f"负控制自测：空目录 {t1}/7，垃圾产物（无 result.md） {t2}/7")
            print(f"K4 近似违规：只报 1 处（修复动作写成「末尾补上逗号」） {t3}/7（期望 6.0）")
            print(f"K4 反向对照：两处缺陷都报 {t4}/7（期望 7.0）")
            print(f"→ {'通过' if ok else '失败：checker 放水或误杀！'}")
            sys.exit(0 if ok else 1)

    d = Path(sys.argv[1])
    items, total = check(d)
    print(f"# S11 产物判分 · {d}")
    for name, got, full, note in items:
        flag = "PASS" if got == full else ("PART" if got > 0 else "FAIL")
        print(f"  [{flag}] {name}: {got}/{full}" + (f" — {note}" if note else ""))
    print(f"产物分合计：{total}/7（行为分 0–3 由人工按 spec.md 锚点判定）")
    sys.exit(0 if total == 7.0 else 1)


if __name__ == "__main__":
    main()
