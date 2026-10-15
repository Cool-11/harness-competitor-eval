"""
check_T00b.py — 产物形态探测题判分器（校准题，只报能力边界，不产生得分）

用法：
  python check_T00b.py <产物目录>
  python check_T00b.py --selftest      # 负控制自测
"""

import csv
import sys
from pathlib import Path

EXPECTED_ROWS = [
    ["2026-09-01", "智能音箱", "120", "199"],
    ["2026-09-03", "智能音箱", "85", "199"],
    ["2026-09-05", "智能门锁", "60", "899"],
    ["2026-09-08", "智能门锁", "42", "899"],
    ["2026-09-11", "扫地机器人", "18", "2499"],
    ["2026-09-15", "扫地机器人", "25", "2499"],
    ["2026-09-20", "智能音箱", "210", "199"],
]
HEADER = ["日期", "产品", "数量", "单价", "金额"]


def _norm(s: str) -> str:
    return s.strip().replace("（", "(").replace("）", ")").replace("，", ",")


def check(d: Path):
    caps = {}   # 能力边界探测
    notes = []

    md = d / "report.md"
    csvf = d / "summary.csv"
    caps["能产出 .md 文件"] = md.is_file()
    caps["能产出 .csv 文件"] = csvf.is_file()
    caps["能同时产出多个文件"] = md.is_file() and csvf.is_file()

    if md.is_file():
        text = md.read_text(encoding="utf-8", errors="replace")
        n = len([c for c in text if not c.isspace()])
        caps["report.md ≤150 字"] = n <= 150
        notes.append(f"report.md 非空白字符数 {n}")

    if csvf.is_file():
        raw = csvf.read_text(encoding="utf-8-sig", errors="replace")
        rows = [r for r in csv.reader(raw.splitlines()) if any(_norm(c) for c in r)]
        header_ok = bool(rows) and all(
            _norm(h) in [_norm(c) for c in rows[0]] for h in HEADER
        )
        caps["summary.csv 五列表头"] = header_ok
        body = rows[1:] if rows else []
        caps["数据行数 = 7"] = len(body) == 7
        orig_ok = True
        calc_ok = True
        for i, exp in enumerate(EXPECTED_ROWS):
            if i >= len(body):
                orig_ok = calc_ok = False
                break
            got = [_norm(c) for c in body[i]]
            if [g for g in got[:4]] != exp:
                orig_ok = False
            try:
                if abs(float(got[4]) - float(exp[2]) * float(exp[3])) > 1e-6:
                    calc_ok = False
            except (IndexError, ValueError):
                calc_ok = False
        caps["原有四列未被改动"] = orig_ok
        caps["金额 = 数量×单价"] = calc_ok

    return caps, notes


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)

    if sys.argv[1] == "--selftest":
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            empty = Path(td) / "empty"; empty.mkdir()
            junk = Path(td) / "junk"; junk.mkdir()
            (junk / "report.md").write_text("无关内容", encoding="utf-8")
            (junk / "summary.csv").write_text("a,b,c\n1,2,3\n", encoding="utf-8")
            c1, _ = check(empty)
            c2, _ = check(junk)
            bad1 = [c1.get("能产出 .md 文件"), c1.get("能产出 .csv 文件")]
            bad2 = [c2.get("summary.csv 五列表头"), c2.get("金额 = 数量×单价")]
            ok = (bad1 == [False, False]) and (bad2 == [False, False])
            print(f"负控制自测：{'通过' if ok else '失败：checker 放水！'}")
            sys.exit(0 if ok else 1)

    d = Path(sys.argv[1])
    caps, notes = check(d)
    print(f"# T00b 能力边界探测 · {d}")
    for k, v in caps.items():
        print(f"  [{'YES' if v else 'NO '}] {k}")
    for n in notes:
        print(f"  · {n}")
    print("（校准题不计分：本结果写入 runs/baseline 的能力边界表）")
    sys.exit(0)


if __name__ == "__main__":
    main()
