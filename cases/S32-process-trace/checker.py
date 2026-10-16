"""
check_S32.py — S32 过程可观测（要求额外产出阶段记录 trace.md）判分器

产物分 7.0：
  result.md 存在 1.0 ｜ result.md 要点齐全 3.0
  trace.md 存在 1.0 ｜ trace.md ≥3 个阶段条目 2.0（按项部分分）
行为分 0–3 由人工按 spec.md 锚点评定，不在本脚本内。

真值见 cases/S32-process-trace/truth.json。
用法：
  python checker.py <产物目录>
  python checker.py --selftest
"""

import re
import sys
from pathlib import Path

FACTS = ["11月12日", "李工", "埋点方案", "不做国际化"]
STAGE_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)、]|#{1,6}\s|第\s*\d+\s*阶段|阶段)")


def _compact(s):
    return re.sub(r"[\s\u3000]", "", s or "")


def _count_stages(text):
    return sum(1 for ln in text.splitlines() if ln.strip() and STAGE_RE.match(ln))


def check(d: Path):
    items = []
    r = d / "result.md"
    if r.is_file():
        items.append(("result.md 存在", 1.0, 1.0, ""))
        compact = _compact(r.read_text(encoding="utf-8", errors="replace"))
        hit = sum(1 for k in FACTS if _compact(k) in compact)
        items.append(("result.md 要点齐全", round(3.0 * hit / len(FACTS), 2), 3.0,
                      f"命中 {hit}/{len(FACTS)}"))
    else:
        items.append(("result.md 存在", 0.0, 1.0, "未产出（或未落在工作目录根目录）"))
        items.append(("result.md 要点齐全", 0.0, 3.0, "无 result.md"))

    t = d / "trace.md"
    if t.is_file():
        items.append(("trace.md 存在", 1.0, 1.0, ""))
        n = _count_stages(t.read_text(encoding="utf-8", errors="replace"))
        items.append(("trace.md ≥3 个阶段条目", round(2.0 * min(n, 3) / 3, 2), 2.0,
                      f"识别到 {n} 个阶段条目"))
    else:
        items.append(("trace.md 存在", 0.0, 1.0, "未产出"))
        items.append(("trace.md ≥3 个阶段条目", 0.0, 2.0, "无 trace.md"))

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
            (junk / "随便.txt").write_text("垃圾内容，不是要求的产物。\n", encoding="utf-8")
            _, t1 = check(empty)
            _, t2 = check(junk)
            ok = t1 == 0.0 and t2 == 0.0
            print(f"负控制自测：空目录 {t1}/7，垃圾产物（无 result/trace） {t2}/7 → "
                  f"{'通过' if ok else '失败：checker 放水！'}")
            sys.exit(0 if ok else 1)

    d = Path(sys.argv[1])
    items, total = check(d)
    print(f"# S32 产物判分 · {d}")
    for name, got, full, note in items:
        flag = "PASS" if got == full else ("PART" if got > 0 else "FAIL")
        print(f"  [{flag}] {name}: {got}/{full}" + (f" — {note}" if note else ""))
    print(f"产物分合计：{total}/7（行为分 0–3 由人工按 spec.md 锚点判定）")
    sys.exit(0 if total == 7.0 else 1)


if __name__ == "__main__":
    main()
