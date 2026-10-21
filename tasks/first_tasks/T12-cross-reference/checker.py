"""
check_T12.py — T12 跨文件检索（RETR）判分器

产物分 8.0：
  三部分二级标题齐全 1.5 ｜ 涉及文件无遗漏 2.0 ｜ 各文件金额正确 2.0
  合计 822,500 正确 1.5 ｜ 无张冠李戴 1.0
行为分 0–3 由人工按 spec.md 判定锚点评定，不在本脚本内。

真值：cases/T12-cross-reference/truth.json
存疑：备忘录-1.md 是否应计入（truth.json 未收）——本 checker 对「多列 备忘录-1」不扣分，
      该边界待作者裁定后修订 truth.json（见 runs/Five-app-log-analyse 存疑①）。
用法：
  python check_T12.py <产物目录>
  python check_T12.py --selftest
"""

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SECTIONS = ["涉及文件", "各文件金额", "合计"]
TOTAL = 822500
PENDING_OK = {"备忘录-1.md", "备忘录-1"}


def _norm(s):
    return re.sub(r"[\s\u3000]", "", s or "")


def check(d: Path):
    truth = json.loads((HERE / "truth.json").read_text(encoding="utf-8"))
    files = truth["提及华创科技的文件"]
    amounts = truth["含金额的文件与金额"]

    items = []
    f = d / "cross_ref.md"
    if not f.is_file():
        return [("cross_ref.md 存在", 0.0, 1.5, "未落成文件")], 0.0

    text = f.read_text(encoding="utf-8", errors="replace")
    compact = _norm(text)
    nocomma = re.sub(r"[,，]", "", text)   # 金额千分位归一：128,000 → 128000

    sec_hit = sum(1 for s in SECTIONS if re.search(rf"^\s*##\s*{s}", text, re.M))
    items.append(("三部分二级标题齐全", round(1.5 * sec_hit / 3, 2), 1.5,
                  f"命中 {sec_hit}/3"))

    miss = [name for name in files if _norm(Path(name).stem) not in compact]
    items.append(("涉及文件无遗漏", round(2.0 * (len(files) - len(miss)) / len(files), 2), 2.0,
                  ("缺：" + "、".join(miss)) if miss else ""))
    if any(_norm(Path(p).stem) in compact for p in PENDING_OK):
        items[-1] = (items[-1][0], items[-1][1], items[-1][2],
                     (items[-1][3] + "；" if items[-1][3] else "") + "另多列 备忘录-1（存疑①，不扣分）")

    amt_ok = 0
    for name, val in amounts.items():
        stem = _norm(Path(name).stem)
        v = str(val)
        if re.search(rf"{re.escape(stem)}[^\n]{{0,40}}?{v}", nocomma) or \
           re.search(rf"{v}[^\n]{{0,40}}?{re.escape(stem)}", nocomma):
            amt_ok += 1
    items.append(("各文件金额与原文一致", round(2.0 * amt_ok / len(amounts), 2), 2.0,
                  f"命中 {amt_ok}/{len(amounts)}"))

    tot_ok = str(TOTAL) in re.sub(r"[,，]", "", text)
    items.append(("合计 822,500 正确", 1.5 if tot_ok else 0.0, 1.5, "" if tot_ok else "未见正确合计"))

    # 无张冠李戴：出现的合同金额均应为真值集合中的值（千分位已归一）
    known = {str(v) for v in amounts.values()}
    nums = set(re.findall(r"\d{5,7}", nocomma))
    stray = {n for n in nums if n not in known and n != str(TOTAL)}
    items.append(("无金额张冠李戴", 1.0 if not stray else 0.0, 1.0,
                  f"出现非真值金额：{sorted(stray)}" if stray else ""))

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
            (junk / "cross_ref.md").write_text("## 涉及文件\n无\n## 合计\n999999\n", encoding="utf-8")
            _, t1 = check(empty)
            _, t2 = check(junk)
            ok = t1 == 0.0 and t2 <= 2.0
            print(f"负控制自测：空目录 {t1}/8，垃圾产物 {t2}/8 → {'通过' if ok else '失败：checker 放水！'}")
            sys.exit(0 if ok else 1)

    d = Path(sys.argv[1])
    items, total = check(d)
    print(f"# T12 产物判分 · {d}")
    for name, got, full, note in items:
        flag = "PASS" if got == full else ("PART" if got > 0 else "FAIL")
        print(f"  [{flag}] {name}: {got}/{full}" + (f" — {note}" if note else ""))
    print(f"产物分合计：{total}/8（行为分 0–3 由人工按 spec.md 锚点判定）")
    sys.exit(0 if total == 8.0 else 1)


if __name__ == "__main__":
    main()
