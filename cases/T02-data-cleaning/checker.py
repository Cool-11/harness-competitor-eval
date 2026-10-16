"""
check_T02.py — T02 数据清洗（MOD）判分器

产物分 7.0：
  cleaned.csv  存在 1.0 ｜ 行数=11 且无完全重复行 1.5 ｜ 缺失补齐 1.0 ｜ 日期规范化 1.5 ｜ 未越权改动 1.0
  changes.md   存在 0.5 ｜ 变更覆盖（去重/补缺/日期三类）0.5

修订 2026-10-17（登记）：原真值把「李娜/吴敏 同城同量同日但**姓名不同**」判为重复（期望 10 行），
与任务书字面「删除**完全重复**的行」冲突——五款按字面保留两行（11 行）却被判 FAIL。
经 docs/10 §3.1 第⓪.5 步「真值自洽」判定为 oracle 错，改真值为 11 行；**题面不变**。
行为分 0–3 由人工按 spec.md 判定锚点评定，不在本脚本内。

真值依据：cases/T02-data-cleaning/truth.json（机读真值，绝不进产品工作目录）。
用法：
  python check_T02.py <产物目录>
  python check_T02.py --selftest
"""

import csv
import re
import sys
from pathlib import Path

W = {"exists": 1.0, "rows_dedup": 1.5, "fill": 1.0, "date": 1.5,
     "nochange": 1.0, "ch_exists": 0.5, "ch_cover": 0.5}

# 去重后应保留的确定行（姓名,城市,数量,日期）
REQ = [
    ("张伟", "深圳", "12", "2026-09-03"),
    ("王强", "未知", "15", "2026-09-07"),
    ("刘洋", "珠海", "0", "2026-09-11"),
    ("陈静", "深圳", "6", "2026-09-12"),
    ("杨帆", "未知", "9", "2026-09-15"),
    ("赵磊", "东莞", "11", "2026-09-18"),
    ("孙悦", "广州", "0", "2026-09-20"),
    ("周涛", "深圳", "7", "2026-09-22"),
    ("郑凯", "佛山", "14", "2026-09-25"),
]
# 李娜/吴敏 姓名不同 → 非「完全重复」，二者都应保留（修订 2026-10-17）
BOTH_KEEP = {("李娜", "广州", "8", "2026-09-05"), ("吴敏", "广州", "8", "2026-09-05")}


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
        return [("cleaned.csv 存在", 0.0, W["exists"], "未落成文件")], 0.0
    items.append(("cleaned.csv 存在", W["exists"], W["exists"], ""))

    header, body = _read_rows(f)
    header_ok = [ _norm(c) for c in header][:4] == ["姓名", "城市", "数量", "日期"]

    # 归一化为 4 元组
    norm_rows = []
    for r in body:
        cells = [_norm(c) for c in r]
        cells = (cells + ["", "", "", ""])[:4]
        cells[3] = parse_date(cells[3]) or cells[3]
        norm_rows.append(tuple(cells))

    # 行数=11 且无完全重复行
    dups = len(norm_rows) - len(set(norm_rows))
    ok = header_ok and len(norm_rows) == 11 and dups == 0
    items.append(("表头保留 + 行数=11 + 无完全重复行", W["rows_dedup"] if ok else 0.0, W["rows_dedup"],
                  f"表头{'对' if header_ok else '错'}，实际 {len(norm_rows)} 行，完全重复 {dups} 组"))

    # 缺失补齐（王强/杨帆 城市→未知；刘洋/孙悦 数量→0）
    fill_expect = {("王强", "未知"), ("杨帆", "未知"), ("刘洋", "0"), ("孙悦", "0")}
    got_fill = {(r[0], r[1] if r[0] in ("王强", "杨帆") else r[2]) for r in norm_rows}
    fill_hit = len(fill_expect & got_fill)
    items.append(("缺失值补齐正确（4 处）", round(W["fill"] * fill_hit / 4, 2), W["fill"],
                  f"命中 {fill_hit}/4"))

    # 日期规范化：所有日期均可解析，且 4 个待规范化行正确
    date_expect = {("张伟", "2026-09-03"), ("王强", "2026-09-07"),
                   ("赵磊", "2026-09-18"), ("郑凯", "2026-09-25")}
    all_parsed = all(parse_date(r[3]) is not None for r in norm_rows)
    date_hit = sum(1 for name, dt in date_expect if any(r[0] == name and r[3] == dt for r in norm_rows))
    d_ok = all_parsed and date_hit == 4
    items.append(("日期统一为 YYYY-MM-DD 且 4 处规范化正确", W["date"] if d_ok else round(W["date"] * date_hit / 4, 2),
                  W["date"], f"可解析={all_parsed}，规范化命中 {date_hit}/4"))

    # 未越权改动：结果集 == 9 确定行 + 1 个可接受行
    got = set(norm_rows)
    both_ok = len(got & BOTH_KEEP) == 2
    extra = got - set(REQ) - BOTH_KEEP
    miss = set(REQ) - got
    nochange_ok = both_ok and not extra and not miss
    detail = ""
    if not nochange_ok:
        if extra:
            detail += f"多出 {extra}；"
        if miss:
            detail += f"缺失 {miss}；"
        if not both_ok:
            detail += "李娜/吴敏 非完全重复，二者应都保留"
    items.append(("未改动无关列/未增删无关行", W["nochange"] if nochange_ok else 0.0, W["nochange"], detail))

    # changes.md
    cm = d / "changes.md"
    if not cm.is_file():
        items.append(("changes.md 存在", 0.0, W["ch_exists"], "缺失"))
        items.append(("变更覆盖（去重/补缺/日期）", 0.0, W["ch_cover"], "无文件"))
    else:
        items.append(("changes.md 存在", W["ch_exists"], W["ch_exists"], ""))
        t = cm.read_text(encoding="utf-8", errors="replace")
        cats = {
            "去重": bool(re.search(r"(重复|去重|删除.{0,6}行|去掉了?重复)", t)),
            "补缺": bool(re.search(r"(缺失|空|未知|补)", t)),
            "日期": bool(re.search(r"(日期|格式|YYYY|规范化)", t)),
        }
        hit = sum(cats.values())
        items.append(("变更覆盖（去重/补缺/日期三类）", round(W["ch_cover"] * hit / 3, 2), W["ch_cover"],
                      "缺：" + "/".join(k for k, v in cats.items() if not v) if hit < 3 else ""))

    total = round(sum(i[1] for i in items), 2)
    return items, total


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)

    if sys.argv[1] == "--selftest":
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            empty = Path(td) / "e"; empty.mkdir()
            junk = Path(td) / "j"; junk.mkdir()
            (junk / "cleaned.csv").write_text("a,b,c\n1,2,3\n", encoding="utf-8")
            _, t1 = check(empty)
            _, t2 = check(junk)
            ok = t1 == 0.0 and t2 <= 1.0
            print(f"负控制自测：空目录 {t1}/7，垃圾产物 {t2}/7 → {'通过' if ok else '失败：checker 放水！'}")
            sys.exit(0 if ok else 1)

    d = Path(sys.argv[1])
    items, total = check(d)
    print(f"# T02 产物判分 · {d}")
    for name, got, full, note in items:
        flag = "PASS" if got == full else ("PART" if got > 0 else "FAIL")
        print(f"  [{flag}] {name}: {got}/{full}" + (f" — {note}" if note else ""))
    print(f"产物分合计：{total}/7（行为分 0–3 由人工按 spec.md 锚点判定）")
    sys.exit(0 if total == 7.0 else 1)


if __name__ == "__main__":
    main()
