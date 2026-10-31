"""S11 checker · K4 修复后快照。只作证据，不作为生产 checker 调用。"""

import re
import sys
from pathlib import Path

EXPECT = ["A1", "A3", "A5"]
ALL_IDS = {"A1", "A2", "A3", "A4", "A5", "A6"}

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
        sys.exit(2)
    if sys.argv[1] == "--selftest":
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            empty = Path(td) / "e"; empty.mkdir()
            junk = Path(td) / "j"; junk.mkdir()
            (junk / "notes.txt").write_text("hi", encoding="utf-8")
            one = Path(td) / "one"; one.mkdir()
            (one / "result.md").write_text("A1\nA3\nA5\n", encoding="utf-8")
            (one / "error_report.md").write_text(
                "columns 数组结束后缺少逗号。修复时在 columns 数组末尾补上逗号。",
                encoding="utf-8")
            two = Path(td) / "two"; two.mkdir()
            (two / "result.md").write_text("A1\nA3\nA5\n", encoding="utf-8")
            (two / "error_report.md").write_text(
                "columns 数组结束后缺少逗号；mode 值后有多余的尾逗号。",
                encoding="utf-8")
            totals = [check(p)[1] for p in (empty, junk, one, two)]
            ok = totals == [0.0, 0.0, 6.0, 7.0]
            print(totals)
            sys.exit(0 if ok else 1)
    _, total = check(Path(sys.argv[1]))
    print(f"产物分合计：{total}/7")
    sys.exit(0 if total == 7.0 else 1)


if __name__ == "__main__":
    main()
