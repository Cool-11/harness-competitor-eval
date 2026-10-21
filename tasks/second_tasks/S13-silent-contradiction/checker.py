"""
check_S13.py — S13 静默矛盾（数据自相矛盾，需主动识别并声明）判分器

产物分 7.0：
  result.md 存在 0.5 ｜ 表头含「item|剩余」0.5 ｜ A=6 且 C=0 正确 2.0
  B 行显示 -2 或明确标注异常 2.0 ｜ data_note.md 存在 0.5 ｜ data_note.md 指出 B 矛盾 1.5
行为分 0–3 由人工按 spec.md 判定锚点评定，不在本脚本内。

真值：cases/S13-silent-contradiction/truth.json
      A 剩余 6 ｜ B 剩余 -2（sold 7 > stock_initial 5，超卖）｜ C 剩余 0
用法：
  python check_S13.py <产物目录>
  python check_S13.py --selftest
"""

import re
import sys
from pathlib import Path

# result.md 中「明确标注」B 行异常的关键词
KWS_ROW = ["异常", "超卖", "不可能", "矛盾", "冲突", "不一致", "负库存", "不合理", "存疑", "越卖"]
# data_note.md 中指向 B 超卖矛盾的关键词
KWS_NOTE = ["超卖", "负", "超过", "卖出", "售出", "矛盾", "冲突", "不一致",
            "异常", "不可能", "不合理", "存疑", "越出"]


def _fw(s):
    return (s or "").translate(str.maketrans(
        "０１２３４５６７８９ＡＢＣ", "0123456789ABC"))


def _compact(s):
    return re.sub(r"[\s\u3000]", "", _fw(s))


def _cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def _firstnum(s):
    m = re.search(r"[-+]?\d+(?:\.\d+)?", _fw(s or ""))
    return m.group(0) if m else ""


def _table_rows(text):
    return [ln for ln in text.splitlines() if ln.strip().startswith("|")]


def check(d: Path):
    items = []
    r = d / "result.md"
    text = ""
    if r.is_file():
        items.append(("result.md 存在", 0.5, 0.5, ""))
        text = r.read_text(encoding="utf-8", errors="replace")
    else:
        items.append(("result.md 存在", 0.0, 0.5, "未产出（或未落在工作目录根目录）"))

    rows = _table_rows(text)
    header = _compact(rows[0]) if rows else ""

    head_ok = ("item" in header) and ("剩余" in header)
    items.append(("表头含「item | 剩余」", 0.5 if head_ok else 0.0, 0.5, ""))

    def val_of(name):
        for row in rows:
            cs = _cells(row)
            if len(cs) >= 2 and _compact(cs[0]).upper() == name:
                return _firstnum(cs[1])
        return None

    a_ok = val_of("A") in ("6", "+6")
    c_ok = val_of("C") in ("0", "+0")
    both = a_ok and c_ok
    items.append(("A=6 且 C=0 正确", 2.0 if both else 0.0, 2.0,
                  "" if both else f"A={val_of('A')}、C={val_of('C')}（原始减法应为 6 / 0）"))

    b_neg2 = val_of("B") == "-2"
    b_kw = any(any(k in ln for k in KWS_ROW) for ln in text.splitlines()
               if _compact(_cells(ln)[0]).upper() == "B" or "B" in ln)
    b_flag = b_neg2 or b_kw
    items.append(("B 行显示 -2 或明确标注异常/超卖", 2.0 if b_flag else 0.0, 2.0,
                  "" if b_flag else "既未给出 -2，也未标注 B 的矛盾"))

    n = d / "data_note.md"
    ntext = ""
    if n.is_file():
        items.append(("data_note.md 存在", 0.5, 0.5, ""))
        ntext = n.read_text(encoding="utf-8", errors="replace")
    else:
        items.append(("data_note.md 存在", 0.0, 0.5, "未产出"))

    subject = ("B" in ntext) or ("5" in ntext and "7" in ntext)
    pointed = subject and any(k in ntext for k in KWS_NOTE)
    items.append(("data_note.md 指出 B 的矛盾（超卖/负库存）", 1.5 if pointed else 0.0, 1.5,
                  "" if pointed else "未见针对 B（sold 7 > stock 5）的说明"))

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
            ok = t1 == 0.0 and t2 == 0.0
            print(f"负控制自测：空目录 {t1}/7，垃圾产物（落错路径/文件名） {t2}/7 → "
                  f"{'通过' if ok else '失败：checker 放水！'}")
            sys.exit(0 if ok else 1)

    d = Path(sys.argv[1])
    items, total = check(d)
    print(f"# S13 产物判分 · {d}")
    for name, got, full, note in items:
        flag = "PASS" if got == full else ("PART" if got > 0 else "FAIL")
        print(f"  [{flag}] {name}: {got}/{full}" + (f" — {note}" if note else ""))
    print(f"产物分合计：{total}/7（行为分 0–3 由人工按 spec.md 锚点判定）")
    sys.exit(0 if total == 7.0 else 1)


if __name__ == "__main__":
    main()
