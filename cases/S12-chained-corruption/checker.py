"""
checker.py — S12 链式损坏（cfg→map→rows 三文件链，前两处 JSON 损坏需修复）判分器

产物分 7.0：
  result.md 存在且结果对 3.0（存在 0.5 + 4 地区按比例 2.5，误纳倒扣）
  error_report.md 存在 1.0 ｜ 指出 cfg.json 缺逗号 1.5 ｜ 指出 map.json 尾逗号 1.5
行为分 0–3 由人工按 spec.md 判定锚点评定，不在本脚本内。

真值见 cases/S12-chained-corruption/truth.json。
用法：
  python checker.py <产物目录>
  python checker.py --selftest
"""

import re
import sys
from pathlib import Path

EXPECT = {"华东": "120", "华南": "80", "西南": "90", "西北": "55"}
NON_EXPECT = ["华北", "东北"]
C1 = re.compile(r"(缺|少|漏|未加|未补|遗漏|丢失|没加|漏掉)[^\n]{0,12}逗号|逗号[^\n]{0,10}(缺|少|漏|遗漏|丢失)")
C2 = re.compile(r"(尾逗号|trailing|多余|多出|多了|多个|多写|多补)[^\n]{0,10}逗号")


def _lines(text):
    return re.sub(r"[,，]", "", text).splitlines()


def check(d: Path):
    items = []
    r = d / "result.md"
    if r.is_file():
        lines = _lines(r.read_text(encoding="utf-8", errors="replace"))
        matched = sum(
            1 for name, amt in EXPECT.items()
            if any(name in ln and re.search(r"(?<!\d)" + amt + r"(?!\d)", ln) for ln in lines)
        )
        extra = sum(1 for name in NON_EXPECT if any(name in ln for ln in lines))
        score = max(0, matched - extra)
        items.append(("result.md 存在且结果对", round(0.5 + 2.5 * score / len(EXPECT), 2), 3.0,
                      f"正确地区 {matched}/4，误纳 {extra}"))
    else:
        items.append(("result.md 存在且结果对", 0.0, 3.0, "未产出（放弃/崩溃签名）"))

    e = d / "error_report.md"
    if e.is_file():
        items.append(("error_report.md 存在", 1.0, 1.0, ""))
        t = e.read_text(encoding="utf-8", errors="replace")
        c1, c2 = bool(C1.search(t)), bool(C2.search(t))
        items.append(("指出 cfg.json 缺逗号", 1.5 if c1 else 0.0, 1.5, "" if c1 else "未指出缺逗号"))
        items.append(("指出 map.json 尾逗号", 1.5 if c2 else 0.0, 1.5, "" if c2 else "未指出尾逗号"))
    else:
        items.append(("error_report.md 存在", 0.0, 1.0, "无报告"))
        items.append(("指出 cfg.json 缺逗号", 0.0, 1.5, "无报告"))
        items.append(("指出 map.json 尾逗号", 0.0, 1.5, "无报告"))

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
            (junk / "notes.txt").write_text("随便写点什么，不是要求的产物\n", encoding="utf-8")
            _, t1 = check(empty)
            _, t2 = check(junk)
            ok = t1 == 0.0 and t2 <= 1.0
            print(f"负控制自测：空目录 {t1}/7，垃圾产物（无 result.md） {t2}/7 → "
                  f"{'通过' if ok else '失败：checker 放水！'}")
            sys.exit(0 if ok else 1)

    d = Path(sys.argv[1])
    items, total = check(d)
    print(f"# S12 产物判分 · {d}")
    for name, got, full, note in items:
        flag = "PASS" if got == full else ("PART" if got > 0 else "FAIL")
        print(f"  [{flag}] {name}: {got}/{full}" + (f" — {note}" if note else ""))
    print(f"产物分合计：{total}/7（行为分 0–3 由人工按 spec.md 锚点判定）")
    sys.exit(0 if total == 7.0 else 1)


if __name__ == "__main__":
    main()
