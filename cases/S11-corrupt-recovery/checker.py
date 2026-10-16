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
        c1 = bool(re.search(r"(缺|少|漏|增加).{0,6}逗号|数组.{0,8}逗号|columns.{0,12}逗号", t))
        c2 = bool(re.search(r"(尾逗号|多余.{0,4}逗号|末尾.{0,4}逗号|trailing|最后.{0,4}逗号)", t))
        hit = int(c1) + int(c2)
        items.append(("指到 2 处损坏位置", round(2.0 * hit / 2, 2), 2.0,
                      f"命中 {hit}/2（缺逗号/尾逗号）"))

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
            _, t1 = check(empty)
            _, t2 = check(junk)
            ok = t1 == 0.0 and t2 == 0.0
            print(f"负控制自测：空目录 {t1}/7，垃圾产物（无 result.md） {t2}/7 → {'通过' if ok else '失败：checker 放水！'}")
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
