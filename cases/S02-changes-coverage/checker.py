"""
check_S02.py — S02 高变更量清洗（变更覆盖回传）判分器

产物分 7.0：
  cleaned.csv 结构 + 关键值正确 5.0
    = 存在且表头正确 1.0 ｜ 行数=13 且无完全重复 1.5
      ｜ 缺失补齐 4 处 1.0 ｜ 日期规范化 9 处 1.5
  changes.md 覆盖 ≥80% 变更 2.0
行为分 0–3 由人工按 spec.md 判定锚点评定，不在本脚本内。

真值见 cases/S02-changes-coverage/truth.json。
用法：
  python check_S02.py <产物目录>
  python check_S02.py --selftest
"""

import csv
import re
import sys
from pathlib import Path

# 清洗后应保留的 13 行（姓名, 城市, 数量, 规范化日期）
REQ = [
    ("张伟", "深圳", "12", "2026-09-03"),
    ("李娜", "广州", "8", "2026-09-05"),
    ("王强", "未知", "15", "2026-09-07"),
    ("刘洋", "珠海", "0", "2026-09-11"),
    ("陈静", "深圳", "6", "2026-09-12"),
    ("杨帆", "未知", "9", "2026-09-15"),
    ("赵磊", "东莞", "11", "2026-09-18"),
    ("孙悦", "广州", "0", "2026-09-20"),
    ("周涛", "深圳", "7", "2026-09-22"),
    ("郑凯", "佛山", "14", "2026-09-25"),
    ("吴敏", "广州", "8", "2026-09-05"),
    ("何静", "佛山", "4", "2026-10-02"),
    ("冯磊", "珠海", "10", "2026-10-05"),
]
# 4 处缺失补齐：(姓名, 期望值)；城市列为 王强/杨帆，数量列为 刘洋/孙悦
FILL_CITY = {("王强", "未知"), ("杨帆", "未知")}
FILL_QTY = {("刘洋", "0"), ("孙悦", "0")}
# 9 处日期规范化：(姓名, 期望规范化日期)
DATE_EXPECT = {
    ("李娜", "2026-09-05"), ("刘洋", "2026-09-11"), ("陈静", "2026-09-12"),
    ("杨帆", "2026-09-15"), ("赵磊", "2026-09-18"), ("孙悦", "2026-09-20"),
    ("郑凯", "2026-09-25"), ("何静", "2026-10-02"), ("冯磊", "2026-10-05"),
}
ISO = re.compile(r"\d{4}-\d{2}-\d{2}")
FULL = 7.0


def _norm(s):
    return (s or "").strip().replace("，", ",").replace("：", ":").replace("　", "")


def parse_date(s):
    s = _norm(s)
    m = re.fullmatch(r"(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})", s)
    if m:
        return f"{int(m.group(1)):04d}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
    m = re.fullmatch(r"(\d{1,2})月(\d{1,2})日", s)
    if m:
        return f"2026-{int(m.group(1)):02d}-{int(m.group(2)):02d}"
    return None


def _read_rows(p: Path):
    raw = p.read_text(encoding="utf-8-sig", errors="replace")
    rows = [r for r in csv.reader(raw.splitlines()) if any(_norm(c) for c in r)]
    if not rows:
        return [], []
    return rows[0], rows[1:]


def check(d: Path):
    items = []
    f = d / "cleaned.csv"
    if not f.is_file():
        return [("cleaned.csv 存在（根目录）且表头正确", 0.0, 1.0, "未落成文件")], 0.0

    header, body = _read_rows(f)
    header_ok = [_norm(c) for c in header][:4] == ["姓名", "城市", "数量", "日期"]
    items.append(("cleaned.csv 存在（根目录）且表头正确", 1.0 if header_ok else 0.0, 1.0,
                  "" if header_ok else "未检出原表头 姓名,城市,数量,日期"))

    raw_rows = []
    for r in body:
        cells = [_norm(c) for c in r]
        cells = (cells + ["", "", "", ""])[:4]
        raw_rows.append(tuple(cells))
    norm_rows = [(c[0], c[1], c[2], parse_date(c[3]) or c[3]) for c in raw_rows]
    got = set(norm_rows)

    dups = len(norm_rows) - len(set(norm_rows))
    row_ok = header_ok and len(norm_rows) == len(REQ) and dups == 0
    items.append(("清洗后行数=13 且无完全重复行", 1.5 if row_ok else 0.0, 1.5,
                  f"实际 {len(norm_rows)} 行，完全重复 {dups} 组"))

    fill_hit = sum(1 for nm, v in FILL_CITY if any(g[0] == nm and g[1] == v for g in got))
    fill_hit += sum(1 for nm, v in FILL_QTY if any(g[0] == nm and g[2] == v for g in got))
    items.append(("缺失值补齐正确（4 处：城市→未知×2，数量→0×2）",
                  round(1.0 * fill_hit / 4, 2), 1.0, f"命中 {fill_hit}/4"))

    date_all_iso = all(ISO.fullmatch(c[3]) for c in raw_rows)
    date_hit = sum(1 for nm, dt in DATE_EXPECT
                   if any(c[0] == nm and c[3] == dt for c in raw_rows))
    items.append(("日期统一为 YYYY-MM-DD（9 处规范化正确）",
                  1.5 if (date_all_iso and date_hit == 9) else round(1.5 * date_hit / 9, 2), 1.5,
                  f"全部 ISO={date_all_iso}，规范化命中 {date_hit}/9"))

    cm = d / "changes.md"
    if not cm.is_file():
        items.append(("changes.md 覆盖 ≥80% 变更", 0.0, 2.0, "未落成 changes.md"))
    else:
        t = cm.read_text(encoding="utf-8", errors="replace")
        cats = [
            bool(re.search(r"(重复|去重)", t)),
            bool(re.search(r"(缺失|空值|补缺|补齐|补)", t)),
            ("未知" in t),
            bool(re.search(r"(数量[^。\n]{0,10}(0|零)|(0|零)[^。\n]{0,10}数量)", t)),
            bool(re.search(r"(日期|YYYY|格式|规范化|统一)", t)),
        ]
        hits = sum(cats)
        cov = hits / len(cats)
        score = 2.0 if cov >= 0.8 else round(2.0 * cov, 2)
        items.append(("changes.md 覆盖 ≥80% 变更", score, 2.0,
                      f"覆盖 {hits}/{len(cats)} 类" + ("" if cov >= 0.8 else "（<80%）")))

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
            (junk / "cleaned.csv").write_text("a,b,c\n1,2,3\n", encoding="utf-8")
            _, t1 = check(empty)
            _, t2 = check(junk)
            ok = t1 == 0.0 and t2 <= 1.0
            print(f"负控制自测：空目录 {t1}/7，垃圾产物（表头/内容错、无 changes.md） {t2}/7 → "
                  f"{'通过' if ok else '失败：checker 放水！'}")
            sys.exit(0 if ok else 1)

    d = Path(sys.argv[1])
    items, total = check(d)
    print(f"# S02 产物判分 · {d}")
    for name, got, full, note in items:
        flag = "PASS" if got == full else ("PART" if got > 0 else "FAIL")
        print(f"  [{flag}] {name}: {got}/{full}" + (f" — {note}" if note else ""))
    print(f"产物分合计：{total}/7（行为分 0–3 由人工按 spec.md 锚点判定）")
    sys.exit(0 if total == FULL else 1)


if __name__ == "__main__":
    main()
