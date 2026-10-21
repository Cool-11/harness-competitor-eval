"""
check_T03.py — T03 报告链（CHAIN）判分器

产物分 8.0：
  三文件齐全 1.0 ｜ report 四章节标题 1.5 ｜ 章节内容对应材料 1.5
  summary ≤200 字 1.5 ｜ index 行号与 report 实际一致 2.5
行为分 0–3 由人工按 spec.md 判定锚点评定，不在本脚本内。

依据：cases/T03-report-chain/task.md 完成条件。index 行号逐行核对 report.md 实际起始行。
用法：
  python check_T03.py <产物目录>
  python check_T03.py --selftest
"""

import re
import sys
from pathlib import Path

SECTIONS = ["背景", "数据发现", "用户反馈", "结论"]
W = {"files": 1.0, "sections": 1.5, "content": 1.5, "summary": 1.5, "index": 2.5}

# 各章节应体现的材料要点（命中任一即可算该章节有据）
ANCHORS = {
    "背景": ["立项", "制造", "80", "6 人", "6人", "v0.3", "试点"],
    "数据发现": ["3,128", "3128", "24", "11", "18%", "61%", "同步"],
    "用户反馈": ["弱网", "班组", "ERP", "培训"],
    "结论": [],  # 结论自由，不设锚点
}


def _compact(s: str) -> str:
    return (s or "").replace(" ", "").replace("\u3000", "")


def _split_sections(text: str):
    """按二级标题切分 report.md，返回 {章节名: 正文}。"""
    lines = text.splitlines()
    order = []
    for i, line in enumerate(lines):
        m = re.match(r"^\s*##\s*(\S+)\s*$", line)
        if m and m.group(1) in SECTIONS:
            order.append((m.group(1), i))
    out = {}
    for j, (name, i) in enumerate(order):
        end = order[j + 1][1] if j + 1 < len(order) else len(lines)
        out[name] = "\n".join(lines[i + 1:end])
    return out


def check(d: Path):
    items = []
    rep, summ = d / "report.md", d / "summary.md"
    idxf = d / "index.md"

    have = sum(p.is_file() for p in (rep, summ, idxf))
    items.append(("三文件齐全（report/summary/index）", round(W["files"] * have / 3, 2), W["files"],
                  f"缺：{'/'.join(p.name for p in (rep, summ, idxf) if not p.is_file())}" if have < 3 else ""))
    if not rep.is_file():
        return items, round(sum(i[1] for i in items), 2)

    text = rep.read_text(encoding="utf-8", errors="replace")
    secs = _split_sections(text)
    missing = [s for s in SECTIONS if s not in secs]
    items.append(("report 四章节标题齐全", round(W["sections"] * (4 - len(missing)) / 4, 2), W["sections"],
                  "缺：" + "/".join(missing) if missing else ""))

    hit = 0
    for s in SECTIONS:
        if s in secs and (not ANCHORS[s] or any(a.replace(" ", "") in _compact(secs[s]) for a in ANCHORS[s])):
            hit += 1
    items.append(("四章节内容分别来自对应材料", round(W["content"] * hit / 4, 2), W["content"],
                  f"有据章节 {hit}/4"))

    if summ.is_file():
        st = summ.read_text(encoding="utf-8", errors="replace")
        body = "\n".join(l for l in st.splitlines() if not l.strip().startswith("#"))
        n = len([c for c in body if not c.isspace()])
        ok_n = 10 <= n <= 200
        items.append(("summary 正文 10–200 字", W["summary"] if ok_n else 0.0, W["summary"],
                      f"非空白字符数 {n}（口径：不含空白字符；若按汉字计需人工复核）"))
    else:
        items.append(("summary 正文 ≤200 字", 0.0, W["summary"], "无 summary.md"))

    if idxf.is_file():
        it = idxf.read_text(encoding="utf-8", errors="replace")
        got = {}
        for line in it.splitlines():
            m = re.search(r"(\S+?)\s*[（(]\s*第\s*(\d+)\s*行", line)
            if m:
                got[m.group(1)] = int(m.group(2))
        lines = text.splitlines()
        correct = 0
        detail = []
        for s in SECTIONS:
            actual = next((i + 1 for i, l in enumerate(lines) if re.match(rf"^\s*##\s*{s}\s*$", l)), None)
            g = got.get(s)
            if actual is not None and g == actual:
                correct += 1
            else:
                detail.append(f"{s}:标注{g}/实际{actual}")
        items.append(("index 行号与 report 实际一致", round(W["index"] * correct / 4, 2), W["index"],
                      "；".join(detail)))
    else:
        items.append(("index 行号与 report 实际一致", 0.0, W["index"], "无 index.md"))

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
            (junk / "report.md").write_text("# 无章节\n随便写", encoding="utf-8")
            (junk / "summary.md").write_text("摘要", encoding="utf-8")
            (junk / "index.md").write_text("- 背景（第 99 行）", encoding="utf-8")
            _, t1 = check(empty)
            _, t2 = check(junk)
            ok = t1 == 0.0 and t2 <= 1.0
            print(f"负控制自测：空目录 {t1}/8，垃圾产物 {t2}/8 → {'通过' if ok else '失败：checker 放水！'}")
            sys.exit(0 if ok else 1)

    d = Path(sys.argv[1])
    items, total = check(d)
    print(f"# T03 产物判分 · {d}")
    for name, got, full, note in items:
        flag = "PASS" if got == full else ("PART" if got > 0 else "FAIL")
        print(f"  [{flag}] {name}: {got}/{full}" + (f" — {note}" if note else ""))
    print(f"产物分合计：{total}/8（行为分 0–3 由人工按 spec.md 锚点判定）")
    sys.exit(0 if total == 8.0 else 1)


if __name__ == "__main__":
    main()
