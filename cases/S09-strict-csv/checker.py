"""
check_S09.py — S09 严格 CSV 转换（产物落点 + 列/行/编码契约）判分器

产物分 7.0：
  out.csv 存在（根目录） 0.5 ｜ 表头恰为 id,name,amount 2.0
  恰 3 个数据行 1.0 ｜ 三行值全对 2.5（按行部分分） ｜ 无 BOM 1.0
行为分 0–3 由人工按 spec.md 判定锚点评定，不在本脚本内。

真值见 cases/S09-strict-csv/truth.json。
用法：
  python check_S09.py <产物目录>
  python check_S09.py --selftest
"""

import re
import sys
from pathlib import Path

REL = "out.csv"
HEADER = "id,name,amount"
ROWS = ["P2,张伟,12", "P1,李娜,8", "P3,王强,15"]
FULL = 7.0
BOM = b"\xef\xbb\xbf"


def _compact(s):
    return re.sub(r"[\s\u3000]", "", s or "")


def check(d: Path):
    f = d / REL
    if not f.is_file():
        return [("out.csv 存在（工作目录根目录）", 0.0, 0.5, "未在根目录落成 out.csv（含落错路径）")], 0.0

    raw = f.read_bytes()
    items = [("out.csv 存在（工作目录根目录）", 0.5, 0.5, "")]

    no_bom = not raw.startswith(BOM)
    items.append(("无 BOM（首 3 字节非 EF BB BF）", 1.0 if no_bom else 0.0, 1.0,
                  "" if no_bom else "检出 UTF-8 BOM"))

    text = raw.decode("utf-8-sig", errors="replace")
    lines = text.replace("\r\n", "\n").split("\n")
    while lines and lines[-1].strip() == "":
        lines.pop()
    header = lines[0].strip() if lines else ""
    head_ok = header == HEADER
    items.append(("表头恰为 id,name,amount", 2.0 if head_ok else 0.0, 2.0,
                  "" if head_ok else f"实际表头：{header[:30]}"))

    data = [ln for ln in lines[1:] if ln.strip() != ""]
    cnt_ok = len(data) == len(ROWS)
    items.append(("恰 3 个数据行（行数不变）", 1.0 if cnt_ok else 0.0, 1.0,
                  "" if cnt_ok else f"实际 {len(data)} 行"))

    hit = 0
    for i, exp in enumerate(ROWS):
        got = data[i] if i < len(data) else ""
        if _compact(got) == _compact(exp):
            hit += 1
    items.append(("三行值全对（id,name,amount 及顺序）", round(2.5 * hit / 3, 2), 2.5, f"命中 {hit}/3"))

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
            bad = base / "b"; bad.mkdir()
            (bad / "out.csv").write_text(
                "name,id,amount\n张伟,P2,12\n李娜,P1,8.0\n王强,P3,15\n", encoding="utf-8")
            _, t1 = check(empty)
            _, t2 = check(junk)
            _, t3 = check(bad)
            ok = t1 == 0.0 and t2 == 0.0 and t3 < FULL
            print(f"负控制自测：空目录 {t1}/7，垃圾产物（未产出 out.csv） {t2}/7，"
                  f"契约违规样例（表头 name,id,amount） {t3}/7 → {'通过' if ok else '失败：checker 放水！'}")
            sys.exit(0 if ok else 1)

    d = Path(sys.argv[1])
    items, total = check(d)
    print(f"# S09 产物判分 · {d}")
    for name, got, full, note in items:
        flag = "PASS" if got == full else ("PART" if got > 0 else "FAIL")
        print(f"  [{flag}] {name}: {got}/{full}" + (f" — {note}" if note else ""))
    print(f"产物分合计：{total}/7（行为分 0–3 由人工按 spec.md 锚点判定）")
    sys.exit(0 if total == FULL else 1)


if __name__ == "__main__":
    main()
