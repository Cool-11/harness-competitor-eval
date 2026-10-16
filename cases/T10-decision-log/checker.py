"""
check_T10.py — T10 决策日志（GEN）判分器

产物分 7.0：
  plan.md 存在 0.5 ｜ 表头「事项|时间|负责方」1.0 ｜ 5 事项无遗漏且按时间排序 2.5
  decision_log.md 存在 0.5 ｜ 决策记录完整（≥5 条且含取舍）2.5
行为分 0–3 由人工按 spec.md 判定锚点评定，不在本脚本内。

真值依据：inputs/source_notes.md 共 5 事项，正确时间顺序见 EVENTS。
用法：
  python check_T10.py <产物目录>
  python check_T10.py --selftest
"""

import re
import sys
from pathlib import Path

# (关键词, 期望(月,日))
EVENTS = {
    "调研问卷": (9, 22),
    "接口联调": (9, 28),
    "组织培训": (10, 8),
    "验收材料": (10, 15),
    "设备清单": (10, 20),
}


def _date_in(line: str):
    m = re.search(r"(\d{1,2})\s*月\s*(\d{1,2})\s*日", line)
    if m:
        return (int(m.group(1)), int(m.group(2)))
    m = re.search(r"\d{4}[-/.](\d{1,2})[-/.](\d{1,2})", line)
    if m:
        return (int(m.group(1)), int(m.group(2)))
    return None


def check(d: Path):
    items = []
    plan, dlog = d / "plan.md", d / "decision_log.md"
    if not plan.is_file():
        items.append(("plan.md 存在", 0.0, 0.5, "未落成文件"))
    else:
        items.append(("plan.md 存在", 0.5, 0.5, ""))
        text = plan.read_text(encoding="utf-8", errors="replace")
        compact = text.replace(" ", "").replace("\u3000", "")
        head_ok = all(k in compact for k in ["事项", "时间", "负责方"])
        items.append(("表头含「事项|时间|负责方」", 1.0 if head_ok else 0.0, 1.0, ""))

        # 事件命中 + 时间排序
        found, seq, missing = 0, [], []
        for kw, exp in EVENTS.items():
            line = next((l for l in text.splitlines() if kw in l), None)
            if line is None:
                missing.append(kw)
                continue
            found += 1
            dt = _date_in(line) or exp
            seq.append((dt, kw))
        order_ok = (found == 5) and all(seq[i][0] <= seq[i + 1][0] for i in range(len(seq) - 1))
        score = round(1.25 * found / 5, 2) + (1.25 if order_ok else 0.0)
        items.append(("5 事项无遗漏且按时间排序", min(score, 2.5), 2.5,
                      (f"缺：{'、'.join(missing)}" if missing else "") + ("" if order_ok else "；顺序不符")))

    items.append(("decision_log.md 存在", 0.5 if dlog.is_file() else 0.0, 0.5, ""))
    if dlog.is_file():
        t = dlog.read_text(encoding="utf-8", errors="replace")
        why = len(re.findall(r"(为什么|原因|理由|因为)", t))
        gave = len(re.findall(r"(放弃|未采用|不考虑|另可|备选|取舍)", t))
        entries = len(re.findall(r"^\s*(#{1,6}\s*)?(决定|决策)\s*\d*", t, re.M)) or \
            len([l for l in t.splitlines() if l.strip().startswith(("-", "*", "1.", "2.", "3.", "4.", "5."))])
        ok = entries >= 5 and why >= 3 and gave >= 1
        items.append(("决策记录完整（≥5 条且含取舍）", 2.5 if ok else 0.0, 2.5,
                      f"条目 {entries}，含'为什么' {why}，含'放弃' {gave}"))
    else:
        items.append(("决策记录完整（≥5 条且含取舍）", 0.0, 2.5, "无 decision_log.md"))

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
            (junk / "plan.md").write_text("| a | b | c |\n| 1 | 2 | 3 |\n", encoding="utf-8")
            (junk / "decision_log.md").write_text("完成了。", encoding="utf-8")
            _, t1 = check(empty)
            _, t2 = check(junk)
            ok = t1 == 0.0 and t2 <= 1.0
            print(f"负控制自测：空目录 {t1}/7，垃圾产物 {t2}/7 → {'通过' if ok else '失败：checker 放水！'}")
            sys.exit(0 if ok else 1)

    d = Path(sys.argv[1])
    items, total = check(d)
    print(f"# T10 产物判分 · {d}")
    for name, got, full, note in items:
        flag = "PASS" if got == full else ("PART" if got > 0 else "FAIL")
        print(f"  [{flag}] {name}: {got}/{full}" + (f" — {note}" if note else ""))
    print(f"产物分合计：{total}/7（行为分 0–3 由人工按 spec.md 锚点判定）")
    sys.exit(0 if total == 7.0 else 1)


if __name__ == "__main__":
    main()
