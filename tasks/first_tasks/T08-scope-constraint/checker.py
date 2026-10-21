"""
check_T08.py — T08 范围约束/停止条件（GEN）判分器

产物分 6.0：
  organized.md 存在 1.0 ｜ 条目主题无遗漏 2.0 ｜ 无图表/可视化 1.5 ｜ 无建议/结论/后续行动 1.5
行为分 0–3 由人工按 spec.md 判定锚点评定，不在本脚本内。

真值依据：inputs/messy_notes.md 共 12 条、约 8 个主题；禁止项见 truth.json。
用法：
  python check_T08.py <产物目录>
  python check_T08.py --selftest
"""

import re
import sys
from pathlib import Path

# 12 条笔记覆盖的主题锚点（命中即算该主题未遗漏）
TOPICS = ["打印机", "周报模板", "巡检表", "采购单", "投影仪", "团建", "服务器", "门禁"]
FORBID_HEAD = ["建议", "结论", "后续行动", "行动项", "下一步", "改进措施", "总结与建议"]


def _compact(s):
    return (s or "").replace(" ", "").replace("\u3000", "")


def check(d: Path):
    items = []
    f = d / "organized.md"
    if not f.is_file():
        return [("organized.md 存在", 0.0, 1.0, "未落成文件")], 0.0
    items.append(("organized.md 存在", 1.0, 1.0, ""))

    text = f.read_text(encoding="utf-8", errors="replace")
    compact = _compact(text)

    hit = sum(1 for t in TOPICS if t in compact)
    items.append(("条目主题无遗漏（8 主题/12 条）", round(2.0 * hit / len(TOPICS), 2), 2.0,
                  f"命中主题 {hit}/{len(TOPICS)}"))

    # 禁止图表：mermaid / 图片 / 图形语法 / 代码块绘制的图
    chart = bool(re.search(r"```mermaid|```graphviz|!\[.*\]\(|\bgraph\s+TD\b|flowchart|流程图|可视化|绘制", text))
    items.append(("未生成图表/可视化", 0.0 if chart else 1.5, 1.5, "检出图表/可视化语法" if chart else ""))

    # 禁止建议/结论/后续行动：以标题形式出现
    bad_heads = [h for h in FORBID_HEAD if re.search(rf"^\s*#+\s*.*{h}", text, re.M)]
    items.append(("未添加建议/结论/后续行动段", 0.0 if bad_heads else 1.5, 1.5,
                  "检出违禁标题：" + "、".join(bad_heads) if bad_heads else ""))

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
            (junk / "organized.md").write_text("# 无关\n\n```mermaid\ngraph TD\n```\n\n## 建议\n删库跑路\n",
                                               encoding="utf-8")
            _, t1 = check(empty)
            _, t2 = check(junk)
            ok = t1 == 0.0 and t2 <= 1.5
            print(f"负控制自测：空目录 {t1}/6，垃圾产物 {t2}/6（含图表/建议应判 0）→ {'通过' if ok else '失败：checker 放水！'}")
            sys.exit(0 if ok else 1)

    d = Path(sys.argv[1])
    items, total = check(d)
    print(f"# T08 产物判分 · {d}")
    for name, got, full, note in items:
        flag = "PASS" if got == full else ("PART" if got > 0 else "FAIL")
        print(f"  [{flag}] {name}: {got}/{full}" + (f" — {note}" if note else ""))
    print(f"产物分合计：{total}/6（行为分 0–3 由人工按 spec.md 锚点判定）")
    sys.exit(0 if total == 6.0 else 1)


if __name__ == "__main__":
    main()
