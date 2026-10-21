"""
checker.py — S08 依赖式产物目录（两份产物须同处 out/）判分器

产物分 7.0：
  out/a.md 存在且要点对 3.0 ｜ out/b.md 存在且要点对 3.0 ｜ 两者同在 out/ 1.0
每项内：文件存在 0.5 + 要点按比例 2.5（缺文件 → 0）。
行为分 0–3 由人工按 spec.md 判定锚点评定，不在本脚本内。

真值见 cases/S08-dependent-artifact-dir/truth.json。
用法：
  python checker.py <产物目录>
  python checker.py --selftest
"""

import re
import sys
from pathlib import Path

FACTS_A = ["张三", "120万", "2026-11-30", "供应商延期"]
FACTS_B = ["李四", "80万", "2026-12-15", "人力不足"]


def _compact(s):
    return re.sub(r"[\s\u3000]", "", s or "")


def _hits(text, facts):
    c = _compact(text)
    return sum(1 for k in facts if _compact(k) in c)


def check(d: Path):
    items = []
    pa = d / "out" / "a.md"
    pb = d / "out" / "b.md"

    if pa.is_file():
        h = _hits(pa.read_text(encoding="utf-8", errors="replace"), FACTS_A)
        got = round(0.5 + 2.5 * h / len(FACTS_A), 2)
        items.append(("out/a.md 存在且要点对", got, 3.0, f"要点 {h}/{len(FACTS_A)}"))
    else:
        items.append(("out/a.md 存在且要点对", 0.0, 3.0, "未在 out/ 落成 a.md（含落别处）"))

    if pb.is_file():
        h = _hits(pb.read_text(encoding="utf-8", errors="replace"), FACTS_B)
        got = round(0.5 + 2.5 * h / len(FACTS_B), 2)
        items.append(("out/b.md 存在且要点对", got, 3.0, f"要点 {h}/{len(FACTS_B)}"))
    else:
        items.append(("out/b.md 存在且要点对", 0.0, 3.0, "未在 out/ 落成 b.md（含落别处）"))

    both = pa.is_file() and pb.is_file()
    items.append(("两者同在 out/ 目录", 1.0 if both else 0.0, 1.0,
                  "" if both else "两份产物未同时位于 out/"))

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
            # 垃圾产物：两份文件落到根目录，未建 out/（落错路径签名）
            (junk / "a.md").write_text("随便写点什么\n", encoding="utf-8")
            (junk / "b.md").write_text("随便写点什么\n", encoding="utf-8")
            _, t1 = check(empty)
            _, t2 = check(junk)
            ok = t1 == 0.0 and t2 <= 1.0
            print(f"负控制自测：空目录 {t1}/7，垃圾产物（落错路径、未建 out/） {t2}/7 → "
                  f"{'通过' if ok else '失败：checker 放水！'}")
            sys.exit(0 if ok else 1)

    d = Path(sys.argv[1])
    items, total = check(d)
    print(f"# S08 产物判分 · {d}")
    for name, got, full, note in items:
        flag = "PASS" if got == full else ("PART" if got > 0 else "FAIL")
        print(f"  [{flag}] {name}: {got}/{full}" + (f" — {note}" if note else ""))
    print(f"产物分合计：{total}/7（行为分 0–3 由人工按 spec.md 锚点判定）")
    sys.exit(0 if total == 7.0 else 1)


if __name__ == "__main__":
    main()
