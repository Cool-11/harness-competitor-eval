"""
check_S17.py — S17 多文件交叉汇总（跨文件检索 + 上下文管理）判分器

产物分 7.0：
  cross_ref.md 存在 0.5 ｜ 表头「供应商|合同数|总金额」1.0
  三家供应商的合同数与总金额全部正确 4.0（按供应商部分分）
  总计行含正确总额 1.0（K2：漏写总计或金额不符即扣，见 prompt 完成条件）
  无张冠李戴（金额未串行）0.5
行为分 0–3 由人工按 spec.md 判定锚点评定，不在本脚本内。

真值见 cases/S17-multifile-crossref/truth.json。
用法：
  python check_S17.py <产物目录>
  python check_S17.py --selftest
"""

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _compact(s):
    return re.sub(r"[\s\u3000]", "", s or "")


def check(d: Path):
    truth = json.loads((HERE / "truth.json").read_text(encoding="utf-8"))
    vendors = truth["供应商"]

    items = []
    f = d / "cross_ref.md"
    if not f.is_file():
        return [("cross_ref.md 存在", 0.0, 0.5, "未落成文件（含落错路径）")], 0.0
    items.append(("cross_ref.md 存在", 0.5, 0.5, ""))

    text = f.read_text(encoding="utf-8", errors="replace")
    compact = _compact(text)
    nocomma = re.sub(r"[,，]", "", text)   # 千分位归一：362,000 → 362000
    lines = nocomma.splitlines()

    head_ok = all(k in compact for k in ("供应商", "合同数", "总金额"))
    items.append(("表头「供应商|合同数|总金额」", 1.0 if head_ok else 0.0, 1.0,
                  "" if head_ok else "表头关键字不全"))

    # 按供应商计分：同一行内"合同数 + 总金额"都对 = 1.0，只对一项 = 0.5
    credit = 0.0
    detail = []
    for name, exp in vendors.items():
        cnt, tot = exp["合同数"], exp["总金额"]
        vlines = [ln for ln in lines if name in ln]
        best = 0.0
        for ln in vlines:
            c_ok = re.search(r"(?<!\d)" + str(cnt) + r"(?!\d)", ln) is not None
            a_ok = str(tot) in ln
            best = max(best, 0.5 * int(c_ok) + 0.5 * int(a_ok))
        credit += best
        detail.append(f"{name}={'满' if best == 1.0 else ('半' if best == 0.5 else '错')}")
    items.append(("三家合同数与总金额全部正确", round(4.0 * credit / len(vendors), 2), 4.0,
                  " ".join(detail)))

    # K2：prompt 要求"给出总计一行"；缺行或金额不符按完成条件扣 1.0
    total_val = str(truth["总计"])
    total_ok = any(("总计" in ln or "合计" in ln) and total_val in ln for ln in lines)
    items.append(("总计行含正确总额", 1.0 if total_ok else 0.0, 1.0,
                  "" if total_ok else f"未写总计行或总额≠{total_val}"))

    # 无张冠李戴：任一供应商行内出现的金额（≥5 位数字）必须恰为该供应商真值
    stray = []
    for name, exp in vendors.items():
        for ln in [ln for ln in lines if name in ln]:
            bad = [n for n in re.findall(r"\d{5,}", ln) if n != str(exp["总金额"])]
            if bad:
                stray.append(f"{name}:{bad}")
    items.append(("无张冠李戴（金额未串行）", 0.5 if not stray else 0.0, 0.5,
                  ("串行：" + "、".join(stray)) if stray else ""))

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
            (junk / "cross_ref.md").write_text("## 汇总\n甲 999999\n乙 999999\n", encoding="utf-8")
            near = Path(td) / "n"; near.mkdir()
            (near / "cross_ref.md").write_text(
                "| 供应商 | 合同数 | 总金额 |\n| 甲 | 3 | 362000 |\n"
                "| 乙 | 3 | 241000 |\n| 丙 | 2 | 121000 |\n", encoding="utf-8")
            _, t1 = check(empty)
            _, t2 = check(junk)
            _, t3 = check(near)
            ok = t1 == 0.0 and t2 <= 1.0 and t3 == 6.0
            print(f"负控制自测：空目录 {t1}/7，垃圾产物 {t2}/7 → {'通过' if ok else '失败：checker 放水！'}")
            print(f"近似违规自测：缺总计行 {t3}/7（应 6.0）→ {'通过' if t3 == 6.0 else '失败：K2 回归！'}")
            sys.exit(0 if ok else 1)

    d = Path(sys.argv[1])
    items, total = check(d)
    print(f"# S17 产物判分 · {d}")
    for name, got, full, note in items:
        flag = "PASS" if got == full else ("PART" if got > 0 else "FAIL")
        print(f"  [{flag}] {name}: {got}/{full}" + (f" — {note}" if note else ""))
    print(f"产物分合计：{total}/7（行为分 0–3 由人工按 spec.md 锚点判定）")
    sys.exit(0 if total == 7.0 else 1)


if __name__ == "__main__":
    main()
