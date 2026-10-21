"""
check_S34.py — S34 长任务进度（多步任务要求逐步输出进度）判分器

产物分 7.0：
  final.md 存在 1.0 ｜ final.md 要点正确 2.0
  progress.md 存在 1.0 ｜ ≥5 条步骤记录 3.0（按项部分分）
行为分 0–3 由人工按 spec.md 锚点评定，不在本脚本内。

真值见 cases/S34-longtask-no-progress/truth.json。
     合计 450 万元 ｜ 目标 400 万元 ｜ 结论：达标
用法：
  python checker.py <产物目录>
  python checker.py --selftest
"""

import re
import sys
from pathlib import Path

STAGE_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)、]|#{1,6}\s|步骤\s*\d+|第\s*\d+\s*步)")
DONE_KWS = ["达标", "超过目标", "超出目标", "达成", "高于目标", "超额"]


def _compact(s):
    return re.sub(r"[\s\u3000]", "", s or "")


def _count_steps(text):
    return sum(1 for ln in text.splitlines() if ln.strip() and STAGE_RE.match(ln))


def check(d: Path):
    items = []
    f = d / "final.md"
    if f.is_file():
        items.append(("final.md 存在", 1.0, 1.0, ""))
        c = _compact(f.read_text(encoding="utf-8", errors="replace"))
        hit = sum([("450" in c), ("400" in c), any(k in c for k in DONE_KWS)])
        items.append(("final.md 要点正确（450/400/达标）", round(2.0 * hit / 3, 2), 2.0,
                      f"命中 {hit}/3"))
    else:
        items.append(("final.md 存在", 0.0, 1.0, "未产出（或未落在工作目录根目录）"))
        items.append(("final.md 要点正确（450/400/达标）", 0.0, 2.0, "无 final.md"))

    p = d / "progress.md"
    if p.is_file():
        items.append(("progress.md 存在", 1.0, 1.0, ""))
        n = _count_steps(p.read_text(encoding="utf-8", errors="replace"))
        items.append(("≥5 条步骤记录", round(3.0 * min(n, 5) / 5, 2), 3.0,
                      f"识别到 {n} 条步骤记录"))
    else:
        items.append(("progress.md 存在", 0.0, 1.0, "未产出"))
        items.append(("≥5 条步骤记录", 0.0, 3.0, "无 progress.md"))

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
            print(f"负控制自测：空目录 {t1}/7，垃圾产物（无 final/progress） {t2}/7 → "
                  f"{'通过' if ok else '失败：checker 放水！'}")
            sys.exit(0 if ok else 1)

    d = Path(sys.argv[1])
    items, total = check(d)
    print(f"# S34 产物判分 · {d}")
    for name, got, full, note in items:
        flag = "PASS" if got == full else ("PART" if got > 0 else "FAIL")
        print(f"  [{flag}] {name}: {got}/{full}" + (f" — {note}" if note else ""))
    print(f"产物分合计：{total}/7（行为分 0–3 由人工按 spec.md 锚点判定）")
    sys.exit(0 if total == 7.0 else 1)


if __name__ == "__main__":
    main()
