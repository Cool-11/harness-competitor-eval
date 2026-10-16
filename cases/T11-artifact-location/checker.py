"""
check_T11.py — T11 产物落点四重约束（MOD）判分器

产物分 7.0：
  output/final_v2.md 存在（路径正确）2.0 ｜ 首行一级标题文字正确 1.5
  无残留 (待补充) 1.0 ｜ 无残留 TODO 1.0 ｜ 原文实质内容保留 1.5
行为分 0–3 由人工按 spec.md 判定锚点评定，不在本脚本内。

依据：cases/T11-artifact-location/task.md 四项落点要求 + inputs/draft.md。
用法：
  python check_T11.py <产物目录>
  python check_T11.py --selftest
"""

import sys
from pathlib import Path

TITLE = "# 项目立项说明"
KEEP_ANCHORS = ["降低单次巡检耗时", "提高记录完整率", "分三个阶段", "## 目标", "## 范围", "## 计划"]


def check(d: Path):
    items = []
    target = d / "output" / "final_v2.md"
    misplaced = d / "final_v2.md"

    if not target.is_file():
        note = "未落在 output/ 子目录"
        if misplaced.is_file():
            note = "产物误落在工作目录根目录（应为 output/final_v2.md）"
        items.append(("产物落点 output/final_v2.md", 0.0, 2.0, note))
        items.append(("首行一级标题文字正确", 0.0, 1.5, ""))
        items.append(("无残留 (待补充)", 0.0, 1.0, ""))
        items.append(("无残留 TODO", 0.0, 1.0, ""))
        items.append(("原文实质内容保留", 0.0, 1.5, ""))
        return items, 0.0

    items.append(("产物落点 output/final_v2.md", 2.0, 2.0, ""))

    text = target.read_text(encoding="utf-8", errors="replace")
    lines = [l for l in text.splitlines()]
    first = next((l.strip() for l in lines if l.strip()), "")
    title_ok = first.replace(" ", "") == TITLE.replace(" ", "")
    items.append(("首行一级标题文字正确", 1.5 if title_ok else 0.0, 1.5,
                  "" if title_ok else f"首行实为「{first}」"))

    items.append(("无残留 (待补充)", 0.0 if "(待补充)" in text else 1.0, 1.0,
                  "仍有未替换的 (待补充)" if "(待补充)" in text else ""))
    items.append(("无残留 TODO", 0.0 if "TODO" in text else 1.0, 1.0,
                  "仍有未删除的 TODO" if "TODO" in text else ""))

    compact = text.replace(" ", "")
    hit = sum(1 for a in KEEP_ANCHORS if a.replace(" ", "") in compact)
    items.append(("原文实质内容保留", round(1.5 * hit / len(KEEP_ANCHORS), 2), 1.5,
                  f"命中 {hit}/{len(KEEP_ANCHORS)}"))

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
            (junk / "final_v2.md").write_text("随便写\n(待补充) TODO\n", encoding="utf-8")
            _, t1 = check(empty)
            _, t2 = check(junk)
            ok = t1 == 0.0 and t2 == 0.0   # 落点错 → 0 分
            print(f"负控制自测：空目录 {t1}/7，落点错误的垃圾产物 {t2}/7 → {'通过' if ok else '失败：checker 放水！'}")
            sys.exit(0 if ok else 1)

    d = Path(sys.argv[1])
    items, total = check(d)
    print(f"# T11 产物判分 · {d}")
    for name, got, full, note in items:
        flag = "PASS" if got == full else ("PART" if got > 0 else "FAIL")
        print(f"  [{flag}] {name}: {got}/{full}" + (f" — {note}" if note else ""))
    print(f"产物分合计：{total}/7（行为分 0–3 由人工按 spec.md 锚点判定）")
    sys.exit(0 if total == 7.0 else 1)


if __name__ == "__main__":
    main()
