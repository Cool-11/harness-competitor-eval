"""
check_T04.py — T04 长文档提取（RETR）判分器

产物分 8.0：
  文件+表头 1.5 ｜ 条目数=20 1.5 ｜ 编号顺序 1.0
  风险事项文本准确率 2.0 ｜ 阶段/严重程度/提出人 准确率 2.0
行为分 0–3 由人工按 spec.md 判定锚点评定，不在本脚本内。

真值：cases/T04-long-doc-extract/truth.json（编号/风险事项/阶段/严重程度）
      提出人由 long_doc.md 逐条抄录（见 PERSON）。
用法：
  python check_T04.py <产物目录>
  python check_T04.py --selftest
"""

import csv
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
HEADER = ["编号", "风险事项", "所属阶段", "严重程度", "提出人"]
PERSON = ["赵磊", "王强", "张伟", "王强", "杨帆", "张伟", "杨帆", "赵磊", "赵磊", "刘洋",
          "王强", "陈静", "刘洋", "杨帆", "赵磊", "王强", "李娜", "李娜", "杨帆", "王强"]


def _norm(s: str) -> str:
    return re.sub(r"[\s\u3000,，、;；:：]", "", (s or ""))


def _truth():
    return json.loads((HERE / "truth.json").read_text(encoding="utf-8"))


def check(d: Path):
    items = []
    f = d / "summary.csv"
    if not f.is_file():
        return [("summary.csv 存在", 0.0, 1.5, "未落成文件")], 0.0

    raw = f.read_text(encoding="utf-8-sig", errors="replace")
    rows = [r for r in csv.reader(raw.splitlines()) if any(c.strip() for c in r)]
    header = [_norm(c) for c in rows[0]] if rows else []
    body = rows[1:]
    head_ok = header[:5] == [_norm(h) for h in HEADER]
    items.append(("文件存在 + 表头完全正确", 1.5 if head_ok else (0.5 if rows else 0.0), 1.5,
                  "" if head_ok else f"实际表头 {rows[0] if rows else '空'}"))

    truth = _truth()
    items.append(("提取条目数 = 20", 1.5 if len(body) == 20 else 0.0, 1.5, f"实际 {len(body)} 条"))

    # 编号顺序 1..20
    nums = []
    for r in body:
        try:
            nums.append(int(_norm(r[0])))
        except (ValueError, IndexError):
            nums.append(None)
    order_ok = nums[:20] == list(range(1, 21))
    items.append(("编号按出现顺序 1→20", 1.0 if order_ok else 0.0, 1.0, ""))

    # 风险事项文本准确
    ok_item = 0
    for i, t in enumerate(truth):
        if i < len(body) and _norm(t["风险事项"]) in _norm("".join(body[i])):
            ok_item += 1
    items.append(("风险事项文本准确（逐条）", round(2.0 * ok_item / 20, 2), 2.0, f"命中 {ok_item}/20"))

    # 阶段/严重程度/提出人（抽查全部 20 条的三列）
    ok_meta = 0
    for i, t in enumerate(truth):
        if i >= len(body):
            break
        joined = _norm("".join(body[i]))
        if _norm(t["所属阶段"]) in joined and _norm(t["严重程度"]) in joined and _norm(PERSON[i]) in joined:
            ok_meta += 1
    items.append(("阶段/严重程度/提出人准确", round(2.0 * ok_meta / 20, 2), 2.0, f"命中 {ok_meta}/20"))

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
            (junk / "summary.csv").write_text("a,b\n1,2\n", encoding="utf-8")
            _, t1 = check(empty)
            _, t2 = check(junk)
            ok = t1 == 0.0 and t2 <= 1.0
            print(f"负控制自测：空目录 {t1}/8，垃圾产物 {t2}/8 → {'通过' if ok else '失败：checker 放水！'}")
            sys.exit(0 if ok else 1)

    d = Path(sys.argv[1])
    items, total = check(d)
    print(f"# T04 产物判分 · {d}")
    for name, got, full, note in items:
        flag = "PASS" if got == full else ("PART" if got > 0 else "FAIL")
        print(f"  [{flag}] {name}: {got}/{full}" + (f" — {note}" if note else ""))
    print(f"产物分合计：{total}/8（行为分 0–3 由人工按 spec.md 锚点判定）")
    sys.exit(0 if total == 8.0 else 1)


if __name__ == "__main__":
    main()
