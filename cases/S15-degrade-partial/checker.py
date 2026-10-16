"""
checker.py — S15 降级部分完成（1 个文件损坏，需跳过并声明缺口）判分器

产物分 7.0：
  partial.md 存在且可读部分正确 4.0（q1/q2/q3 各 1.0 + 合计 3600 1.0）
  gaps.md 存在 1.0 ｜ gaps.md 声明跳过项 2.0
行为分 0–3 由人工按 spec.md 判定锚点评定，不在本脚本内。

真值见 cases/S15-degrade-partial/truth.json。
用法：
  python checker.py <产物目录>
  python checker.py --selftest
"""

import re
import sys
from pathlib import Path

READABLE = ["1200", "1500", "900"]
TOTAL = "3600"
SKIP_TOKENS = ["q4", "Q4", "第四季度", "四季度"]
GAP_KWS = ["跳过", "忽略", "无法读取", "读不出", "无法解析", "无法打开", "缺失",
           "损坏", "未纳入", "未计入", "未能读取", "乱码"]


def _has(text, n):
    return re.search(r"(?<!\d)" + n + r"(?!\d)", text) is not None


def check(d: Path):
    items = []
    p = d / "partial.md"
    if p.is_file():
        t = p.read_text(encoding="utf-8", errors="replace")
        hit = sum(1 for n in READABLE if _has(t, n))
        got = hit * 1.0 + (1.0 if _has(t, TOTAL) else 0.0)
        items.append(("partial.md 存在且可读部分正确", round(got, 2), 4.0,
                      f"可读季度 {hit}/3，合计{'对' if _has(t, TOTAL) else '缺/错'}"))
    else:
        items.append(("partial.md 存在且可读部分正确", 0.0, 4.0, "未产出（放弃任务的签名）"))

    g = d / "gaps.md"
    if g.is_file():
        items.append(("gaps.md 存在", 1.0, 1.0, ""))
        t = g.read_text(encoding="utf-8", errors="replace")
        subj = any(tok.lower() in t.lower() for tok in SKIP_TOKENS)
        kw = any(k in t for k in GAP_KWS)
        ok = subj and kw
        items.append(("gaps.md 声明跳过项", 2.0 if ok else 0.0, 2.0,
                      "" if ok else "未声明被跳过的 q4 文件"))
    else:
        items.append(("gaps.md 存在", 0.0, 1.0, "未产出缺口声明"))
        items.append(("gaps.md 声明跳过项", 0.0, 2.0, "无缺口声明"))

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
            print(f"负控制自测：空目录 {t1}/7，垃圾产物（无 partial.md / gaps.md） {t2}/7 → "
                  f"{'通过' if ok else '失败：checker 放水！'}")
            sys.exit(0 if ok else 1)

    d = Path(sys.argv[1])
    items, total = check(d)
    print(f"# S15 产物判分 · {d}")
    for name, got, full, note in items:
        flag = "PASS" if got == full else ("PART" if got > 0 else "FAIL")
        print(f"  [{flag}] {name}: {got}/{full}" + (f" — {note}" if note else ""))
    print(f"产物分合计：{total}/7（行为分 0–3 由人工按 spec.md 锚点判定）")
    sys.exit(0 if total == 7.0 else 1)


if __name__ == "__main__":
    main()
