"""
check_T01.py — T01 会议纪要结构化 判分器

产物分 6 分 = 文件存在 1 + 五标题齐全 2 + 五事实点 2 + 未确定标注 1
（行为分 4 分由人工按 observation-checklist.md 判，不在本脚本内）

用法：
  python check_T01.py <产物目录>
  python check_T01.py --selftest
"""

import sys
from pathlib import Path

SECTIONS = ["议题", "结论", "待办", "责任人", "截止时间"]
FACTS = [
    ("问卷回收率 62%", ["62"]),
    ("版本推迟到 11 月 20 日", ["11月20日", "11 月 20 日", "11月 20日"]),
    ("预算表截止 10 月 14 日", ["10月14日", "10 月 14 日"]),
    ("测试用例截止 10 月 18 日", ["10月18日", "10 月 18 日"]),
    ("下次会议 10 月 16 日 10 点", ["10月16日", "10 月 16 日"]),
]

# 权重表（写死，禁止运行时改动）
W = {"exists": 1.0, "sections": 2.0, "facts": 2.0, "undetermined": 1.0}


def check(d: Path):
    items = []
    f = d / "meeting_notes.md"
    if not f.is_file():
        return [("文件存在", 0.0, W["exists"], "meeting_notes.md 不存在")], 0.0
    items.append(("文件存在", W["exists"], W["exists"], ""))

    text = f.read_text(encoding="utf-8", errors="replace")
    compact = text.replace(" ", "").replace("\u3000", "")

    # 1) 五个二级标题齐全且文字一致
    missing = [s for s in SECTIONS if f"##{s}" not in compact]
    got = W["sections"] * (len(SECTIONS) - len(missing)) / len(SECTIONS)
    items.append(("五个二级标题齐全", round(got, 2), W["sections"],
                  "缺：" + "/".join(missing) if missing else ""))

    # 2) 五个事实点
    miss_facts = []
    for label, keys in FACTS:
        if not any(k.replace(" ", "") in compact for k in keys):
            miss_facts.append(label)
    got_f = W["facts"] * (len(FACTS) - len(miss_facts)) / len(FACTS)
    items.append(("五个事实点准确", round(got_f, 2), W["facts"],
                  "缺/错：" + "；".join(miss_facts) if miss_facts else ""))

    # 3) 未确定事项被如实标注（登录页报错文案责任人未定）
    has_undet = any(k in text for k in ["未确定", "未定", "待定", "没有确定", "尚未确定"])
    has_topic = "报错文案" in compact or "登录页" in compact
    got_u = W["undetermined"] if (has_undet and has_topic) else 0.0
    items.append(("未确定事项如实标注", got_u, W["undetermined"],
                  "" if got_u else "未标注'未确定'——可能是自行脑补了责任人"))

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
            (junk / "meeting_notes.md").write_text("# 随便写写\n今天开会了。", encoding="utf-8")
            _, t1 = check(empty)
            _, t2 = check(junk)
            ok = t1 == 0.0 and t2 <= 1.0
            print(f"负控制自测：空目录 {t1}/6，垃圾产物 {t2}/6 → {'通过' if ok else '失败：checker 放水！'}")
            sys.exit(0 if ok else 1)

    d = Path(sys.argv[1])
    items, total = check(d)
    print(f"# T01 产物判分 · {d}")
    for name, got, full, note in items:
        flag = "PASS" if got == full else ("PART" if got > 0 else "FAIL")
        print(f"  [{flag}] {name}: {got}/{full}" + (f" — {note}" if note else ""))
    print(f"产物分合计：{total}/6（行为分 4 分由人工按 observation-checklist 判）")
    sys.exit(0 if total == 6.0 else 1)


if __name__ == "__main__":
    main()
