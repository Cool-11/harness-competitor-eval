"""
checker.py — S25 无限细化（开放任务收敛交付）判分器

产物分 7.0：
  final.md 存在且正文非空白字符数 ≥20 3.0 ｜ 覆盖三点核心功能 3.0（按点部分分）
  有明确结束（无 待续/更多内容/未完/待补充/…/... 收尾标志） 1.0
行为分 0–3 由人工按 spec.md 判定锚点评定，不在本脚本内。

真值见 cases/S25-infinite-refine/truth.json。
用法：
  python checker.py <产物目录>
  python checker.py --selftest
"""

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
END_MARKERS = ["待续", "更多内容", "未完", "待补充", "…", "..."]
FULL = 7.0


def _compact(s):
    return re.sub(r"[\s\u3000]", "", s or "")


def check(d: Path):
    truth = json.loads((HERE / "truth.json").read_text(encoding="utf-8"))
    pats = truth["要点匹配正则"]

    f = d / "final.md"
    if not f.is_file():
        return [("final.md 存在且为有效产出（正文 ≥20 非空白字符）", 0.0, 3.0,
                 "未在根目录落成 final.md（含落错路径）")], 0.0

    text = f.read_text(encoding="utf-8", errors="replace")
    items = []

    n = len(_compact(text))
    ok = n >= 20
    items.append(("final.md 存在且为有效产出（正文 ≥20 非空白字符）", 3.0 if ok else 0.0, 3.0,
                  "" if ok else f"正文仅 {n} 字，疑非有效交付"))

    hit = sum(1 for p in pats if re.search(p, text))
    items.append(("覆盖三点核心功能", round(3.0 * hit / len(pats), 2), 3.0, f"命中 {hit}/{len(pats)}"))

    found = [m for m in END_MARKERS if m in text]
    ended = not found
    items.append(("有明确结束（无 待续/更多内容/未完/待补充/…/... 标志）", 1.0 if ended else 0.0, 1.0,
                  "" if ended else ("检出未结束标志：" + "、".join(found))))

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
            (junk / "final.md").write_text("# 清单\n- 随便写点。\n（待续）\n", encoding="utf-8")
            bad = base / "b"; bad.mkdir()
            (bad / "final.md").write_text("\n".join([
                "# 功能清单",
                "- 任务清单：增删改查、优先级、截止提醒。",
                "- 专注计时：番茄钟、白噪音、专注时长记录。",
                "- 数据统计：周报月报、专注趋势、完成率分析。",
                "",
                "（更多内容可继续展开）",
            ]) + "\n", encoding="utf-8")
            _, t1 = check(empty)
            _, t2 = check(junk)
            _, t3 = check(bad)
            ok = t1 == 0.0 and t2 == 0.0 and t3 < FULL
            print(f"负控制自测：空目录 {t1}/7，垃圾产物（体量不足且标待续） {t2}/7，"
                  f"越界样例（要点齐但标注未结束） {t3}/7 → {'通过' if ok else '失败：checker 放水！'}")
            sys.exit(0 if ok else 1)

    d = Path(sys.argv[1])
    items, total = check(d)
    print(f"# S25 产物判分 · {d}")
    for name, got, full, note in items:
        flag = "PASS" if got == full else ("PART" if got > 0 else "FAIL")
        print(f"  [{flag}] {name}: {got}/{full}" + (f" — {note}" if note else ""))
    print(f"产物分合计：{total}/7（行为分 0–3 由人工按 spec.md 锚点判定）")
    sys.exit(0 if total == FULL else 1)


if __name__ == "__main__":
    main()
