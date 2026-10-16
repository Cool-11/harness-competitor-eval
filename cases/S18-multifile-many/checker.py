"""
checker.py — S18 多文件海量汇总（30 个小文件，求和需无遗漏）判分器

产物分 7.0：
  cross_ref.md 存在 1.0 ｜ 总计金额正确 5.0 ｜ 无漏计（项数=30）1.0（按项数部分分）
行为分 0–3 由人工按 spec.md 判定锚点评定，不在本脚本内。

真值见 cases/S18-multifile-many/truth.json。
用法：
  python checker.py <产物目录>
  python checker.py --selftest
"""

import re
import sys
from pathlib import Path

AMOUNTS = list(range(101, 131))   # item-01..item-30 的金额 101..130
TOTAL = 3465


def check(d: Path):
    items = []
    f = d / "cross_ref.md"
    if not f.is_file():
        items.append(("cross_ref.md 存在", 0.0, 1.0, "未落成文件（含落错路径）"))
        items.append(("总计金额正确", 0.0, 5.0, "无产物"))
        items.append(("无漏计（项数=30）", 0.0, 1.0, "无产物"))
        return items, 0.0
    items.append(("cross_ref.md 存在", 1.0, 1.0, ""))

    text = f.read_text(encoding="utf-8", errors="replace")
    nocomma = text.replace(",", "").replace("，", "")

    total_ok = re.search(r"(?<!\d)" + str(TOTAL) + r"(?!\d)", nocomma) is not None
    items.append(("总计金额正确", 5.0 if total_ok else 0.0, 5.0,
                  "" if total_ok else f"未出现正确总计 {TOTAL}"))

    hit = sum(1 for a in AMOUNTS if re.search(r"(?<!\d)" + str(a) + r"(?!\d)", text))
    items.append(("无漏计（项数=30）", round(1.0 * hit / len(AMOUNTS), 2), 1.0,
                  f"命中金额项 {hit}/30"))

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
            (junk / "cross_ref.md").write_text("## 汇总\n总计 999999 元\n", encoding="utf-8")
            _, t1 = check(empty)
            _, t2 = check(junk)
            ok = t1 == 0.0 and t2 <= 1.0
            print(f"负控制自测：空目录 {t1}/7，垃圾产物（错总计） {t2}/7 → "
                  f"{'通过' if ok else '失败：checker 放水！'}")
            sys.exit(0 if ok else 1)

    d = Path(sys.argv[1])
    items, total = check(d)
    print(f"# S18 产物判分 · {d}")
    for name, got, full, note in items:
        flag = "PASS" if got == full else ("PART" if got > 0 else "FAIL")
        print(f"  [{flag}] {name}: {got}/{full}" + (f" — {note}" if note else ""))
    print(f"产物分合计：{total}/7（行为分 0–3 由人工按 spec.md 锚点判定）")
    sys.exit(0 if total == 7.0 else 1)


if __name__ == "__main__":
    main()
