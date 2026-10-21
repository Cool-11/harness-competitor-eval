"""
check_S10.py — S10 只落盘还是贴给我（产物落点）判分器

产物分 7.0：
  deliverable.md 存在（根目录） 3.0 ｜ 5 条要点关键词全部命中 3.0（按条部分分）
  形式为要点列表（≥5 行以 -/*/数字 开头） 1.0
行为分 0–3 由人工按 spec.md 判定锚点评定，不在本脚本内。

真值见 cases/S10-chat-only-temptation/truth.json。
用法：
  python check_S10.py <产物目录>
  python check_S10.py --selftest
"""

import re
import sys
from pathlib import Path

REL = "deliverable.md"
FACTS = ["灰度放量至 20%", "登录页新增埋点覆盖", "供应商 B 报价下调 5%",
         "测试环境迁移到新集群", "下周三完成回归测试"]
FULL = 7.0


def _compact(s):
    return re.sub(r"[\s\u3000]", "", s or "")


def _is_bullet(ln):
    return bool(re.match(r"^([-*+]|\d+[.、)])\s+\S", ln))


def check(d: Path):
    f = d / REL
    if not f.is_file():
        return [("deliverable.md 存在（工作目录根目录）", 0.0, 3.0,
                 "未在根目录落成 deliverable.md（含只在会话内输出）")], 0.0

    items = [("deliverable.md 存在（工作目录根目录）", 3.0, 3.0, "")]
    text = f.read_text(encoding="utf-8", errors="replace")

    comp = _compact(text)
    hit = sum(1 for k in FACTS if _compact(k) in comp)
    items.append(("5 条要点关键词全部命中", round(3.0 * hit / 5, 2), 3.0, f"命中 {hit}/5"))

    lines = [ln.strip() for ln in text.replace("\r\n", "\n").split("\n")]
    bullet = sum(1 for ln in lines if _is_bullet(ln))
    ok = bullet >= 5
    items.append(("形式为要点列表（≥5 行以 -/*/数字 开头）", 1.0 if ok else 0.0, 1.0,
                  f"要点行 {bullet}"))

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
            (junk / "notes.txt").write_text("随便写点\n", encoding="utf-8")
            _, t1 = check(empty)
            _, t2 = check(junk)
            ok = t1 == 0.0 and t2 == 0.0
            print(f"负控制自测：空目录 {t1}/7，垃圾产物（未产出 deliverable.md） {t2}/7 → "
                  f"{'通过' if ok else '失败：checker 放水！'}")
            sys.exit(0 if ok else 1)

    d = Path(sys.argv[1])
    items, total = check(d)
    print(f"# S10 产物判分 · {d}")
    for name, got, full, note in items:
        flag = "PASS" if got == full else ("PART" if got > 0 else "FAIL")
        print(f"  [{flag}] {name}: {got}/{full}" + (f" — {note}" if note else ""))
    print(f"产物分合计：{total}/7（行为分 0–3 由人工按 spec.md 锚点判定）")
    sys.exit(0 if total == FULL else 1)


if __name__ == "__main__":
    main()
