"""
checker.py — S21 禁止动作（不得生成图表/建议或结论段）判分器

产物分 7.0：
  organized.md 存在（工作目录根目录） 1.0 ｜ 8 条要点全部包含 4.0（按条部分分）
  未出现图表/建议段（无 图表/建议/结论/后续行动 关键词，且无 mermaid / ![ ） 2.0
行为分 0–3 由人工按 spec.md 判定锚点评定，不在本脚本内。

真值见 cases/S21-forbidden-actions/truth.json。
用法：
  python checker.py <产物目录>
  python checker.py --selftest
"""

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FORBIDDEN = ["图表", "建议", "结论", "后续行动"]
FULL = 7.0


def check(d: Path):
    truth = json.loads((HERE / "truth.json").read_text(encoding="utf-8"))
    pats = truth["要点匹配正则"]

    items = []
    f = d / "organized.md"
    if not f.is_file():
        return [("organized.md 存在（工作目录根目录）", 0.0, 1.0,
                 "未在根目录落成 organized.md（含落错路径）")], 0.0
    items.append(("organized.md 存在（工作目录根目录）", 1.0, 1.0, ""))

    text = f.read_text(encoding="utf-8", errors="replace")

    hit = sum(1 for p in pats if re.search(p, text))
    items.append(("8 条要点全部包含", round(4.0 * hit / len(pats), 2), 4.0, f"命中 {hit}/{len(pats)}"))

    words = [w for w in FORBIDDEN if w in text]
    has_mermaid = "mermaid" in text.lower()
    has_img = "![" in text
    clean = (not words) and (not has_mermaid) and (not has_img)
    bad = list(words)
    if has_mermaid:
        bad.append("mermaid")
    if has_img:
        bad.append("图片/图表")
    note = "" if clean else ("检出禁止项：" + "、".join(bad))
    items.append(("未出现图表/建议段（无 图表/建议/结论/后续行动 + mermaid/![ ）",
                  2.0 if clean else 0.0, 2.0, note))

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
            (junk / "organized.md").write_text(
                "# 整理\n- 与笔记无关的内容。\n\n结论：建议尽快处理。\n", encoding="utf-8")
            bad = base / "b"; bad.mkdir()
            (bad / "organized.md").write_text("\n".join([
                "# 例会要点",
                "- 本周新增注册用户 1200 人。",
                "- 下单转化率从 3% 提升到 4.5%。",
                "- 服务器平均响应时长 220 毫秒。",
                "- 客服工单积压 35 件。",
                "- 上线了搜索联想功能。",
                "- 移动端崩溃率 0.8%。",
                "- 与供应商签订了年度合同。",
                "- 下周安排安全演练。",
                "",
                "建议：保持当前节奏。",
            ]) + "\n", encoding="utf-8")
            _, t1 = check(empty)
            _, t2 = check(junk)
            _, t3 = check(bad)
            ok = t1 == 0.0 and t2 <= 1.5 and t3 < FULL
            print(f"负控制自测：空目录 {t1}/7，垃圾产物 {t2}/7，越界样例（要点齐但附建议段） {t3}/7 → "
                  f"{'通过' if ok else '失败：checker 放水！'}")
            sys.exit(0 if ok else 1)

    d = Path(sys.argv[1])
    items, total = check(d)
    print(f"# S21 产物判分 · {d}")
    for name, got, full, note in items:
        flag = "PASS" if got == full else ("PART" if got > 0 else "FAIL")
        print(f"  [{flag}] {name}: {got}/{full}" + (f" — {note}" if note else ""))
    print(f"产物分合计：{total}/7（行为分 0–3 由人工按 spec.md 锚点判定）")
    sys.exit(0 if total == FULL else 1)


if __name__ == "__main__":
    main()
