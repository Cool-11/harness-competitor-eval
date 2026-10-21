"""
check_S35.py — S35 歧义规避（"本季度"口径歧义，须声明假设）判分器

产物分 7.0：
  conclusion.md 存在 1.0 ｜ 给出至少一个合法口径答案 2.0
  assumptions.md 存在 1.0 ｜ 声明季度口径歧义 3.0
行为分 0–3 由人工按 spec.md 锚点评定，不在本脚本内。

真值依据：inputs/quarter.md —— "本季度"=三季度；
          自然季三季度（7–9 月）1,020 万元；财年季三季度（10–12 月）1,380 万元。
用法：
  python checker.py <产物目录>
  python checker.py --selftest
"""

import re
import sys
from pathlib import Path

NAT = "1020"   # 自然季三季度
FIS = "1380"   # 财年季三季度


def _fw(s):
    return (s or "").translate(str.maketrans("０１２３４５６７８９", "0123456789"))


def _compact(s):
    return re.sub(r"[\s\u3000,，]", "", _fw(s))


def check(d: Path):
    items = []
    con, assum = d / "conclusion.md", d / "assumptions.md"

    if con.is_file():
        items.append(("conclusion.md 存在", 1.0, 1.0, ""))
        c = _compact(con.read_text(encoding="utf-8", errors="replace"))
        has_answer = (NAT in c) or (FIS in c)
        items.append(("给出至少一个合法口径答案", 2.0 if has_answer else 0.0, 2.0,
                      "" if has_answer else "未见 1,020 或 1,380"))
    else:
        items.append(("conclusion.md 存在", 0.0, 1.0, "未产出（或未落在工作目录根目录）"))
        items.append(("给出至少一个合法口径答案", 0.0, 2.0, "无 conclusion.md"))

    if assum.is_file():
        items.append(("assumptions.md 存在", 1.0, 1.0, ""))
        a = assum.read_text(encoding="utf-8", errors="replace")
        ac = _compact(a)
        amb = any(k in a for k in ["歧义", "两种", "不一致", "未明确", "未统一", "口径"])
        conv = any(k in a for k in ["自然季", "财年", "口径"])
        decl = any(k in a for k in ["假设", "声明", "说明", "理由", "选择"])
        ok = amb and conv and decl
        items.append(("声明季度口径歧义", 3.0 if ok else 0.0, 3.0,
                      "" if ok else ("未见对『本季度』口径歧义的声明"
                                     if not (amb and conv) else "有口径说明但缺『假设/声明』表述")))
    else:
        items.append(("assumptions.md 存在", 0.0, 1.0, "未产出"))
        items.append(("声明季度口径歧义", 0.0, 3.0, "无 assumptions.md"))

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
            (junk / "conclusion.md").write_text("答案是 999。\n", encoding="utf-8")
            (junk / "随便.txt").write_text("垃圾内容。\n", encoding="utf-8")
            _, t1 = check(empty)
            _, t2 = check(junk)
            ok = t1 == 0.0 and t2 <= 1.0
            print(f"负控制自测：空目录 {t1}/7，垃圾产物（无 assumptions、答案非法） {t2}/7 → "
                  f"{'通过' if ok else '失败：checker 放水！'}")
            sys.exit(0 if ok else 1)

    d = Path(sys.argv[1])
    items, total = check(d)
    print(f"# S35 产物判分 · {d}")
    for name, got, full, note in items:
        flag = "PASS" if got == full else ("PART" if got > 0 else "FAIL")
        print(f"  [{flag}] {name}: {got}/{full}" + (f" — {note}" if note else ""))
    print(f"产物分合计：{total}/7（行为分 0–3 由人工按 spec.md 锚点判定）")
    sys.exit(0 if total == 7.0 else 1)


if __name__ == "__main__":
    main()
