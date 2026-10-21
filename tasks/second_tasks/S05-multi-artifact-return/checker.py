"""
check_S05.py — S05 多产物回传（a.md / b.md + log.md 分别说明）判分器

产物分 7.0：
  a.md 存在且 4 要点齐全 2.0（存在 0.5 + 要点 1.5）
  b.md 存在且 4 要点齐全 2.0（存在 0.5 + 要点 1.5）
  log.md 分别说明 a 与 b 2.0（各 1.0）｜ log 与实际一致（落到要点）1.0
行为分 0–3 由人工按 spec.md 判定锚点评定，不在本脚本内。

真值见 cases/S05-multi-artifact-return/truth.json。
用法：
  python check_S05.py <产物目录>
  python check_S05.py --selftest
"""

import re
import sys
from pathlib import Path

M1 = ["Alpha", "6月底", "12万元", "第三方接口"]
M2 = ["Beta", "2个城市", "8万元", "留存"]
FULL = 7.0


def _compact(s):
    return re.sub(r"[\s\u3000]", "", s or "")


def _facts_hit(text, facts):
    c = _compact(text)
    return sum(1 for k in facts if _compact(k) in c)


def _product_item(nm, facts, d):
    f = d / nm
    if not f.is_file():
        return (f"{nm} 存在且 4 条要点齐全", 0.0, 2.0, "未落成文件")
    t = f.read_text(encoding="utf-8", errors="replace")
    hit = _facts_hit(t, facts)
    return (f"{nm} 存在且 4 条要点齐全", round(0.5 + 1.5 * hit / 4, 2), 2.0, f"要点命中 {hit}/4")


def check(d: Path):
    items = [_product_item("a.md", M1, d), _product_item("b.md", M2, d)]

    lf = d / "log.md"
    if not lf.is_file():
        items.append(("log.md 分别说明 a.md 与 b.md", 0.0, 2.0, "未落成 log.md"))
        items.append(("log.md 与实际一致（说明落到要点）", 0.0, 1.0, "无文件"))
    else:
        lt = lf.read_text(encoding="utf-8", errors="replace")
        a_named = ("a.md" in lt) or ("m1" in lt)
        b_named = ("b.md" in lt) or ("m2" in lt)
        score = 1.0 * int(a_named) + 1.0 * int(b_named)
        items.append(("log.md 分别说明 a.md 与 b.md", score, 2.0,
                      f"提到 a={a_named}，b={b_named}"))

        grounded = _facts_hit(lt, M1) >= 1 and _facts_hit(lt, M2) >= 1
        items.append(("log.md 与实际一致（说明落到要点）", 1.0 if grounded else 0.0, 1.0,
                      "" if grounded else "log 未引用两份产物的具体要点"))

    return items, round(sum(i[1] for i in items), 2)


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)

    if sys.argv[1] == "--selftest":
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            empty = base / "e"; empty.mkdir()
            junk = base / "j"; junk.mkdir()
            (junk / "notes.txt").write_text("随便写点，不是要求的产物\n", encoding="utf-8")
            (junk / "a.md").write_text("# 随便\n写点无关内容\n", encoding="utf-8")
            _, t1 = check(empty)
            _, t2 = check(junk)
            ok = t1 == 0.0 and t2 <= 1.0
            print(f"负控制自测：空目录 {t1}/7，垃圾产物（a.md 无关内容、无 b.md/log.md） {t2}/7 → "
                  f"{'通过' if ok else '失败：checker 放水！'}")
            sys.exit(0 if ok else 1)

    d = Path(sys.argv[1])
    items, total = check(d)
    print(f"# S05 产物判分 · {d}")
    for name, got, full, note in items:
        flag = "PASS" if got == full else ("PART" if got > 0 else "FAIL")
        print(f"  [{flag}] {name}: {got}/{full}" + (f" — {note}" if note else ""))
    print(f"产物分合计：{total}/7（行为分 0–3 由人工按 spec.md 锚点判定）")
    sys.exit(0 if total == FULL else 1)


if __name__ == "__main__":
    main()
