"""
checker.py — S20 早期约束丢失（全局约束保持）判分器

产物分 7.0：
  final.md 存在（工作目录根目录） 1.0 ｜ 3 条要点齐全 3.0（按条部分分）
  全文无大写字母（不含 A–Z） 2.0 ｜ 正文非空白字符数 ≤120 1.0
「正文」= 去掉 Markdown 标题行（以 # 开头的行）后的文本。
行为分 0–3 由人工按 spec.md 判定锚点评定，不在本脚本内。

真值见 cases/S20-early-constraint-loss/truth.json。
用法：
  python checker.py <产物目录>
  python checker.py --selftest
"""

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _compact(s):
    return re.sub(r"[\s\u3000]", "", s or "")


def _body(text):
    lines = [ln for ln in text.splitlines() if not ln.lstrip().startswith("#")]
    return "\n".join(lines)


def check(d: Path):
    truth = json.loads((HERE / "truth.json").read_text(encoding="utf-8"))
    pats = truth["要点匹配正则"]

    items = []
    f = d / "final.md"
    if not f.is_file():
        return [("final.md 存在（工作目录根目录）", 0.0, 1.0,
                 "未在根目录落成 final.md（含落错路径）")], 0.0
    items.append(("final.md 存在（工作目录根目录）", 1.0, 1.0, ""))

    text = f.read_text(encoding="utf-8", errors="replace")

    hit = sum(1 for p in pats if re.search(p, text))
    items.append(("3 条要点齐全", round(3.0 * hit / len(pats), 2), 3.0, f"命中 {hit}/{len(pats)}"))

    no_upper = re.search(r"[A-Z]", text) is None
    items.append(("全文无大写字母（不含 A–Z）", 2.0 if no_upper else 0.0, 2.0,
                  "" if no_upper else "检出大写字母"))

    n = len(_compact(_body(text)))
    len_ok = n <= 120
    items.append(("正文非空白字符数 ≤120", 1.0 if len_ok else 0.0, 1.0,
                  "" if len_ok else f"实际 {n} 字"))

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
            (junk / "final.md").write_text(
                "# Report\n" + "THIS IS AN UNRELATED ENGLISH PARAGRAPH. " * 6 + "\n",
                encoding="utf-8")
            _, t1 = check(empty)
            _, t2 = check(junk)
            ok = t1 == 0.0 and t2 <= 1.0
            print(f"负控制自测：空目录 {t1}/7，垃圾产物（超字数且含大写） {t2}/7 → "
                  f"{'通过' if ok else '失败：checker 放水！'}")
            sys.exit(0 if ok else 1)

    d = Path(sys.argv[1])
    items, total = check(d)
    print(f"# S20 产物判分 · {d}")
    for name, got, full, note in items:
        flag = "PASS" if got == full else ("PART" if got > 0 else "FAIL")
        print(f"  [{flag}] {name}: {got}/{full}" + (f" — {note}" if note else ""))
    print(f"产物分合计：{total}/7（行为分 0–3 由人工按 spec.md 锚点判定）")
    sys.exit(0 if total == 7.0 else 1)


if __name__ == "__main__":
    main()
