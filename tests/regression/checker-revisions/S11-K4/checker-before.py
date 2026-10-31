"""S11 checker · K4 修复前快照。只作证据，不作为生产 checker 调用。"""

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
            print(f"负控制自测：空目录 {t1}/7，垃圾产物（无 result.md） {t2}/7 → {'通过' if ok else '失败'}")
            sys.exit(0 if ok else 1)
    _, total = check(Path(sys.argv[1]))
    print(f"产物分合计：{total}/7")
    sys.exit(0 if total == 7.0 else 1)


if __name__ == "__main__":
    main()
