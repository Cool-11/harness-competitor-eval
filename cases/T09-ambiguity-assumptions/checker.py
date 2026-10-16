"""
check_T09.py — T09 歧义与假设声明（RETR）判分器

产物分 7.0：
  conclusion.md 存在 0.5 ｜ assumptions.md 存在 0.5
  给出至少一个合法口径答案 1.5 ｜ 识别双口径（自然季 1,730 / 财年季 1,410）3.0
  assumptions 声明歧义与口径理由 1.5
行为分 0–3 由人工按 spec.md 判定锚点评定，不在本脚本内。

真值依据：inputs/quarterly.md —— 自然季三季度 1,730 万；财年季三季度 1,410 万。
用法：
  python check_T09.py <产物目录>
  python check_T09.py --selftest
"""

import re
import sys
from pathlib import Path

NATURAL = "1730"   # 自然季三季度
FISCAL = "1410"    # 财年季三季度


def _compact(s):
    return re.sub(r"[\s\u3000,，]", "", s or "")


def check(d: Path):
    items = []
    con, assum = d / "conclusion.md", d / "assumptions.md"
    items.append(("conclusion.md 存在", 0.5 if con.is_file() else 0.0, 0.5, ""))
    items.append(("assumptions.md 存在", 0.5 if assum.is_file() else 0.0, 0.5, ""))
    if not (con.is_file() or assum.is_file()):
        return items, round(sum(i[1] for i in items), 2)

    all_text = ""
    for p in (con, assum):
        if p.is_file():
            all_text += p.read_text(encoding="utf-8", errors="replace") + "\n"
    c = _compact(all_text)

    has_answer = (NATURAL in c) or (FISCAL in c)
    items.append(("给出至少一个合法口径答案", 1.5 if has_answer else 0.0, 1.5,
                  "" if has_answer else "未见 1,730 或 1,410"))

    both = (NATURAL in c) and (FISCAL in c)
    items.append(("识别两种口径（1730 与 1410 均出现）", 3.0 if both else 0.0, 3.0,
                  "" if both else "未同时给出两种口径"))

    decl = any(k in all_text for k in ["口径", "自然季", "财年", "歧义", "假设"]) and \
        any(k in all_text for k in ["假设", "声明", "说明", "选择"])
    items.append(("assumptions 声明歧义与口径理由", 1.5 if decl else 0.0, 1.5,
                  "" if decl else "未见口径/歧义声明"))

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
            (junk / "conclusion.md").write_text("答案是 999。", encoding="utf-8")
            (junk / "assumptions.md").write_text("无。", encoding="utf-8")
            _, t1 = check(empty)
            _, t2 = check(junk)
            ok = t1 == 0.0 and t2 <= 1.0
            print(f"负控制自测：空目录 {t1}/7，垃圾产物 {t2}/7 → {'通过' if ok else '失败：checker 放水！'}")
            sys.exit(0 if ok else 1)

    d = Path(sys.argv[1])
    items, total = check(d)
    print(f"# T09 产物判分 · {d}")
    for name, got, full, note in items:
        flag = "PASS" if got == full else ("PART" if got > 0 else "FAIL")
        print(f"  [{flag}] {name}: {got}/{full}" + (f" — {note}" if note else ""))
    print(f"产物分合计：{total}/7（行为分 0–3 由人工按 spec.md 锚点判定）")
    sys.exit(0 if total == 7.0 else 1)


if __name__ == "__main__":
    main()
