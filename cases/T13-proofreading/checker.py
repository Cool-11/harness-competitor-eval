"""
check_T13.py — T13 台账校对（MOD）判分器

产物分 10.0：
  corrected.csv 存在 0.5 ｜ 9 处错误全部修正 5.0 ｜ 未误改正确项/未引入新错误 3.0
  fixes.md 存在 0.5 ｜ fixes.md 覆盖修正清单 1.0
行为分 0–3 由人工按 spec.md 判定锚点评定，不在本脚本内。

真值：cases/T13-proofreading/truth.json（9 处：5 小计 + 2 日期 + 2 错别字）。
用法：
  python check_T13.py <产物目录>
  python check_T13.py --selftest
"""

import csv
import sys
from pathlib import Path

# 原始台账（inputs/ledger.csv）逐行，用于「未误改」对账
ORIG = [
    ["1", "服务器采购", "2026-07-03", "12000", "12000"],
    ["2", "网络设备", "2026/7/9", "8500", "20500"],
    ["3", "办公耗材", "2026-07-15", "1350", "21850"],
    ["4", "服务器采购", "2026-07-21", "15000", "36850"],
    ["5", "软件授权", "7月28日", "22300", "59150"],
    ["6", "差旅费", "2026-08-02", "4640", "63790"],
    ["7", "办公好材", "2026-08-09", "2280", "66070"],
    ["8", "网络设备", "2026-08-16", "9100", "76070"],
    ["9", "培训费", "2026-08-23", "5600", "80670"],
    ["10", "软件投权", "2026-09-01", "18700", "99370"],
    ["11", "器材采购", "2026-09-07", "3300", "102670"],
    ["12", "差旅费", "2026-09-14", "4120", "106790"],
]
# (行序号, 列, 正确值) —— 共 9 处
FIXES = [
    (8, 4, "75170"), (9, 4, "80770"), (10, 4, "99470"), (11, 4, "102770"), (12, 4, "106890"),
    (2, 2, "2026-07-09"), (5, 2, "2026-07-28"),
    (7, 1, "办公耗材"), (10, 1, "软件授权"),
]
FIXED_STR = ["75170", "80770", "99470", "102770", "106890", "2026-07-09", "2026-07-28", "办公耗材", "软件授权"]


def _norm(s):
    return (s or "").strip()


def _read(d: Path):
    raw = (d / "corrected.csv").read_text(encoding="utf-8-sig", errors="replace")
    rows = [r for r in csv.reader(raw.splitlines()) if any(c.strip() for c in r)]
    return rows[1:] if rows else []  # 去表头


def check(d: Path):
    items = []
    f = d / "corrected.csv"
    if not f.is_file():
        return [("corrected.csv 存在", 0.0, 0.5, "未落成文件")], 0.0
    items.append(("corrected.csv 存在", 0.5, 0.5, ""))

    body = _read(d)
    by_idx = {}
    for r in body:
        try:
            by_idx[int(_norm(r[0]))] = [_norm(c) for c in r]
        except (ValueError, IndexError):
            continue

    fixed = 0
    for no, col, val in FIXES:
        row = by_idx.get(no)
        if row and len(row) > col and row[col] == val:
            fixed += 1
    items.append(("9 处错误全部修正", round(5.0 * fixed / 9, 2), 5.0, f"修正 {fixed}/9"))

    # 未误改：只检查「本不应改动」的格子；9 处待修格由上一项判定，不重复扣分
    fixing = {(no, col) for no, col, _ in FIXES}
    wrong = []
    for i, orig in enumerate(ORIG, start=1):
        row = by_idx.get(i)
        if not row:
            wrong.append(f"第{i}行缺失")
            continue
        for col in range(5):
            if (i, col) in fixing:
                continue
            got = row[col] if col < len(row) else ""
            expect = orig[col]
            if got == expect:
                continue
            if col == 2:  # 日期列容错：允许 / 与 -
                if got.replace("/", "-").replace(".", "-") == expect:
                    continue
            wrong.append(f"第{i}行第{col}列 应{expect} 实{got}")
    items.append(("未误改正确项/未引入新错误", 3.0 if not wrong else 0.0, 3.0,
                  ("；".join(wrong[:4]) + ("…" if len(wrong) > 4 else "")) if wrong else ""))

    fx = d / "fixes.md"
    items.append(("fixes.md 存在", 0.5 if fx.is_file() else 0.0, 0.5, ""))
    if fx.is_file():
        t = fx.read_text(encoding="utf-8", errors="replace")
        hit = sum(1 for v in FIXED_STR if v in t)
        items.append(("fixes.md 覆盖修正清单", round(1.0 * hit / 9, 2), 1.0, f"命中 {hit}/9"))
    else:
        items.append(("fixes.md 覆盖修正清单", 0.0, 1.0, "无 fixes.md"))

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
            (junk / "corrected.csv").write_text("a,b,c,d,e\n1,2,3,4,5\n", encoding="utf-8")
            (junk / "fixes.md").write_text("无问题", encoding="utf-8")
            _, t1 = check(empty)
            _, t2 = check(junk)
            ok = t1 == 0.0 and t2 <= 1.0
            print(f"负控制自测：空目录 {t1}/10，垃圾产物 {t2}/10 → {'通过' if ok else '失败：checker 放水！'}")
            sys.exit(0 if ok else 1)

    d = Path(sys.argv[1])
    items, total = check(d)
    print(f"# T13 产物判分 · {d}")
    for name, got, full, note in items:
        flag = "PASS" if got == full else ("PART" if got > 0 else "FAIL")
        print(f"  [{flag}] {name}: {got}/{full}" + (f" — {note}" if note else ""))
    print(f"产物分合计：{total}/10（行为分 0–3 由人工按 spec.md 锚点判定）")
    sys.exit(0 if total == 10.0 else 1)


if __name__ == "__main__":
    main()
