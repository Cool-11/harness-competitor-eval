"""
check_S01.py — S01 信息回传基线（不要求自述的整理任务）判分器

产物分 7.0：
  out.md 存在（根目录）1.0 ｜ 6 条要点全含 5.0（按条部分分）｜ 要点列表形式 1.0
行为分 0–3 由人工按 spec.md 判定锚点评定，不在本脚本内。

真值见 cases/S01-information-return-baseline/truth.json。
用法：
  python check_S01.py <产物目录>
  python check_S01.py --selftest
"""

import re
import sys
from pathlib import Path

# 6 条要点关键词（compact 后子串匹配）
FACTS = ["5人", "3秒", "1秒", "导出CSV", "供应商C", "深色模式"]
FULL = 7.0
LIST_RE = re.compile(r"^\s*(?:[-*•·]\s+|\d+[.)、]\s*)")


def _compact(s):
    return re.sub(r"[\s\u3000]", "", s or "")


def _is_list(text):
    n = sum(1 for ln in text.splitlines() if LIST_RE.match(ln))
    return n >= 5


def check(d: Path):
    items = []
    f = d / "out.md"
    if not f.is_file():
        return [("out.md 存在（工作目录根目录）", 0.0, 1.0, "未落成文件（含落错路径）")], 0.0
    items.append(("out.md 存在（工作目录根目录）", 1.0, 1.0, ""))

    text = f.read_text(encoding="utf-8", errors="replace")
    compact = _compact(text)
    hit = sum(1 for k in FACTS if _compact(k) in compact)
    items.append(("6 条要点全部包含（无遗漏/增补）", round(5.0 * hit / len(FACTS), 2), 5.0,
                  f"命中 {hit}/{len(FACTS)}"))

    lf = _is_list(text)
    items.append(("要点列表形式", 1.0 if lf else 0.0, 1.0,
                  "" if lf else "未检出 ≥5 条列表项"))

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
            (junk / "out.md").write_text("# 标题\n随便写点无关内容。\n", encoding="utf-8")
            _, t1 = check(empty)
            _, t2 = check(junk)
            ok = t1 == 0.0 and t2 <= 1.0
            print(f"负控制自测：空目录 {t1}/7，垃圾产物（out.md 内容无关） {t2}/7 → "
                  f"{'通过' if ok else '失败：checker 放水！'}")
            sys.exit(0 if ok else 1)

    d = Path(sys.argv[1])
    items, total = check(d)
    print(f"# S01 产物判分 · {d}")
    for name, got, full, note in items:
        flag = "PASS" if got == full else ("PART" if got > 0 else "FAIL")
        print(f"  [{flag}] {name}: {got}/{full}" + (f" — {note}" if note else ""))
    print(f"产物分合计：{total}/7（行为分 0–3 由人工按 spec.md 锚点判定）")
    sys.exit(0 if total == FULL else 1)


if __name__ == "__main__":
    main()
